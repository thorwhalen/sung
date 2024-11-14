"""Base functionalities for the sung package."""

from typing import (
    Union,
    Iterable,
    Sequence,
    Optional,
    List,
    Set,
    Any,
    Dict,
    Callable,
    MutableMapping,
    Mapping,
)
from functools import cached_property
from abc import ABC, abstractmethod

from sung.util import (
    get_spotify_client,
    ensure_client,
    DFLT_LIMIT,
    extractor,
    cast_track_key,
    ensure_track_id,
)


# TODO: Include all modifiers in the signature (only year and genre for now)?
# TODO: Make signature using Spotify.search signature
def search_tracks(
    query: str,
    egress: Callable = extractor('tracks.items'),
    *,
    search_type='track',
    market=None,
    year=None,
    genre=None,
    limit: int = DFLT_LIMIT,
    offset: int = 0,
    client=get_spotify_client,
):
    """
    Search for tracks on Spotify.

    Parameters:
        - query - the search query (see how to write a query in the
                official documentation https://developer.spotify.com/documentation/web-api/reference/search/)  # noqa
        - search_type - the types of items to return. One or more of 'artist', 'album',
                    'track', 'playlist', 'show', and 'episode'.  If multiple types are desired,
                    pass in a comma separated string; e.g., 'track,album,episode'.
        - market - An ISO 3166-1 alpha-2 country code or the string
                    from_token.
        - limit - the number of items to return (min = 1, default = 10, max = 50). The limit is applied
                    within each type, not on the total response.
        - offset - the index of the first item to return

    """
    client = ensure_client(client)

    # Build query
    # TODO: Make function using spotify_search_modifiers to do this
    query_string = query
    if year:
        query_string += f" year:{year}"
    if genre:
        query_string += f" genre:{genre}"

    # Execute search
    results = client.search(
        q=query_string, type=search_type, market=market, limit=limit, offset=offset
    )

    # Extract tracks and return a list of song names with additional details

    return egress(results)


# --------------------------------------------------------------------------------------
# Tracks and Playlist classes

# TODO: Repair: The setup doesn't allow dol.wrap_kvs everywhere (e.g., try adding a
# extract_standard_metadata value_decoder to a playlist and do playlist.dataframe)
# TODO: Add value caching (e.g. lru_cache on _getitem) with a cache clearing method,
#    and possibly and automatic cache invalidation when appropriate
# TODO: Use pydantic models where it makes sense

# Type aliases
# TrackId = str
# TrackURI = str
# TrackSpec = Union[TrackId, TrackURI]
# TrackKey = Union[TrackId, TrackURI, int, slice, Iterable[TrackId]]
# TrackMetadata = Dict[str, Any]
from sung.util import TrackId, TrackRef, TrackKey, TrackMetadata


class TracksABC(Mapping[TrackId, TrackMetadata], ABC):
    """Abstract base class representing a collection of Spotify tracks."""

    def __init__(self, *, client: Optional[Any] = None):
        if client is None:
            client = get_spotify_client()
        self.client = client

    @property
    @abstractmethod
    def track_ids(self) -> Sequence[TrackId]:
        """Should return the list of track IDs."""
        pass

    def __iter__(self) -> Iterable[TrackId]:
        return iter(self.track_ids)

    def __len__(self) -> int:
        return len(self.track_ids)

    def __contains__(self, key: TrackId) -> bool:
        return key in set(self.track_ids)

    def __getitem__(self, key: TrackKey) -> Union[TrackMetadata, List[TrackMetadata]]:
        return self._getitem(key)

    def _getitem(self, key: TrackKey) -> Union[TrackMetadata, List[TrackMetadata]]:
        """
        Get track(s) by key.

        The key could be a track ID, a track index, a slice, or a list of track IDs.
        """
        if isinstance(key, str):
            if key not in self:
                raise KeyError(key)
            # Get the track metadata
            track: TrackMetadata = self.client.track(key)
            return track
        elif isinstance(key, slice):
            keys = self.track_ids[key]
            return [self[k] for k in keys]
        elif isinstance(key, Iterable):
            keys = list(key)
            missing_keys = [k for k in keys if k not in self]
            if missing_keys:
                raise KeyError(f"Keys {missing_keys} not found in the collection")
            response_dict = self.client.tracks(keys)
            tracks: List[TrackMetadata] = response_dict['tracks']
            return tracks
        elif isinstance(key, int):
            index = key
            if -len(self) <= index < len(self):
                key = self.track_ids[index]
                return self[key]
            else:
                raise IndexError(f"Index {index} out of range")
        else:
            raise TypeError(f"Invalid key type {type(key)}")

    def dataframe(self, key: TrackKey = slice(None)) -> 'pd.DataFrame':
        """
        Get tracks metadata for given key(s), as a pandas DataFrame.

        By default, will return all tracks in the collection.
        """
        import pandas as pd  # Delayed import to avoid unnecessary dependency

        data = self[key]
        if isinstance(data, dict):
            data = [data]
        return pd.DataFrame(data)


