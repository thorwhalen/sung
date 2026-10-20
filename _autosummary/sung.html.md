# sung

Tools to get music metadata (from Spotify, Wikipedia, etc.)

```pycon
>>> from sung.base import Tracks, Playlist  # Import necessary classes
>>> from sung import delete_playlist  # Import delete function for playlists
```

Search for tracks with the query ‘Love’, limiting the results to 7

```pycon
>>> tracks = Tracks.search(query='Love', limit=7)
```

You can also make a `tracks` object by passing a list of track IDs or urls

```pycon
>>> track_ids = [
...     '1vrd6UOGamcKNGnSHJQlSt',
...     '3CeCwYWvdfXbZLXFhBrbnf',
...     '1dGr1c8CrMLDpV6mPbImSI',
...     '0u2P5u6lvoDfwTYjAADbn4',
...     '6nGeLlakfzlBcFdZXteDq7',
...     '6dBUzqjtbnIa1TwYbyw5CM',
...     '7hR22TOX3RorxJPcsz5Wbo'
... ]
>>> tracks = Tracks(track_ids)
```

`tracks` is a `Mapping` (that means “dict-like”), so you can do what you do with dicts…

Like listing the track keys (IDs)

```pycon
>>> list(tracks)
['1vrd6UOGamcKNGnSHJQlSt',
 '3CeCwYWvdfXbZLXFhBrbnf',
 ...,
 '6dBUzqjtbnIa1TwYbyw5CM',
 '7hR22TOX3RorxJPcsz5Wbo']
```

Like accessing the value of a track for a given key.
The value is a bunch of metadata about the track.

```pycon
>>> track_metadata = tracks['1dGr1c8CrMLDpV6mPbImSI']  # get metadata of track via it's id
>>> assert isinstance(track_metadata, dict)
>>> sorted(track_metadata)
['album',
 'artists',
 'available_markets',
 'disc_number',
 'duration_ms',
 'explicit',
 'external_ids',
 'external_urls',
 'href',
 'id',
 'is_local',
 'name',
 'popularity',
 'preview_url',
 'track_number',
 'type',
 'uri']
```

```pycon
>>> df = tracks.data
                                                    name  duration_ms  popularity  ...  track_number   type                                   uri
    id                                                                              ...
    1vrd6UOGamcKNGnSHJQlSt                     Love Story       235266          62  ...             3  track  spotify:track:1vrd6UOGamcKNGnSHJQlSt
    3CeCwYWvdfXbZLXFhBrbnf  Love Story (Taylor’s Version)       235766          76  ...
    ...
    6dBUzqjtbnIa1TwYbyw5CM                    Lovers Rock       213920          85  ...             9  track  spotify:track:6dBUzqjtbnIa1TwYbyw5CM
    7hR22TOX3RorxJPcsz5Wbo                  Love Somebody       204828          86  ...             1  track  spotify:track:7hR22TOX3RorxJPcsz5Wbo
```

Create a new playlist named ‘my_test_playlist’ with the selected tracks

```pycon
>>> playlist = Playlist.create_from_track_list(
...     track_list=list(tracks),
...     playlist_name='my_test_playlist'
... )
```

Get the playlist URL of the newly created playlist (so you can check it out on Spotify)

```pycon
>>> playlist.playlist_url
'https://open.spotify.com/playlist/...'
```

Delete the playlist.

We purposely tried to make deleting a playlist not as easy as the other actions.
So we didn’t attach a delete method to the playlist instance, but put this in a
separate function you have to import.
Also, we made that function verbose, and asking for confirmation by default.
(But there’s arguments to control that, so you can use `functools.partial` to
make your own cowboy (not speaking and not asking for permission) version).

```pycon
>>> delete_playlist(playlist.playlist_id, ask_confirmation=False)
Playlist ... has been deleted (unfollowed).
```

Instantiate a Playlist object using the URL (let’s just use the one we just created!)

