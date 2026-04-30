"""Build Spotify playlists from human-friendly song descriptors.

Given a list of "song descriptors" — things like ``"Clocks"``,
``"Clocks - Coldplay"``, ``("Believer", "Imagine Dragons")``, or
``{"name": "Fix You", "artist": "Coldplay"}`` — resolve each to a Spotify
track and create a playlist in one call.

Example::

    >>> from sung.playlists import playlist_from_songs
    >>> playlist, report = playlist_from_songs(  # doctest: +SKIP
    ...     [
    ...         ("Clocks", "Coldplay"),
    ...         "Radioactive - Imagine Dragons",
    ...         {"name": "Believer", "artist": "Imagine Dragons"},
    ...     ],
    ...     playlist_name="My Mix",
    ... )
    >>> playlist.playlist_url  # doctest: +SKIP
    'https://open.spotify.com/playlist/...'

The lower-level :func:`resolve_song` returns the chosen match plus the full
ranked candidate list, which the CLI uses to surface ambiguous matches.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Union
from collections.abc import Iterable, Sequence

from sung.base import Playlist, search_tracks
from sung.util import get_spotify_client, ensure_client


SongDescriptor = Union[str, tuple, dict]


@dataclass
class SongMatch:
    """Result of resolving a single song descriptor."""

    descriptor: Any
    query_name: str
    query_artist: Optional[str]
    track_id: Optional[str]
    track_name: Optional[str]
    artist_names: list = field(default_factory=list)
    album_name: Optional[str] = None
    popularity: Optional[int] = None
    score: float = 0.0
    candidates: list = field(default_factory=list)
    ambiguous: bool = False
    not_found: bool = False

    @property
    def primary_artist(self) -> Optional[str]:
        return self.artist_names[0] if self.artist_names else None

    def summary(self) -> str:
        if self.not_found:
            return f"NOT FOUND: {self.descriptor!r}"
        flag = " (AMBIGUOUS)" if self.ambiguous else ""
        return (
            f"{self.track_name} — {', '.join(self.artist_names)} "
            f"[{self.album_name}] pop={self.popularity}{flag}"
        )


def parse_song_descriptor(descriptor: SongDescriptor) -> tuple[str, Optional[str]]:
    """Parse a song descriptor into ``(name, artist_or_None)``.

    Accepts:

    - a plain string: ``"Clocks"``
    - ``"Title - Artist"`` or ``"Title — Artist"`` or ``"Title by Artist"``
    - a 2-tuple/list ``(name, artist)``
    - a dict with ``name``/``title`` and optional ``artist``/``artists``

    >>> parse_song_descriptor("Clocks")
    ('Clocks', None)
    >>> parse_song_descriptor("Clocks - Coldplay")
    ('Clocks', 'Coldplay')
    >>> parse_song_descriptor("Clocks by Coldplay")
    ('Clocks', 'Coldplay')
    >>> parse_song_descriptor(("Believer", "Imagine Dragons"))
    ('Believer', 'Imagine Dragons')
    >>> parse_song_descriptor({"name": "Fix You", "artist": "Coldplay"})
    ('Fix You', 'Coldplay')
    """
    if isinstance(descriptor, dict):
        name = descriptor.get("name") or descriptor.get("title")
        if not name:
            raise ValueError(f"Song dict must have 'name' or 'title': {descriptor!r}")
        artist = descriptor.get("artist") or descriptor.get("artists")
        if isinstance(artist, (list, tuple)):
            artist = ", ".join(artist) if artist else None
        return name.strip(), (artist.strip() if artist else None)

    if isinstance(descriptor, (tuple, list)):
        if len(descriptor) == 1:
            return str(descriptor[0]).strip(), None
        if len(descriptor) >= 2:
            return str(descriptor[0]).strip(), str(descriptor[1]).strip()
        raise ValueError(f"Empty song tuple: {descriptor!r}")

    if isinstance(descriptor, str):
        text = descriptor.strip()
        # Try "Title - Artist", "Title — Artist", "Title – Artist", "Title by Artist"
        for sep in (" — ", " – ", " - ", " by "):
            if sep in text:
                left, right = text.split(sep, 1)
                return left.strip(), right.strip()
        return text, None

    raise TypeError(f"Unsupported song descriptor type: {type(descriptor).__name__}")


def _normalize(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.isalnum())


def _same_song(a: dict, b: dict) -> bool:
    """True when two candidates appear to be the same song by the same primary artist.

    Spotify search routinely returns the same recording on the original album,
    a compilation, a deluxe edition, and a live release. We don't want to flag
    those as ambiguous — the user gets the same song either way.
    """
    if _normalize(a.get("name", "")) != _normalize(b.get("name", "")):
        return False
    a_artists = {_normalize(x["name"]) for x in a.get("artists", [])}
    b_artists = {_normalize(x["name"]) for x in b.get("artists", [])}
    return bool(a_artists & b_artists)


def _score_candidate(
    candidate: dict, query_name: str, query_artist: Optional[str]
) -> float:
    """Score a candidate track against the query. Higher is better."""
    score = 0.0

    cand_name = candidate.get("name", "")
    cand_artists = [a["name"] for a in candidate.get("artists", [])]

    qn = _normalize(query_name)
    cn = _normalize(cand_name)

    # Title match: exact > prefix > substring
    if cn == qn:
        score += 100
    elif cn.startswith(qn) or qn.startswith(cn):
        score += 60
    elif qn in cn or cn in qn:
        score += 30

    # Artist match (only if user provided one)
    if query_artist:
        qa = _normalize(query_artist)
        artist_normed = [_normalize(a) for a in cand_artists]
        if any(a == qa for a in artist_normed):
            score += 80
        elif any(qa in a or a in qa for a in artist_normed):
            score += 40
        else:
            # User specified an artist but no candidate artist matched; penalize
            score -= 50

    # Light popularity tiebreaker (0..100 → 0..10)
    score += (candidate.get("popularity") or 0) / 10.0

    # Mildly prefer non-explicit-remix / non-live versions: penalize obvious
    # alternate-version markers if the user didn't ask for them.
    name_lower = cand_name.lower()
    if not query_artist or "remix" not in query_artist.lower():
        if "remix" in name_lower:
            score -= 5
    if "live" in name_lower and "live" not in query_name.lower():
        score -= 3
    if "karaoke" in name_lower or "tribute" in name_lower:
        score -= 30

    return score


def resolve_song(
    descriptor: SongDescriptor,
    *,
    market: Optional[str] = None,
    search_limit: int = 10,
    ambiguous_score_gap: float = 10.0,
    client: Any = None,
) -> SongMatch:
    """Resolve one song descriptor to a Spotify track via search + ranking.

    Returns a :class:`SongMatch` with the best candidate selected. The match
    is flagged ``ambiguous`` when the top two candidates score within
    ``ambiguous_score_gap`` of each other (callers may want to confirm).
    """
    name, artist = parse_song_descriptor(descriptor)

    # Use Spotify field-qualified search when we have an artist
    if artist:
        query = f'track:"{name}" artist:"{artist}"'
    else:
        query = f'track:"{name}"'

    candidates = search_tracks(
        query=query, market=market, limit=search_limit, client=client
    )

    # Fallback: if a qualified search returns nothing, try a plain query
    if not candidates:
        plain = f"{name} {artist}".strip() if artist else name
        candidates = search_tracks(
            query=plain, market=market, limit=search_limit, client=client
        )

    if not candidates:
        return SongMatch(
            descriptor=descriptor,
            query_name=name,
            query_artist=artist,
            track_id=None,
            track_name=None,
            not_found=True,
        )

    scored = sorted(
        ((c, _score_candidate(c, name, artist)) for c in candidates),
        key=lambda x: x[1],
        reverse=True,
    )
    best, best_score = scored[0]
    runner_up = scored[1][0] if len(scored) > 1 else None
    runner_up_score = scored[1][1] if len(scored) > 1 else float("-inf")
    ambiguous = (
        runner_up is not None
        and (best_score - runner_up_score) < ambiguous_score_gap
        and not _same_song(best, runner_up)
    )

    return SongMatch(
        descriptor=descriptor,
        query_name=name,
        query_artist=artist,
        track_id=best["id"],
        track_name=best["name"],
        artist_names=[a["name"] for a in best.get("artists", [])],
        album_name=best.get("album", {}).get("name"),
        popularity=best.get("popularity"),
        score=best_score,
        candidates=[
            {
                "id": c["id"],
                "name": c["name"],
                "artists": [a["name"] for a in c.get("artists", [])],
                "album": c.get("album", {}).get("name"),
                "popularity": c.get("popularity"),
                "score": s,
            }
            for c, s in scored
        ],
        ambiguous=ambiguous,
    )


def resolve_songs(
    descriptors: Iterable[SongDescriptor],
    *,
    market: Optional[str] = None,
    search_limit: int = 10,
    client: Any = None,
) -> list[SongMatch]:
    """Resolve a list of descriptors. See :func:`resolve_song`."""
    client = ensure_client(client)
    return [
        resolve_song(d, market=market, search_limit=search_limit, client=client)
        for d in descriptors
    ]


def playlist_from_songs(
    descriptors: Iterable[SongDescriptor],
    playlist_name: str = "New Playlist",
    *,
    public: bool = True,
    market: Optional[str] = None,
    search_limit: int = 10,
    skip_missing: bool = True,
    client: Any = None,
) -> tuple[Optional[Playlist], list[SongMatch]]:
    """Search for each song, then create a playlist with the resolved tracks.

    Returns ``(playlist, matches)``. ``playlist`` is ``None`` if no songs
    resolved. ``matches`` is the list of :class:`SongMatch` results — one
    per descriptor — including any that were ``not_found`` or ``ambiguous``.

    Use ``skip_missing=False`` to raise instead of silently dropping
    descriptors that could not be resolved.
    """
    descriptors = list(descriptors)
    matches = resolve_songs(
        descriptors, market=market, search_limit=search_limit, client=client
    )

    missing = [m for m in matches if m.not_found]
    if missing and not skip_missing:
        raise LookupError(
            "Could not resolve: " + "; ".join(repr(m.descriptor) for m in missing)
        )

    track_ids = [m.track_id for m in matches if m.track_id]
    if not track_ids:
        return None, matches

    # Re-use existing scope-aware client construction in Playlist.create_from_track_list
    playlist = Playlist.create_from_track_list(
        track_list=track_ids,
        playlist_name=playlist_name,
        public=public,
        client=client,
    )
    return playlist, matches


# --------------------------------------------------------------------------------------
# CLI
#
# Usage:
#   python -m sung.playlists SONGS_FILE --name "My Mix" [--private] [--market US]
#
# SONGS_FILE: a text/markdown file with one song per non-empty, non-comment line.
# Each line can be:
#   - "Title"
#   - "Title - Artist" / "Title — Artist" / "Title by Artist"
# Lines starting with "#" are treated as comments. Numbered list markers
# ("1.", "1)", "- ", "* ") and surrounding markdown bold/italic are stripped.

import re as _re

_LIST_PREFIX_RE = _re.compile(r"^\s*(?:[-*]|\d+[.)])\s+")
_MD_EMPHASIS_RE = _re.compile(r"\*+|_+")


def _parse_songs_file(text: str) -> list[str]:
    songs = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        line = _LIST_PREFIX_RE.sub("", line)
        line = _MD_EMPHASIS_RE.sub("", line).strip()
        if line:
            songs.append(line)
    return songs


def _cli(argv=None):
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        description="Create a Spotify playlist from a list of song names."
    )
    parser.add_argument(
        "songs_file",
        help="Path to a text/markdown file with one song per line "
        "(use '-' to read from stdin).",
    )
    parser.add_argument(
        "--name", "-n", default="New Playlist", help="Playlist name."
    )
    parser.add_argument(
        "--private", action="store_true", help="Create a private playlist."
    )
    parser.add_argument(
        "--market", default=None, help="ISO 3166-1 alpha-2 market code."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve songs and print matches, but do not create the playlist.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit the match report as JSON."
    )
    args = parser.parse_args(argv)

    if args.songs_file == "-":
        text = sys.stdin.read()
    else:
        with open(args.songs_file, "r", encoding="utf-8") as fh:
            text = fh.read()

    descriptors = _parse_songs_file(text)
    if not descriptors:
        parser.error("No songs found in input.")

    if args.dry_run:
        matches = resolve_songs(descriptors, market=args.market)
        playlist = None
    else:
        playlist, matches = playlist_from_songs(
            descriptors,
            playlist_name=args.name,
            public=not args.private,
            market=args.market,
        )

    if args.json:
        report = {
            "playlist_url": playlist.playlist_url if playlist else None,
            "playlist_id": playlist.playlist_id if playlist else None,
            "matches": [
                {
                    "descriptor": m.descriptor,
                    "query_name": m.query_name,
                    "query_artist": m.query_artist,
                    "track_id": m.track_id,
                    "track_name": m.track_name,
                    "artist_names": m.artist_names,
                    "album_name": m.album_name,
                    "popularity": m.popularity,
                    "ambiguous": m.ambiguous,
                    "not_found": m.not_found,
                }
                for m in matches
            ],
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    if playlist:
        print(f"Playlist created: {playlist.playlist_url}")
    else:
        print("No tracks resolved; no playlist created.")
    print()
    print(f"{'#':>3}  {'descriptor':<40}  resolved")
    print(f"{'-'*3}  {'-'*40}  {'-'*40}")
    for i, m in enumerate(matches, 1):
        desc = str(m.descriptor)[:40]
        print(f"{i:>3}  {desc:<40}  {m.summary()}")


if __name__ == "__main__":
    _cli()
