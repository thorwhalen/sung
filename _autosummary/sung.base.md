# sung.base

Base functionalities for the sung package.

This module provides foundational tools and abstractions for interacting with Spotify’s
API. It includes classes and functions to search for tracks, manage playlists, and
handle Spotify track metadata. The utilities here are designed to integrate seamlessly
with Spotify’s API and streamline data extraction and manipulation.

Key Components:

- `search_tracks`: A function to perform searches on Spotify, supporting filters such
  as year, genre, and market.
- `TracksBase`: A base class for managing collections of Spotify tracks,
  providing a dictionary-like interface with additional utilities for metadata handling.
- `Tracks`: A concrete implementation of `TracksBase` that uses track IDs or track metadata.
- `PlaylistReader` and `Playlist`: Classes for managing Spotify playlists, offering
  read-only and mutable interfaces respectively.
- Utility functions and constants for managing Spotify clients and data extraction.

This module is foundational for building higher-level operations within the sung package.

### Functions

| `delete_playlist`(playlist_id[, verbose, ...])                                                    |                                                               |
|---------------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| `process_track_columns`(df)                                                                       |                                                               |
| [`search_tracks`](#sung.base.search_tracks)(query[, egress, search_type, ...]) | Search for tracks on Spotify.                                 |
| [`track_ids_to_metas`](#sung.base.track_ids_to_metas)(track_ids, client)            | Convert track IDs to track metadata using the Spotify client. |
| `track_metadata`(track_id, \*[, client])                                                          |                                                               |
| [`track_metas_to_track_ids`](#sung.base.track_metas_to_track_ids)(track_metas)            | Extract track IDs from track metadata.                        |

### Classes

| [`Playlist`](#sung.base.Playlist)(playlist_id, \*[, client])       | A Spotify playlist with mutable mapping interface.                         |
|--------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| [`PlaylistReader`](#sung.base.PlaylistReader)(playlist_id, \*[, client]) | Read-only access to a Spotify playlist.                                    |
| `SpotifyDacc`([client])                                                                    |                                                                            |
| [`Tracks`](#sung.base.Tracks)(tracks, \*[, client])              | A collection of Spotify tracks represented by track IDs or track metadata. |
| [`TracksBase`](#sung.base.TracksBase)(tracks, \*[, client])          | Base class representing a collection of Spotify tracks.                    |

### *class* sung.base.Playlist(playlist_id, , client=None)

Bases: [`PlaylistReader`](#sung.base.PlaylistReader), [`MutableMapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]]

A Spotify playlist with mutable mapping interface.

#### *classmethod* create_from_track_list(track_list=(), playlist_name='New Playlist', public=True, , client=None, user_id=None)

Create a new playlist from a list of track IDs.

* **Parameters:**
  * **track_list** ([`Sequence`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]) – A list of track IDs to add to the playlist.
  * **playlist_name** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The name of the new playlist.
  * **public** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – Whether the playlist should be public.
  * **client** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – The Spotify client to use for creating the playlist.
  * **user_id** ( *-*) – The user ID of the playlist owner.
* **Return type:**
  [`Playlist`](#sung.base.Playlist)

### *class* sung.base.PlaylistReader(playlist_id, , client=None)

Bases: [`Tracks`](#sung.base.Tracks), [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]]

Read-only access to a Spotify playlist.

### *class* sung.base.Tracks(tracks, , client=None)

Bases: [`TracksBase`](#sung.base.TracksBase)

A collection of Spotify tracks represented by track IDs or track metadata.

### *class* sung.base.TracksBase(tracks, , client=None)

Bases: [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]]

Base class representing a collection of Spotify tracks.

#### *property* audio_features

Track-level audio features keyed by track id.

Returns `{}` and emits a one-time warning if Spotify rejects the
request (403) — a known restriction for apps registered after the
Nov 2024 Web API deprecation. Callers should treat audio features as
best-effort and fall back to metadata-only paths when empty.

#### dataframe(key=slice(None, None, None), , front_columns=('name', 'artists_names', 'duration_ms', 'popularity', 'explicit', 'album_name', 'album_release_date', 'album_release_year', 'added_at_date', 'url', 'artist_list', 'first_artist', 'first_letter', 'id'), back_columns=('type', 'episode', 'track', 'album', 'disc_number', 'track_number', 'artists', 'preview_url', 'uri', 'href', 'available_markets', 'external_ids', 'external_urls'))

Get tracks metadata for given key(s), as a pandas DataFrame.

By default, will return all tracks in the collection.

* **Return type:**
  `DataFrame`

#### meta_dataframe(key=slice(None, None, None), , front_columns=('name', 'artists_names', 'duration_ms', 'popularity', 'explicit', 'album_name', 'album_release_date', 'album_release_year', 'added_at_date', 'url', 'artist_list', 'first_artist', 'first_letter', 'id'), back_columns=('type', 'episode', 'track', 'album', 'disc_number', 'track_number', 'artists', 'preview_url', 'uri', 'href', 'available_markets', 'external_ids', 'external_urls'))

Get tracks metadata for given key(s), as a pandas DataFrame.

By default, will return all tracks in the collection.

* **Return type:**
  `DataFrame`

### sung.base.search_tracks(query, egress=functools.partial(<function glom>, spec='tracks.items', default=None), \*, search_type='track', market=None, year=None, genre=None, limit=20, offset=0, client=<function get_spotify_client>)

Search for tracks on Spotify.

* **Parameters:**
  * **the** ( *- query - the search query* *(**see how to write a query in*) – official documentation)
  * **return.** ( *- offset - the index* *of* *the first item to*)
  * **'from_token'.** ( *- market - An ISO 3166-1 alpha-2 country code* *or* *the string*)
  * **return.**
  * **return.**

### sung.base.track_ids_to_metas(track_ids, client)

Convert track IDs to track metadata using the Spotify client.

### sung.base.track_metas_to_track_ids(track_metas)

Extract track IDs from track metadata.
