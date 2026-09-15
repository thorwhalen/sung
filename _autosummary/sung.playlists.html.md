# sung.playlists

Build Spotify playlists from human-friendly song descriptors.

Given a list of “song descriptors” — things like `"Clocks"`,
`"Clocks - Coldplay"`, `("Believer", "Imagine Dragons")`, or
`{"name": "Fix You", "artist": "Coldplay"}` — resolve each to a Spotify
track and create a playlist in one call.

Example:

```default
>>> from sung.playlists import playlist_from_songs
>>> playlist, report = playlist_from_songs(
...     [
...         ("Clocks", "Coldplay"),
...         "Radioactive - Imagine Dragons",
...         {"name": "Believer", "artist": "Imagine Dragons"},
...     ],
...     playlist_name="My Mix",
... )
>>> playlist.playlist_url
'https://open.spotify.com/playlist/...'
```

The lower-level [`resolve_song()`](#sung.playlists.resolve_song) returns the chosen match plus the full
ranked candidate list, which the CLI uses to surface ambiguous matches.

### Functions

| [`parse_song_descriptor`](#sung.playlists.parse_song_descriptor)(descriptor)             | Parse a song descriptor into `(name, artist_or_None)`.                 |
|------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| [`playlist_from_songs`](#sung.playlists.playlist_from_songs)(descriptors[, ...])       | Search for each song, then create a playlist with the resolved tracks. |
| [`resolve_song`](#sung.playlists.resolve_song)(descriptor, \*[, market, ...])   | Resolve one song descriptor to a Spotify track via search + ranking.   |
| [`resolve_songs`](#sung.playlists.resolve_songs)(descriptors, \*[, market, ...]) | Resolve a list of descriptors.                                         |

### Classes

| [`SongMatch`](#sung.playlists.SongMatch)(descriptor, query_name, ...[, ...])   | Result of resolving a single song descriptor.   |
|--------------------------------------------------------------------------------------------------|-------------------------------------------------|

### *class* sung.playlists.SongMatch(descriptor, query_name, query_artist, track_id, track_name, artist_names=<factory>, album_name=None, popularity=None, score=0.0, candidates=<factory>, ambiguous=False, not_found=False)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Result of resolving a single song descriptor.

### sung.playlists.parse_song_descriptor(descriptor)

Parse a song descriptor into `(name, artist_or_None)`.

Accepts:

- a plain string: `"Clocks"`
- `"Title - Artist"` or `"Title — Artist"` or `"Title by Artist"`
- a 2-tuple/list `(name, artist)`
- a dict with `name`/`title` and optional `artist`/`artists`

```pycon
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
```

* **Return type:**
  [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]

### sung.playlists.playlist_from_songs(descriptors, playlist_name='New Playlist', , public=True, market=None, search_limit=10, skip_missing=True, client=None)

Search for each song, then create a playlist with the resolved tracks.

Returns `(playlist, matches)`. `playlist` is `None` if no songs
resolved. `matches` is the list of [`SongMatch`](#sung.playlists.SongMatch) results — one
per descriptor — including any that were `not_found` or `ambiguous`.

Use `skip_missing=False` to raise instead of silently dropping
descriptors that could not be resolved.

* **Return type:**
  [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)[[`Playlist`](sung.base.html.md#sung.base.Playlist)], [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`SongMatch`](#sung.playlists.SongMatch)]]

### sung.playlists.resolve_song(descriptor, , market=None, search_limit=10, ambiguous_score_gap=10.0, client=None)

Resolve one song descriptor to a Spotify track via search + ranking.

Returns a [`SongMatch`](#sung.playlists.SongMatch) with the best candidate selected. The match
is flagged `ambiguous` when the top two candidates score within
`ambiguous_score_gap` of each other (callers may want to confirm).

* **Return type:**
  [`SongMatch`](#sung.playlists.SongMatch)

### sung.playlists.resolve_songs(descriptors, , market=None, search_limit=10, client=None)

Resolve a list of descriptors. See [`resolve_song()`](#sung.playlists.resolve_song).

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`SongMatch`](#sung.playlists.SongMatch)]
