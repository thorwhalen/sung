"""
Tools to get music metadata (from Spotify, Wikipedia, etc.)

>>> from sung import search_tracks
>>> search_tracks('Autumn leaves', limit=3, genre='jazz')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
[{'album': {'album_type': 'album', ...

"""

from sung.base import (
    search_tracks,
    Tracks,
    PlaylistReader,
    Playlist,
    extract_standard_metadata,
    SpotifyDacc,
)
from sung.util import (
    extractor,
    cast_track_key,
    ensure_track_id,
    get_spotify_client,
    ensure_playlist_id,
)
from sung.tools import TracksAnalysis
