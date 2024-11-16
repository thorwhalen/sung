r"""
Tools to get music metadata (from Spotify, Wikipedia, etc.)


>>> from sung.base import Tracks, Playlist  # Import necessary classes
>>> from sung import delete_playlist  # Import delete function for playlists

Search for tracks with the query 'Love', limiting the results to 7

>>> tracks = Tracks.search(query='Love', limit=7)

You can also make a `tracks` object by passing a list of track IDs or urls

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

`tracks` is a `Mapping` (that means "dict-like"), so you can do what you do with dicts...

Like listing the track keys (IDs)

>>> list(tracks)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
['1vrd6UOGamcKNGnSHJQlSt',
 '3CeCwYWvdfXbZLXFhBrbnf',
 ...,
 '6dBUzqjtbnIa1TwYbyw5CM',
 '7hR22TOX3RorxJPcsz5Wbo']


Like accessing the value of a track for a given key. 
The value is a bunch of metadata about the track.

>>> track_metadata = tracks['1dGr1c8CrMLDpV6mPbImSI']  # get metadata of track via it's id
>>> assert isinstance(track_metadata, dict)
>>> sorted(track_metadata)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
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


>>> df = tracks.data  # doctest: +SKIP
                                                    name  duration_ms  popularity  ...  track_number   type                                   uri
    id                                                                              ...
    1vrd6UOGamcKNGnSHJQlSt                     Love Story       235266          62  ...             3  track  spotify:track:1vrd6UOGamcKNGnSHJQlSt
    3CeCwYWvdfXbZLXFhBrbnf  Love Story (Taylor’s Version)       235766          76  ...
    ...
    6dBUzqjtbnIa1TwYbyw5CM                    Lovers Rock       213920          85  ...             9  track  spotify:track:6dBUzqjtbnIa1TwYbyw5CM
    7hR22TOX3RorxJPcsz5Wbo                  Love Somebody       204828          86  ...             1  track  spotify:track:7hR22TOX3RorxJPcsz5Wbo


Create a new playlist named 'my_test_playlist' with the selected tracks

>>> playlist = Playlist.create_from_track_list(
...     track_list=list(tracks),
...     playlist_name='my_test_playlist'
... )


Get the playlist URL of the newly created playlist (so you can check it out on Spotify)

>>> playlist.playlist_url  # doctest: +ELLIPSIS
'https://open.spotify.com/playlist/...'


Delete the playlist.

We purposely tried to make deleting a playlist not as easy as the other actions. 
So we didn't attach a delete method to the playlist instance, but put this in a 
separate function you have to import. 
Also, we made that function verbose, and asking for confirmation by default. 
(But there's arguments to control that, so you can use `functools.partial` to 
make your own cowboy (not speaking and not asking for permission) version).

>>> delete_playlist(playlist.playlist_id, ask_confirmation=False)  # doctest: +ELLIPSIS
Playlist ... has been deleted (unfollowed).


Instantiate a Playlist object using the URL (let's just use the one we just created!)

>>> top50_global_url = 'https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF?si=d6e0c7bc8f59473b'
>>> playlist_obj = Playlist(top50_global_url)
>>> df = playlist_obj.data
>>> df['first_artist'] = df['artists'].apply(lambda x: x[0]['name'])
>>> df['name_and_first_artist'] = df['name'] + ' - ' + df['first_artist']
>>> top_5_tracks = playlist_obj.data.iloc[:5].name_and_first_artist
>>> top_5_tracks  # doctest: +SKIP
id
2plbrEY59IikOBgBGLjaoe          Die With A Smile - Lady Gaga
5vNRhkKd0yEAg8suGBpjeY                           APT. - ROSÉ
6dOtVTDdiauQNBQEDOtlAB    BIRDS OF A FEATHER - Billie Eilish
7ne4VBA60CxGM75vw0EYad        That’s So True - Gracie Abrams
7tI8dRuH2Yc6RuoTjxo4dU                           Who - Jimin
Name: name_and_first_artist, dtype: object

"""

from sung.base import (
    search_tracks,
    Tracks,
    PlaylistReader,
    Playlist,
    extract_standard_metadata,
    SpotifyDacc,
    delete_playlist,
)
from sung.util import (
    extractor,
    cast_track_key,
    ensure_track_id,
    get_spotify_client,
    ensure_playlist_id,
)
from sung.tools import TracksAnalysis
