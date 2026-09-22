# sung.util

Utility functions for the sung package.

### Functions

| [`cast_track_key`](#sung.util.cast_track_key)(track_key[, target_kind, ...])   | Convert a Spotify track key between different formats.                    |
|--------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| `coalesce_string_values`(d, \*\*coalece_kwargs)                                                  |                                                                           |
| [`convert_date`](#sung.util.convert_date)(date_str[, read_formats])          | Convert a date string to a standard format (YYYY-MM-DD).                  |
| `df_extraction`(extractor_func, df)                                                              |                                                                           |
| `df_extractor`(spec)                                                                             |                                                                           |
| `ensure_client`([client])                                                                        |                                                                           |
| `ensure_extractor`(x)                                                                            |                                                                           |
| [`ensure_playlist_id`](#sung.util.ensure_playlist_id)(playlist_spec)               | Ensure that a playlist ID is in the correct format.                       |
| `extractor`(spec)                                                                                |                                                                           |
| [`get_config`](#sung.util.get_config)(config_name)                         | Get the value of a configuration variable.                                |
| [`get_spotify_client`](#sung.util.get_spotify_client)([client, ensure_scope, ...]) | Get a Spotify client.                                                     |
| `get_spotify_creds`(\*\*client_creds_kwargs)                                                     |                                                                           |
| `get_spotify_oauth_creds`(\*\*oauth_kwargs)                                                      |                                                                           |
| `identity`(x)                                                                                    |                                                                           |
| `is_extractor`(x)                                                                                |                                                                           |
| [`move_columns_to_back`](#sung.util.move_columns_to_back)(df, columns, \*[, ...])    | Returns a copy of df with given columns in the back, in the order given.  |
| [`move_columns_to_front`](#sung.util.move_columns_to_front)(df, columns, \*[, ...])   | Returns a copy of df with given columns in the front, in the order given. |
| `pop_client_id_and_secret`(kwargs)                                                               |                                                                           |
| [`strip_values`](#sung.util.strip_values)(d)                                 | Return a new dictionary with all string values stripped.                  |

### sung.util.cast_track_key(track_key, target_kind='uri', , src_kind=None)

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

### sung.util.convert_date(date_str, read_formats=('%Y-%m-%d', '%Y', '%Y-%m'))

Convert a date string to a standard format (YYYY-MM-DD).

### sung.util.ensure_playlist_id(playlist_spec)

Ensure that a playlist ID is in the correct format.

* **Parameters:**
  **check** ( *- playlist_id - the playlist ID to*)
* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
* **Returns:**
  The playlist ID in the correct format.

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
```

### sung.util.ensure_track_id(track_key, , target_kind='id', src_kind=None)

Convert a Spotify track key between different formats.

* **Parameters:**
  * **convert** ( *- track_key - the track key to*)
  * **to** ( *- target_kind - the format to convert*)
  * **key** ( *- src_kind - the format* *of* *the input track*)
* **Returns:**
  The track key in the target format.
* **Return type:**
  [*str*](https://docs.python.org/3/builtins/stdtypes.html#str)

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

### sung.util.get_config(config_name)

Get the value of a configuration variable.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### sung.util.get_spotify_client(client=None, , ensure_scope='', scope='', auth=None, requests_session=True, client_credentials_manager=None, oauth_manager=None, auth_manager=None, proxies=None, requests_timeout=5, status_forcelist=None, retries=3, status_retries=3, backoff_factor=0.3, language=None, client_id=None, client_secret=None, redirect_uri=None, state=None, cache_path=None, username=None, show_dialog=False, open_browser=True, cache_handler=None)

Get a Spotify client.

* **Parameters:**
  * **client** ( *- \*\*kwargs - additional arguments to pass to the Spotify*)
  * **auth_manager** ( *- ensure_scope - a scope to ensure is included in the client's*)
  * **client**
  * **client**

The purpose of having scope and ensure_scope is to allow you to ensure some needed
scopes exist when a code block is asking for a Spotify client with it’s own
scope desires.

### sung.util.move_columns_to_back(df, columns, , allow_excess=True)

Returns a copy of df with given columns in the back, in the order given.

* **Parameters:**
  * **modify** ( *- df - the DataFrame to*)
  * **back** ( *- columns - the columns to move to the*)
  * **DataFrame** ( *- allow_excess - whether to allow columns not in the*)
* **Return type:**
  `DataFrame`
* **Returns:**
  The modified DataFrame.

### sung.util.move_columns_to_front(df, columns, , allow_excess=True)

Returns a copy of df with given columns in the front, in the order given.

* **Parameters:**
  * **modify** ( *- df - the DataFrame to*)
  * **front** ( *- columns - the columns to move to the*)
  * **DataFrame** ( *- allow_excess - whether to allow columns not in the*)
* **Return type:**
  `DataFrame`
* **Returns:**
  The modified DataFrame.

### sung.util.strip_values(d)

Return a new dictionary with all string values stripped.

* **Return type:**
  [`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)