class Tracks(TracksABC):
    """A collection of Spotify tracks represented by a list of track IDs."""

    def __init__(self, track_ids: Sequence[TrackRef], *, client: Optional[Any] = None):
        super().__init__(client=client)
        self._track_ids = list(map(ensure_track_id, track_ids))
        self._track_ids_set = set(self._track_ids)

    @property
    def track_ids(self) -> Sequence[TrackId]:
        return self._track_ids

    def __len__(self) -> int:
        return len(self._track_ids)

    def __iter__(self) -> Iterable[TrackId]:
        return iter(self._track_ids)

    def __contains__(self, key: TrackId) -> bool:
        return key in self._track_ids_set


class PlaylistReader(Mapping[TrackId, TrackMetadata]):
    """Read-only access to a Spotify playlist."""

    def __init__(self, playlist_id: str, *, client: Optional[Any] = None):
        if client is None:
            client = get_spotify_client()
        self.client = client
        self.playlist_id = playlist_id
        self._tracks: Optional[Tracks] = None  # Will be a Tracks instance

    def __repr__(self) -> str:
        return f'PlaylistReader("{self.playlist_id}")'

    @property
    def tracks(self) -> Tracks:
        if self._tracks is None:
            track_ids = self._fetch_track_ids()
            self._tracks = Tracks(track_ids, client=self.client)
        return self._tracks

    def _fetch_track_ids(self) -> List[TrackId]:
        track_ids = []
        offset = 0
        limit = 100
        while True:
            response = self.client.playlist_items(
                self.playlist_id,
                offset=offset,
                limit=limit,
                fields='items.track.id,next',
            )
            items = response['items']
            if not items:
                break
            for item in items:
                track = item['track']
                if track and track['id']:
                    track_ids.append(track['id'])
            if response['next'] is None:
                break
            offset += limit
        return track_ids

    def __getitem__(self, key: TrackKey) -> Union[TrackMetadata, List[TrackMetadata]]:
        return self.tracks[key]

    def __iter__(self) -> Iterable[TrackId]:
        return iter(self.tracks)

    def __len__(self) -> int:
        return len(self.tracks)

    def __contains__(self, key: TrackId) -> bool:
        return key in self.tracks

    def playlist_url(self) -> str:
        return f"https://open.spotify.com/playlist/{self.playlist_id}"

    def dataframe(self, keys: TrackKey = slice(None)) -> 'pd.DataFrame':
        return self.tracks.dataframe(keys)


