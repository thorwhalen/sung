"""Tests for the credential-free half of :mod:`sung.playlists`.

Descriptor parsing, candidate scoring, duplicate-release detection and songs-
file parsing are all pure functions over plain dicts, so the matcher's ranking
rules can be pinned without a single Spotify request. The live search itself is
covered (and deselected when unavailable) in ``test_spotify_live.py``.
"""

import pytest

from sung.playlists import (
    SongMatch,
    _normalize,
    _parse_songs_file,
    _same_song,
    _score_candidate,
    parse_song_descriptor,
)


def candidate(name, artists, popularity=50):
    """Build a Spotify-shaped search result candidate."""
    return {
        "id": name.lower().replace(" ", "-"),
        "name": name,
        "artists": [{"name": artist} for artist in artists],
        "popularity": popularity,
    }


# ---------------------------------------------------------------------------
# Descriptor parsing


@pytest.mark.parametrize(
    "descriptor,expected",
    [
        ("Clocks", ("Clocks", None)),
        ("Clocks - Coldplay", ("Clocks", "Coldplay")),
        ("Clocks — Coldplay", ("Clocks", "Coldplay")),  # em dash
        ("Clocks – Coldplay", ("Clocks", "Coldplay")),  # en dash
        ("Clocks by Coldplay", ("Clocks", "Coldplay")),
        (("Believer", "Imagine Dragons"), ("Believer", "Imagine Dragons")),
        (["Solo"], ("Solo", None)),
        ({"name": "Fix You", "artist": "Coldplay"}, ("Fix You", "Coldplay")),
        ({"title": "Yellow", "artists": ["Coldplay"]}, ("Yellow", "Coldplay")),
        ({"name": "  Spaced  ", "artist": "  A  "}, ("Spaced", "A")),
    ],
)
def test_parse_song_descriptor(descriptor, expected):
    assert parse_song_descriptor(descriptor) == expected


def test_parse_song_descriptor_joins_multiple_artists():
    assert parse_song_descriptor({"name": "X", "artists": ["A", "B"]}) == ("X", "A, B")


def test_parse_song_descriptor_does_not_split_on_a_bare_hyphen():
    """Only a *spaced* separator splits, so hyphenated titles survive.

    "Jack-in-the-Box" must stay one title; splitting it would search for the
    artist "in-the-Box".
    """
    assert parse_song_descriptor("Jack-in-the-Box") == ("Jack-in-the-Box", None)


def test_parse_song_descriptor_rejects_bad_input():
    with pytest.raises(ValueError, match="must have 'name' or 'title'"):
        parse_song_descriptor({"artist": "Coldplay"})
    with pytest.raises(TypeError, match="Unsupported song descriptor type"):
        parse_song_descriptor(3.5)


# ---------------------------------------------------------------------------
# Normalization and duplicate detection


def test_normalize_strips_punctuation_case_and_space():
    assert _normalize("Don't Stop! (Live)") == "dontstoplive"


def test_same_song_ignores_release_packaging():
    """Same title + a shared artist means the same recording for our purposes.

    Spotify returns the same track on the album, a deluxe edition and a
    compilation; flagging those as ambiguous would ask the user to choose
    between identical answers.
    """
    assert _same_song(
        candidate("Clocks", ["Coldplay"]), candidate("CLOCKS", ["Coldplay"])
    )
    assert not _same_song(
        candidate("Clocks", ["Coldplay"]), candidate("Yellow", ["Coldplay"])
    )
    assert not _same_song(
        candidate("Clocks", ["Coldplay"]), candidate("Clocks", ["Other"])
    )


# ---------------------------------------------------------------------------
# Scoring


def test_exact_title_and_artist_outranks_everything_else():
    query = ("Clocks", "Coldplay")
    exact = _score_candidate(candidate("Clocks", ["Coldplay"]), *query)
    partial_title = _score_candidate(candidate("Clocks (Remix)", ["Coldplay"]), *query)
    wrong_artist = _score_candidate(candidate("Clocks", ["Somebody Else"]), *query)
    assert exact > partial_title
    assert exact > wrong_artist


