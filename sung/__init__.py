"""
Tools to get music metadata (from Spotify, Wikipedia, etc.)

>>> from sung import search_tracks
>>> search_tracks('Autumn leaves', limit=3, genre='jazz')  # doctest: +ELLIPSIS

"""

from sung.base import search_tracks, track_metadata
from sung.util import extractor