# TODO: Change so it uses client.playlist_tracks to pupulate the tracks instead
#    Since the metadata given with that method is more complete (e.g. has added_at)
class Playlist(PlaylistReader, MutableMapping[TrackId, TrackMetadata]):
    """A Spotify playlist with mutable mapping interface."""

    def __init__(self, playlist_id: str, *, client: Optional[Any] = None):
        super().__init__(playlist_id=playlist_id, client=client)

    def __setitem__(self, key: TrackId, value: Any) -> None:
        raise NotImplementedError(
            "Tracks cannot be added or modified by setting an item. "
            "Use the 'extend' method to add tracks."
        )

    def __delitem__(self, key: TrackId) -> None:
        if key not in self:
            raise KeyError(key)
        self.delete_songs([key])
        self._invalidate_cache()

    def add_songs(self, track_list: Union[TrackId, Iterable[TrackId]]) -> None:
        if isinstance(track_list, str):
            track_list = [track_list]
        else:
            track_list = list(track_list)
        for i in range(0, len(track_list), 100):
            self.client.playlist_add_items(self.playlist_id, track_list[i : i + 100])
        self._invalidate_cache()

    def delete_songs(self, track_list: Union[TrackId, Iterable[TrackId]]) -> None:
        if isinstance(track_list, str):
            track_list = [track_list]
        else:
            track_list = list(track_list)
        self.client.playlist_remove_all_occurrences_of_items(
            self.playlist_id, track_list
        )
        self._invalidate_cache()

    def extend(self, track_list: Iterable[TrackId]) -> None:
        self.add_songs(track_list)

    def append(self, track_id: TrackId) -> None:
        self.extend([track_id])

    def _invalidate_cache(self) -> None:
        self._tracks = None  # Invalidate the cached Tracks instance

    @classmethod
    def create_from_track_list(
        cls,
        track_list: Sequence[TrackId] = (),
        playlist_name: str = "New Playlist",
        public: bool = True,
        *,
        client: Optional[Any] = None,
    ) -> 'Playlist':
        """
        Create a new playlist from a list of track IDs.
        """
        track_list = [cast_track_key(track, "uri") for track in track_list]

        if client is None:
            scope = "playlist-modify-private playlist-modify-public"
            client = get_spotify_client(scope=scope)

        # Get the current user's ID
        user_id = client.me()['id']

        # Create a new playlist
        playlist = client.user_playlist_create(
            user=user_id, name=playlist_name, public=public
        )
        playlist_id = playlist['id']

        # Add tracks to the playlist in batches of 100
        for i in range(0, len(track_list), 100):
            client.playlist_add_items(playlist_id, track_list[i : i + 100])

        return cls(playlist_id, client=client)


# --------------------------------------------------------------------------------------
# Extracting information from track info

# TODO: Use glom (or dol.paths_getter) and dol.ValueCodec to simplify this and offer
#    a menu of field sets
from sung.util import extractor

standard_track_metadata = {
    'name': 'name',
    'artist': 'artists.0.name',
    'album': 'album.name',
    'release_date': 'album.release_date',
    'duration_ms': 'duration_ms',
    'popularity': 'popularity',
    'explicit': 'explicit',
    'external_url': 'external_urls.spotify',
    'preview_url': 'preview_url',
    'track_number': 'track_number',
    'album_total_tracks': 'album.total_tracks',
    'available_markets': 'available_markets',
    'album_images': 'album.images',
}

extract_standard_metadata = extractor(standard_track_metadata)


def track_metadata(track_id, *, client=get_spotify_client):
    client = ensure_client(client)

    # Get track details
    track = client.track(track_id)

    return extract_standard_metadata(track)


# --------------------------------------------------------------------------------------
# A data accessor for Spotify functionality

class SpotifyDacc:
    def __init__(self, client=None):
        self.client = get_spotify_client(client)

    # TODO: Sometimes works, sometimes says "insufficient scope". Don't know why,
    def recently_played(self, *, extract='items.*.track.name', limit=50, **kwargs):
        client = get_spotify_client(
            self.client, _ensure_scope='user-read-recently-played'
        )
        results = client.current_user_recently_played(limit=50)
        extract = extractor.ensure_extractor(extract)
        return extract(results)

    # TODO: Note tested
    def current_user_top_tracks(
        self, *, extract=None, limit=20, time_range='long_term', **kwargs
    ):
        """
        Get user's top tracks

        time_range: 'short_term', 'medium_term', 'long_term'

        To get names of artists, use extract='items.*.artists.*.name'

        """
        client = get_spotify_client(self.client, _ensure_scope='user-top-read')
        results = client.current_user_top_tracks(
            limit=limit, time_range=time_range, **kwargs
        )
        extract = extractor.ensure_extractor(extract)
        return extract(results)