def test_wrong_artist_is_penalized_when_an_artist_was_requested():
    """Naming an artist must mean something, or covers win on popularity."""
    right = _score_candidate(
        candidate("Clocks", ["Coldplay"], 10), "Clocks", "Coldplay"
    )
    wrong = _score_candidate(
        candidate("Clocks", ["Somebody Else"], 100), "Clocks", "Coldplay"
    )
    assert right > wrong


def test_karaoke_and_tribute_versions_are_pushed_down():
    query = ("Clocks", "Coldplay")
    real = _score_candidate(candidate("Clocks", ["Coldplay"]), *query)
    karaoke = _score_candidate(
        candidate("Clocks (Karaoke Version)", ["Party Tyme"], 100), *query
    )
    tribute = _score_candidate(
        candidate("Clocks (Tribute)", ["Tribute Band"], 100), *query
    )
    assert real > karaoke
    assert real > tribute


def test_popularity_only_breaks_ties():
    """Popularity contributes at most 10 -- less than any title/artist term.

    If popularity could outweigh a title match, a chart hit would beat the
    song the user actually named.
    """
    unpopular_exact = _score_candidate(
        candidate("Clocks", ["Coldplay"], 0), "Clocks", None
    )
    popular_partial = _score_candidate(
        candidate("Clocks Forever", ["Coldplay"], 100), "Clocks", None
    )
    assert unpopular_exact > popular_partial


def test_popularity_orders_otherwise_identical_candidates():
    query = ("Clocks", "Coldplay")
    high = _score_candidate(candidate("Clocks", ["Coldplay"], 90), *query)
    low = _score_candidate(candidate("Clocks", ["Coldplay"], 10), *query)
    assert high > low


def test_live_versions_are_mildly_penalized_unless_requested():
    plain = _score_candidate(candidate("Clocks", ["Coldplay"]), "Clocks", None)
    live = _score_candidate(candidate("Clocks - Live", ["Coldplay"]), "Clocks", None)
    live_requested = _score_candidate(
        candidate("Clocks - Live", ["Coldplay"]), "Clocks Live", None
    )
    assert plain > live
    assert live_requested > live


def test_score_candidate_tolerates_missing_popularity():
    assert isinstance(
        _score_candidate({"name": "Clocks", "artists": []}, "Clocks", None), float
    )


# ---------------------------------------------------------------------------
# SongMatch


def test_song_match_summary_reports_not_found():
    match = SongMatch(
        descriptor="Nope",
        query_name="Nope",
        query_artist=None,
        track_id=None,
        track_name=None,
        not_found=True,
    )
    assert match.summary().startswith("NOT FOUND")
    assert match.primary_artist is None


def test_song_match_summary_flags_ambiguity():
    match = SongMatch(
        descriptor="Clocks",
        query_name="Clocks",
        query_artist=None,
        track_id="abc",
        track_name="Clocks",
        artist_names=["Coldplay", "Guest"],
        album_name="A Rush of Blood",
        popularity=80,
        ambiguous=True,
    )
    summary = match.summary()
    assert "AMBIGUOUS" in summary
    assert "Coldplay" in summary
    assert match.primary_artist == "Coldplay"


# ---------------------------------------------------------------------------
# Songs-file parsing (the CLI's input format)


def test_parse_songs_file_strips_markdown_scaffolding():
    text = "\n".join(
        [
            "# my playlist",
            "",
            "1. Clocks - Coldplay",
            "2) **Yellow**",
            "- Believer by Imagine Dragons",
            "* _Radioactive_",
            "",
        ]
    )
    assert _parse_songs_file(text) == [
        "Clocks - Coldplay",
        "Yellow",
        "Believer by Imagine Dragons",
        "Radioactive",
    ]


def test_parse_songs_file_ignores_blank_and_comment_lines():
    assert _parse_songs_file("\n\n# nope\n   \nClocks\n") == ["Clocks"]