```pycon
>>> top50_global_url = 'https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF?si=d6e0c7bc8f59473b'
>>> playlist_obj = Playlist(top50_global_url)
>>> df = playlist_obj.data
>>> df['first_artist'] = df['artists'].apply(lambda x: x[0]['name'])
>>> df['name_and_first_artist'] = df['name'] + ' - ' + df['first_artist']
>>> top_5_tracks = playlist_obj.data.iloc[:5].name_and_first_artist
>>> top_5_tracks
id
2plbrEY59IikOBgBGLjaoe          Die With A Smile - Lady Gaga
5vNRhkKd0yEAg8suGBpjeY                           APT. - ROSÉ
6dOtVTDdiauQNBQEDOtlAB    BIRDS OF A FEATHER - Billie Eilish
7ne4VBA60CxGM75vw0EYad        That’s So True - Gracie Abrams
7tI8dRuH2Yc6RuoTjxo4dU                           Who - Jimin
Name: name_and_first_artist, dtype: object
```

### Functions

| [`search_tracks`](#sung.search_tracks)(query[, egress, search_type, ...])   | Search for tracks on Spotify.                                                                    |
|-----------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| [`extract_extra_metadata`](#sung.extract_extra_metadata)(target, \*[, spec])         | Access or construct a value from a given *target* based on the specification declared by *spec*. |
| `df_extract_extra_metadata`(df)                                                                     |                                                                                                  |
| `delete_playlist`(playlist_id[, verbose, ...])                                                      |                                                                                                  |
| `extractor`(spec)                                                                                   |                                                                                                  |
| [`cast_track_key`](#sung.cast_track_key)(track_key[, target_kind, ...])      | Convert a Spotify track key between different formats.                                           |
| [`ensure_track_id`](#sung.ensure_track_id)(track_key, \*[, target_kind, ...]) | Convert a Spotify track key between different formats.                                           |
| [`get_spotify_client`](#sung.get_spotify_client)([client, ensure_scope, ...])    | Get a Spotify client.                                                                            |
| [`ensure_playlist_id`](#sung.ensure_playlist_id)(playlist_spec)                  | Ensure that a playlist ID is in the correct format.                                              |
| [`render_chords_and_lyrics`](#sung.render_chords_and_lyrics)(song[, to, ...])          | Aggregator: render to 'pdf' or 'text'.                                                           |
| [`search_songs`](#sung.search_songs)([title, lyrics, artist, data])        | Search for a song by title, lyrics, or artist.                                                   |
| [`remove_non_lyrics`](#sung.remove_non_lyrics)(song[, keep_metadata])           | Convenience function to filter non-lyrics and return as text.                                    |
| [`pack_song_text`](#sung.pack_song_text)(song[, max_length])                 | Convenience function to pack lines and return as text.                                           |
| [`parse_song_descriptor`](#sung.parse_song_descriptor)(descriptor)                  | Parse a song descriptor into `(name, artist_or_None)`.                                           |
| [`resolve_song`](#sung.resolve_song)(descriptor, \*[, market, ...])        | Resolve one song descriptor to a Spotify track via search + ranking.                             |
| [`resolve_songs`](#sung.resolve_songs)(descriptors, \*[, market, ...])      | Resolve a list of descriptors.                                                                   |
| [`playlist_from_songs`](#sung.playlist_from_songs)(descriptors[, ...])            | Search for each song, then create a playlist with the resolved tracks.                           |

### Classes

| [`Tracks`](#sung.Tracks)(tracks, \*[, client])                  | A collection of Spotify tracks represented by track IDs or track metadata.   |
|------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| [`PlaylistReader`](#sung.PlaylistReader)(playlist_id, \*[, client])     | Read-only access to a Spotify playlist.                                      |
| [`Playlist`](#sung.Playlist)(playlist_id, \*[, client])           | A Spotify playlist with mutable mapping interface.                           |
| `SpotifyDacc`([client])                                                                        |                                                                              |
| `TracksAnalysis`(playlist)                                                                     |                                                                              |
| [`SongMatch`](#sung.SongMatch)(descriptor, query_name, ...[, ...]) | Result of resolving a single song descriptor.                                |

### *class* sung.Playlist(playlist_id, , client=None)

Bases: [`PlaylistReader`](sung.base.html.md#sung.base.PlaylistReader), [`MutableMapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]]

A Spotify playlist with mutable mapping interface.

#### *classmethod* create_from_track_list(track_list=(), playlist_name='New Playlist', public=True, , client=None, user_id=None)

Create a new playlist from a list of track IDs.

* **Parameters:**
  * **track_list** ([`Sequence`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]) – A list of track IDs to add to the playlist.
  * **playlist_name** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The name of the new playlist.
  * **public** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – Whether the playlist should be public.
  * **client** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – The Spotify client to use for creating the playlist.
  * **user_id** – The user ID of the playlist owner.
* **Return type:**
  [`Playlist`](sung.base.html.md#sung.base.Playlist)

### *class* sung.PlaylistReader(playlist_id, , client=None)

Bases: [`Tracks`](sung.base.html.md#sung.base.Tracks), [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]]

Read-only access to a Spotify playlist.

### *class* sung.SongMatch(descriptor, query_name, query_artist, track_id, track_name, artist_names=list(), album_name=None, popularity=None, score=0.0, candidates=list(), ambiguous=False, not_found=False)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Result of resolving a single song descriptor.

### *class* sung.Tracks(tracks, , client=None)

Bases: [`TracksBase`](sung.base.html.md#sung.base.TracksBase)

A collection of Spotify tracks represented by track IDs or track metadata.

### sung.cast_track_key(track_key, target_kind='uri', , src_kind=None)

Convert a Spotify track key between different formats.

* **Parameters:**
  * **convert** ( *- track_key - the track key to*)
  * **to** ( *- target_kind - the format to convert*)
  * **key** ( *- src_kind - the format* *of* *the input track*)
* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
* **Returns:**
  The track key in the target format.

### Examples

```pycon
>>> cast_track_key("4iV5W9uYEdYUVa79Axb7Rh")
'spotify:track:4iV5W9uYEdYUVa79Axb7Rh'
>>> cast_track_key("spotify:track:4iV5W9uYEdYUVa79Axb7Rh", target_kind="id")
'4iV5W9uYEdYUVa79Axb7Rh'
>>> cast_track_key("4iV5W9uYEdYUVa79Axb7Rh", "url")
'https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh'
>>> cast_track_key('https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh', "href")
'https://api.spotify.com/v1/tracks/4iV5W9uYEdYUVa79Axb7Rh'
>>> cast_track_key("4iV5W9uYEdYUVa79Axb7Rh", "uri")
'spotify:track:4iV5W9uYEdYUVa79Axb7Rh'
```

### sung.ensure_playlist_id(playlist_spec)

Ensure that a playlist ID is in the correct format.

* **Parameters:**
  * **id** ( *- playlist_spec - a playlist*)
  * **uri**
  * **href** (*url or*)
* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
* **Returns:**
  The playlist ID. Query strings (e.g. `?si=...`) are dropped; a string
  matching no known format is returned as is (assumed to be an id).

### Examples

```pycon
>>> ensure_playlist_id("37i9dQZF1DXcBWIGoYBM5M")
'37i9dQZF1DXcBWIGoYBM5M'
>>> ensure_playlist_id("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M")
'37i9dQZF1DXcBWIGoYBM5M'
>>> ensure_playlist_id("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
'37i9dQZF1DXcBWIGoYBM5M'
>>> ensure_playlist_id("https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M")
'37i9dQZF1DXcBWIGoYBM5M'
>>> ensure_playlist_id("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=abc")
'37i9dQZF1DXcBWIGoYBM5M'
```

### sung.ensure_track_id(track_key, , target_kind='id', src_kind=None)

Convert a Spotify track key between different formats.

* **Parameters:**
  * **convert** ( *- track_key - the track key to*)
  * **to** ( *- target_kind - the format to convert*)
  * **key** ( *- src_kind - the format* *of* *the input track*)
* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
* **Returns:**
  The track key in the target format.

### Examples

```pycon
>>> cast_track_key("4iV5W9uYEdYUVa79Axb7Rh")
'spotify:track:4iV5W9uYEdYUVa79Axb7Rh'
>>> cast_track_key("spotify:track:4iV5W9uYEdYUVa79Axb7Rh", target_kind="id")
'4iV5W9uYEdYUVa79Axb7Rh'
>>> cast_track_key("4iV5W9uYEdYUVa79Axb7Rh", "url")
'https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh'
>>> cast_track_key('https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh', "href")
'https://api.spotify.com/v1/tracks/4iV5W9uYEdYUVa79Axb7Rh'
>>> cast_track_key("4iV5W9uYEdYUVa79Axb7Rh", "uri")
'spotify:track:4iV5W9uYEdYUVa79Axb7Rh'
```

### sung.extract_extra_metadata(target, , spec={'album_images': Coalesce('album.images', default=None), 'album_name': Coalesce('album.name', default=None), 'album_release_date': Coalesce('album.release_date', default=None), 'album_total_tracks': Coalesce('album.total_tracks', default=None), 'artist_list': Coalesce('artists.\*.name', default=None), 'first_artist': Coalesce('artists.0.name', default=None), 'url': Coalesce('external_urls.spotify', default=None)}, \*\*kwargs)

Access or construct a value from a given *target* based on the
specification declared by *spec*.

Accessing nested data, aka deep-get:

```pycon
>>> target = {'a': {'b': 'c'}}
>>> glom(target, 'a.b')
'c'
```

Here the *spec* was just a string denoting a path,
`'a.b'`. As simple as it should be. You can also use
[`glob`](https://docs.python.org/3/library/glob.html#module-glob)-like wildcard selectors:

```pycon
>>> target = {'a': [{'k': 'v1'}, {'k': 'v2'}]}
>>> glom(target, 'a.*.k')
['v1', 'v2']
```

In addition to `*`, you can also use `**` for recursive access:

```pycon
>>> target = {'a': [{'k': 'v3'}, {'k': 'v4'}], 'k': 'v0'}
>>> glom(target, '**.k')
['v0', 'v3', 'v4']
```

The next example shows how to use nested data to
access many fields at once, and make a new nested structure.

Constructing, or restructuring more-complicated nested data:

```pycon
>>> target = {'a': {'b': 'c', 'd': 'e'}, 'f': 'g', 'h': [0, 1, 2]}
>>> spec = {'a': 'a.b', 'd': 'a.d', 'h': ('h', [lambda x: x * 2])}
>>> output = glom(target, spec)
>>> pprint(output)
{'a': 'c', 'd': 'e', 'h': [0, 2, 4]}
```

`glom` also takes a keyword-argument, *default*. When set,
if a `glom` operation fails with a `GlomError`, the
*default* will be returned, very much like
[`dict.get()`](https://docs.python.org/3/builtins/stdtypes.html#dict.get):

```pycon
>>> glom(target, 'a.xx', default='nada')
'nada'
```

The *skip_exc* keyword argument controls which errors should
be ignored.

```pycon
>>> glom({}, lambda x: 100.0 / len(x), default=0.0, skip_exc=ZeroDivisionError)
0.0
```

* **Parameters:**
  * **target** ([*object*](https://docs.python.org/3/builtins/functions.html#object)) – the object on which the glom will operate.
  * **spec** ([*object*](https://docs.python.org/3/builtins/functions.html#object)) – Specification of the output object in the form
    of a dict, list, tuple, string, other glom construct, or
    any composition of these.
  * **default** ([*object*](https://docs.python.org/3/builtins/functions.html#object)) – An optional default to return in the case
    an exception, specified by *skip_exc*, is raised.
  * **skip_exc** ([*Exception*](https://docs.python.org/3/builtins/exceptions.html#Exception)) – An optional exception or tuple of
    exceptions to ignore and return *default* (None if
    omitted). If *skip_exc* and *default* are both not set,
    glom raises errors through.
  * **scope** ([*dict*](https://docs.python.org/3/builtins/stdtypes.html#dict)) – Additional data that can be accessed
    via S inside the glom-spec. Read more: scope.

It’s a small API with big functionality, and glom’s power is
only surpassed by its intuitiveness. Give it a whirl!

### sung.get_spotify_client(client=None, , ensure_scope='', scope='', auth=None, requests_session=True, client_credentials_manager=None, oauth_manager=None, auth_manager=None, proxies=None, requests_timeout=5, status_forcelist=None, retries=3, status_retries=3, backoff_factor=0.3, language=None, client_id=None, client_secret=None, redirect_uri=None, state=None, cache_path=None, username=None, show_dialog=False, open_browser=True, cache_handler=None)

Get a Spotify client.

* **Parameters:**
  * **client** ( *- \*\*kwargs - additional arguments to pass to the Spotify*)
  * **auth_manager**
  * **client**
  * **client**

The purpose of having scope and ensure_scope is to allow you to ensure some needed
scopes exist when a code block is asking for a Spotify client with it’s own
scope desires.

### sung.pack_song_text(song, max_length=80)

Convenience function to pack lines and return as text.

* **Parameters:**
  * **song** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)]) – Raw text or parsed song data
  * **max_length** ([`int`](https://docs.python.org/3/builtins/functions.html#int)) – Maximum length for packed lines
* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
* **Returns:**
  Packed song as text

### sung.parse_song_descriptor(descriptor)

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

### sung.playlist_from_songs(descriptors, playlist_name='New Playlist', , public=True, market=None, search_limit=10, skip_missing=True, client=None)

Search for each song, then create a playlist with the resolved tracks.

Returns `(playlist, matches)`. `playlist` is `None` if no songs
resolved. `matches` is the list of [`SongMatch`](#sung.SongMatch) results — one
per descriptor — including any that were `not_found` or `ambiguous`.

Use `skip_missing=False` to raise instead of silently dropping
descriptors that could not be resolved.

* **Return type:**
  [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)[[`Playlist`](sung.base.html.md#sung.base.Playlist)], [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`SongMatch`](sung.playlists.html.md#sung.playlists.SongMatch)]]

### sung.remove_non_lyrics(song, keep_metadata=False)

Convenience function to filter non-lyrics and return as text.

* **Parameters:**
  * **song** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)]) – Raw text or parsed song data
  * **keep_metadata** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, keep metadata lines (like [Verse])
* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
* **Returns:**
  Filtered song as text

### sung.render_chords_and_lyrics(song, to='pdf', output_path=None, apply_filter_non_lyrics=False, keep_metadata_lines=False, pack_lines=False, max_line_length=80, \*\*kwargs)

Aggregator: render to ‘pdf’ or ‘text’.

- to=’pdf’: writes file to output_path (required).
- to=’text’: returns reconstructed text.

* **Parameters:**
  * **song** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)]) – Raw text or parsed song data
  * **to** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Output format (‘pdf’ or ‘text’)
  * **output_path** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Path for PDF output (required for PDF)
  * **apply_filter_non_lyrics** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, filter out non-lyrics content
  * **keep_metadata_lines** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, keep metadata lines (like [Verse]) when filtering
  * **pack_lines** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, pack short lines together for better space usage
  * **max_line_length** ([`int`](https://docs.python.org/3/builtins/functions.html#int)) – Maximum length for packed lines
  * **\*\*kwargs** – Additional arguments passed to rendering functions
* **Return type:**
  [`None`](https://docs.python.org/3/builtins/constants.html#None) | [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### sung.resolve_song(descriptor, , market=None, search_limit=10, ambiguous_score_gap=10.0, client=None)

Resolve one song descriptor to a Spotify track via search + ranking.

Returns a [`SongMatch`](#sung.SongMatch) with the best candidate selected. The match
is flagged `ambiguous` when the top two candidates score within
`ambiguous_score_gap` of each other (callers may want to confirm).

* **Return type:**
  [`SongMatch`](sung.playlists.html.md#sung.playlists.SongMatch)

### sung.resolve_songs(descriptors, , market=None, search_limit=10, client=None)

Resolve a list of descriptors. See [`resolve_song()`](#sung.resolve_song).

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`SongMatch`](sung.playlists.html.md#sung.playlists.SongMatch)]

### sung.search_songs(title='', , lyrics='', artist='', data=None)

Search for a song by title, lyrics, or artist.

### sung.search_tracks(query, egress=functools.partial(<function glom>, spec='tracks.items', default=None), \*, search_type='track', market=None, year=None, genre=None, limit=20, offset=0, client=<function get_spotify_client>)

Search for tracks on Spotify.

* **Parameters:**
  * **the** ( *- query - the search query* *(**see how to write a query in*) – official documentation)
  * **return.** ( *- offset - the index* *of* *the first item to*)
  * **'from_token'.** ( *- market - An ISO 3166-1 alpha-2 country code* *or* *the string*)
  * **return.**
  * **return.**

### Modules

| [`base`](sung.base.html.md#module-sung.base)                           | Base functionalities for the sung package.                                         |
|--------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| [`chords_and_lyrics`](sung.chords_and_lyrics.html.md#module-sung.chords_and_lyrics) | Tools for chords and lyrics acquisition and processing.                            |
| [`playlists`](sung.playlists.html.md#module-sung.playlists)                 | Build Spotify playlists from human-friendly song descriptors.                      |
| [`pydantic_models`](sung.pydantic_models.html.md#module-sung.pydantic_models)     | Pydantic models generated by datamodel-codegen using the Spotify API OpenAPI spec. |
| [`tools`](sung.tools.html.md#module-sung.tools)                         | Tools using sung                                                                   |
| [`util`](sung.util.html.md#module-sung.util)                           | Utility functions for the sung package.                                            |
