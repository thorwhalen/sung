---
name: sung-playlist
description: Create a Spotify playlist from a list of song names using the sung package. Use when the user asks to make/build/create a Spotify playlist from a list of songs (with or without artist names), wants to bulk-import songs into Spotify, or pastes a song list and asks for a playlist. Triggers on "make a playlist", "create a Spotify playlist with these songs", "turn this list into a playlist".
---

# Build a Spotify playlist from a list of songs

The `sung` package (in this repo) ships a helper, `sung.playlists.playlist_from_songs`, that takes flexible "song descriptors" (just a title, or a title + artist), searches Spotify, picks the best match for each, and creates a playlist in one call. Prefer this over hand-rolling search + create code.

## Inputs accepted

Any of these forms work as a song descriptor:

- `"Clocks"` — title only
- `"Clocks - Coldplay"` / `"Clocks — Coldplay"` / `"Clocks by Coldplay"`
- `("Clocks", "Coldplay")` — 2-tuple
- `{"name": "Clocks", "artist": "Coldplay"}` — dict

When the user provides artists, **always include them** — the matcher heavily weights artist match and avoids picking covers / soundalikes.

## Auth requirements

Creating a playlist requires the OAuth scopes `playlist-modify-public playlist-modify-private`. `playlist_from_songs` arranges this internally via `Playlist.create_from_track_list`, but the user must have these env vars set (the package will OAuth-prompt the first time):

- `SPOTIFY_API_CLIENT_ID`
- `SPOTIFY_API_CLIENT_SECRET`
- `SPOTIPY_REDIRECT_URI` — must use `http://127.0.0.1:PORT/callback` (Spotify rejected `http://localhost` as "Insecure" starting April 2025)

If those are missing, ask the user to set them and point them at https://developer.spotify.com/documentation/web-api/tutorials/getting-started.

**OAuth troubleshooting:**
- "redirect_uri: Insecure" → user has `http://localhost...` set; tell them to switch to `http://127.0.0.1...` in both the env var **and** the dashboard's Redirect URIs.
- "redirect_uri: Not matching configuration" → the URI in the request doesn't match anything saved in the dashboard. Common causes: user added but didn't *save* the URI, trailing slash mismatch, port or path mismatch, wrong client_id.
- The local OAuth server listens on port 8000 by default; if blocked, run `lsof -i :8000` to find the holding process.

## Recommended path: Python helper

This is the preferred approach when you need to inspect or transform results in the same session.

```python
from sung import playlist_from_songs

songs = [
    ("Clocks", "Coldplay"),
    ("Fix You", "Coldplay"),
    ("Radioactive", "Imagine Dragons"),
    # ...
]

playlist, matches = playlist_from_songs(
    songs,
    playlist_name="Coldplay + Imagine Dragons",
    # public=True,           # default
    # market="US",           # optional ISO market code
    # search_limit=10,       # candidates to consider per song
    # skip_missing=True,     # drop unresolved instead of raising
)

print(playlist.playlist_url)
for m in matches:
    print(m.summary())                         # human-readable line
    if m.ambiguous:
        # Top two candidates were close in score — surface to user
        for c in m.candidates[:3]:
            print("  ", c["name"], "—", ", ".join(c["artists"]), c["popularity"])
```

`matches` is a `list[SongMatch]`. Each match exposes:

- `track_id`, `track_name`, `artist_names`, `album_name`, `popularity`
- `ambiguous: bool` — top two *different* songs scored within 10 points (worth showing alternatives). The flag explicitly does NOT fire when the close runner-up is the same song by the same artist on a different release (compilation, deluxe edition, etc.) — those are not real ambiguities.
- `not_found: bool` — search returned nothing (rare; usually a typo)
- `candidates: list[dict]` — full ranked candidate list with scores

After resolving, **always report any `ambiguous` or `not_found` entries to the user** so they can correct the playlist.

## CLI path

For one-shot usage from a song list file:

```bash
# songs.txt: one song per line; "Title - Artist" or just "Title".
# Comment lines (#), markdown bullets (-, *, 1.), and **bold** are tolerated.
python -m sung.playlists songs.txt --name "My Mix"

# Inspect matches without creating the playlist:
python -m sung.playlists songs.txt --dry-run

# JSON report (good for chaining):
python -m sung.playlists songs.txt --name "My Mix" --json

# Other flags:
#   --private           create a private playlist (default is public)
#   --market US         restrict to a Spotify market
```

You can also pipe stdin: `cat songs.txt | python -m sung.playlists - --name "My Mix"`.

## Choosing between Python and CLI

- The user pasted a list inline → write a Python script and run it. You can format the report nicely and flag ambiguities.
- The user has a file or wants to script it themselves → recommend `python -m sung.playlists`.

## Things to do, things to avoid

- **Do** include the artist when the user provided it — even casually. The matcher needs it to disambiguate.
- **Do** print the playlist URL prominently when done, plus a table of resolved tracks.
- **Do** flag ambiguous and not-found matches and offer to refine them.
- **Don't** worry about `client.audio_features` 403s — Spotify removed access for apps registered after Nov 2024. `Tracks.audio_features` now degrades to `{}` with a one-time warning, and `Tracks.data` / `Playlist.data` automatically fall back to metadata-only. Use `meta_dataframe()` if you want to skip the audio-features attempt entirely.
- **Don't** silently drop a song the user listed without telling them. `not_found` results must surface.
- **Don't** create a playlist before showing the resolved match list if the user wants to review first — use `resolve_songs(...)` and only call `playlist_from_songs` after confirmation.

## Underlying API

The helper is a thin layer over existing `sung` primitives:

- `sung.playlists.parse_song_descriptor(...)` — turn a descriptor into `(name, artist)`
- `sung.playlists.resolve_song(...)` / `resolve_songs(...)` — search + rank
- `sung.base.Playlist.create_from_track_list(...)` — actually creates the playlist
- `sung.delete_playlist(playlist_id, ask_confirmation=False)` — clean up if needed

If the user wants something the helper doesn't cover (reordering, deduping, mixing in tracks from a search), drop down to those primitives directly rather than extending the helper unnecessarily.
