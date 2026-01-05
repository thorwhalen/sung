"""Base functionalities for the sung package.

This module provides foundational tools and abstractions for interacting with Spotify's
API. It includes classes and functions to search for tracks, manage playlists, and
handle Spotify track metadata. The utilities here are designed to integrate seamlessly
with Spotify's API and streamline data extraction and manipulation.

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
"""

from typing import (
    Union,
    Optional,
    List,
    Any,
    Dict,
)
from collections.abc import Iterable, Sequence, Callable, MutableMapping, Mapping
from operator import itemgetter
from functools import cached_property, lru_cache
from collections.abc import Mapping
from abc import ABC

import pandas as pd

from sung.util import (
    get_spotify_client,
    ensure_client,
    DFLT_LIMIT,
    extractor,
    convert_date,
    cast_track_key,
    ensure_track_id,
    SearchTypeT,
    TrackId,
    TrackRef,
    TrackKey,
    TrackMetadata,
    move_columns_to_front,
    move_columns_to_back,
    front_columns_for_track_metas,
    back_columns_for_track_metas,
    spotify_audio_features_fields,
    spotify_track_metadata_numerical_field_names,
)


DFLT_VERBOSE = True


# --------------------------------------------------------------------------------------
# Extracting information from track info

from sung.util import extractor, df_extractor

extra_track_metadata_extractions = {
    "artist_list": "artists.*.name",
    "album_name": "album.name",
    "album_release_date": "album.release_date",
    "url": "external_urls.spotify",
    "first_artist": "artists.0.name",
    "album_total_tracks": "album.total_tracks",
    "album_images": "album.images",
}


extract_extra_metadata = extractor(extra_track_metadata_extractions)  # maybe obsolete?
df_extract_extra_metadata = df_extractor(extra_track_metadata_extractions)


def track_metadata(track_id, *, client=get_spotify_client):
    client = ensure_client(client)

    # Get track details
    track = client.track(track_id)

    return extract_extra_metadata(track)


def process_track_columns(df):
    extras = df_extract_extra_metadata(df)
    # assert there's not duplicate columns between df and extras
    common_columns = set(df.columns) & set(extras.columns)
    if common_columns:
        raise ValueError(f"Columns {common_columns} are duplicated in both dataframes.")
    extras["artists_names"] = extras["artist_list"].apply("; ".join)
    extras["album_release_date"] = extras["album_release_date"].apply(convert_date)
    extras["album_release_year"] = extras["album_release_date"].str[:4].astype(int)
    return pd.concat([df, extras], axis=1)


# --------------------------------------------------------------------------------------
# Tracks and Playlist classes

TrackKeySpec = Union[TrackId, int, slice, Iterable[TrackId]]


def track_ids_to_metas(track_ids, client):
    """Convert track IDs to track metadata using the Spotify client."""
    response = client.tracks(track_ids)
    return response["tracks"]


def track_metas_to_track_ids(track_metas):
    """Extract track IDs from track metadata."""
    return [meta["id"] for meta in track_metas]


class TracksBase(Mapping[TrackId, TrackMetadata]):
    """Base class representing a collection of Spotify tracks."""

    _track_ids = ()
    _track_metas = ()

    def __init__(
        self,
        tracks: Iterable[TrackId | TrackMetadata],
        *,
        # track_ids: Optional[Iterable[TrackId]] = None,
        # track_metas: Optional[Iterable[TrackMetadata]] = None,
        client: Any | None = None,
    ):
        if client is None:
            client = get_spotify_client()
        self.client = client

        tracks = list(tracks)

        track_ids, track_metas = None, None
        first_track = next(iter(tracks), None)
        if first_track is not None:
            if isinstance(first_track, str):
                track_ids = tracks
            elif isinstance(first_track, dict):
                track_metas = tracks

            self._track_ids = (
                list(map(ensure_track_id, track_ids)) if track_ids is not None else None
            )
            self._track_metas = list(track_metas) if track_metas is not None else None

    @cached_property
    def _cached_audio_analysis_func(self):
        return lru_cache(maxsize=10_000)(self.client.audio_analysis)

    @cached_property
    def track_ids(self) -> list[TrackId]:
        if self._track_ids is not None:
            return self._track_ids
        elif self._track_metas is not None:
            self._track_ids = track_metas_to_track_ids(self._track_metas)
            return self._track_ids
        else:
            raise ValueError("No track IDs or metadata available")

    @cached_property
    def track_metas(self) -> list[TrackMetadata]:
        if self._track_metas is not None:
            return self._track_metas
        elif self._track_ids is not None:
            self._track_metas = track_ids_to_metas(self._track_ids, self.client)
            return self._track_metas
        else:
            raise ValueError("No track IDs or metadata available")

    def __iter__(self) -> Iterable[TrackId]:
        return iter(self.track_ids)

    def __len__(self) -> int:
        return len(self.track_ids)

    def __contains__(self, key: TrackId) -> bool:
        return key in set(self.track_ids)

    def __getitem__(self, key: TrackKeySpec) -> TrackMetadata | list[TrackMetadata]:
        return self._getitem(key)

    def _getitem(self, key: TrackKeySpec) -> TrackMetadata | list[TrackMetadata]:
        """
        Get track(s) by key.

        The key could be a track ID, a track index, a slice, or a list of track IDs.
        """
        if isinstance(key, str):
            if key not in self:
                raise KeyError(key)
            index = self.track_ids.index(key)
            return self.track_metas[index]
        elif isinstance(key, int):
            index = key % len(self)
            return self.track_metas[index]
        elif isinstance(key, slice):
            indices = range(*key.indices(len(self)))
            return [self.track_metas[i] for i in indices]
        elif isinstance(key, Iterable):
            keys = list(key)
            indices = []
            for k in keys:
                if k not in self:
                    raise KeyError(f"Key {k} not found in the collection")
                indices.append(self.track_ids.index(k))
            return [self.track_metas[i] for i in indices]
        else:
            raise TypeError(f"Invalid key type {type(key)}")

    @cached_property
    def data(self):
        # TODO: Add the added year or date when available
        metadata_df = self.meta_dataframe()
        audio_features_df = pd.DataFrame(self.audio_features).T.set_index("id")
        audio_features_df = audio_features_df[list(spotify_audio_features_fields)]

        # Merge metadata and audio features
        df = metadata_df.join(audio_features_df, how="inner")
        return df

    @cached_property
    def audio_features(self):
        from itertools import chain

        track_ids = list(self)

        def _audio_features_chunks():
            chunks = (track_ids[i : i + 100] for i in range(0, len(track_ids), 100))
            for chunk in chunks:
                yield self.client.audio_features(chunk)

        return dict(zip(track_ids, chain.from_iterable(_audio_features_chunks())))

    audio_features.spotify_audio_features_fields = spotify_audio_features_fields

    # TODO: Deprecate. Just use numerical_features_df
    @property
    def audio_features_df(self):
        print(f"Deprecated: Use 'numerical_features_df' instead.")
        return pd.DataFrame(self.audio_features).T.set_index("id")

    @property
    def numerical_features_df(self):
        fields = list(spotify_track_metadata_numerical_field_names) + list(
            spotify_audio_features_fields
        )
        return self.data[fields]

    def audio_analysis(self, key: TrackKeySpec):
        track_id = ensure_track_id(key)
        return self._cached_audio_analysis_func(track_id)

    def meta_dataframe(
        self,
        key: TrackKeySpec = slice(None),
        *,
        front_columns=front_columns_for_track_metas,
        back_columns=back_columns_for_track_metas,
    ) -> "pd.DataFrame":
        """
        Get tracks metadata for given key(s), as a pandas DataFrame.

        By default, will return all tracks in the collection.
        """
        data = self[key]
        if isinstance(data, dict):
            data = [data]
        df = pd.DataFrame(data)
        df = process_track_columns(df)
        df = move_columns_to_front(df, front_columns)
        df = move_columns_to_back(df, back_columns)
        if "id" in df.columns:
            df.set_index("id", drop=False, inplace=True)
        return df

    dataframe = meta_dataframe  # Alias for backwards compatibility


class Tracks(TracksBase):
    """A collection of Spotify tracks represented by track IDs or track metadata."""

    def __init__(
        self,
        tracks: Iterable[TrackId | TrackMetadata],
        # track_ids: Optional[Iterable[TrackRef]] = None,
        # track_metas: Optional[Iterable[TrackMetadata]] = None,
        *,
        client: Any | None = None,
    ):
        super().__init__(tracks, client=client)
        self._track_ids_set = set(self.track_ids)

    @classmethod
    def search(
        cls,
        query: str,
        egress: Callable = extractor("tracks.items"),
        *,
        search_type: SearchTypeT = "track",
        market=None,
        year=None,
        genre=None,
        limit: int = DFLT_LIMIT,
        offset: int = 0,
        client: Any | None = None,
    ):
        tracks = search_tracks(
            query=query,
            egress=egress,
            search_type=search_type,
            market=market,
            year=year,
            genre=genre,
            limit=limit,
            offset=offset,
            client=client,
        )
        track_metas = tracks
        return cls(track_metas, client=client)

    def __contains__(self, key: TrackId) -> bool:
        return key in self._track_ids_set


# --------------------------------------------------------------------------------------
# Search Function


def search_tracks(
    query: str,
    egress: Callable = extractor("tracks.items"),
    *,
    search_type: SearchTypeT = "track",
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
                  official documentation)
        - search_type - the types of items to return.
        - market - An ISO 3166-1 alpha-2 country code or the string 'from_token'.
        - limit - the number of items to return.
        - offset - the index of the first item to return.
    """
    client = ensure_client(client)

    # Build query
    query_string = query
    if year:
        query_string += f" year:{year}"
    if genre:
        query_string += f" genre:{genre}"

    # Execute search
    results = client.search(
        q=query_string, type=search_type, market=market, limit=limit, offset=offset
    )

    return egress(results)


# --------------------------------------------------------------------------------------
# Playlist Classes


# TODO: Make it a subclass of TracksBase, or Tracks
class PlaylistReader(Tracks, Mapping[TrackId, TrackMetadata]):
    """Read-only access to a Spotify playlist."""

    def __init__(self, playlist_id: str, *, client: Any | None = None):
        if client is None:
            client = get_spotify_client()
        self.client = client
        self.playlist_id = playlist_id
        self._tracks: Tracks | None = None  # Will be a Tracks instance

    def __repr__(self) -> str:
        return f'PlaylistReader("{self.playlist_id}")'

    @property
    def tracks(self) -> Tracks:
        if self._tracks is None:
            track_metas = self._fetch_track_metas()
            self._tracks = Tracks(tracks=track_metas, client=self.client)
        return self._tracks

    def _fetch_track_metas(self) -> list[TrackMetadata]:
        track_metas = []
        offset = 0
        limit = 100
        while True:
            response = self.client.playlist_items(
                self.playlist_id,
                offset=offset,
                limit=limit,
                fields="items.track,next",
            )
            items = response["items"]
            if not items:
                break
            for item in items:
                track = item["track"]
                if track:
                    track_metas.append(track)
            if response["next"] is None:
                break
            offset += limit
        return track_metas

    def __getitem__(self, key: TrackKeySpec) -> TrackMetadata | list[TrackMetadata]:
        return self.tracks[key]

    def __iter__(self) -> Iterable[TrackId]:
        return iter(self.tracks)

    def __len__(self) -> int:
        return len(self.tracks)

    def __contains__(self, key: TrackId) -> bool:
        return key in self.tracks

    @property
    def playlist_url(self) -> str:
        return f"https://open.spotify.com/playlist/{self.playlist_id}"

    # @cached_property
    # def data(self):
    #     return self.meta_dataframe()

    # def meta_dataframe(self, key: TrackKeySpec = slice(None)) -> 'pd.DataFrame':
    #     return self.tracks.meta_dataframe(key)


class Playlist(PlaylistReader, MutableMapping[TrackId, TrackMetadata]):
    """A Spotify playlist with mutable mapping interface."""

    def __init__(self, playlist_id: str, *, client: Any | None = None):
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

    def add_songs(self, track_list: TrackId | Iterable[TrackId]) -> None:
        if isinstance(track_list, str):
            track_list = [track_list]
        else:
            track_list = list(track_list)
        for i in range(0, len(track_list), 100):
            self.client.playlist_add_items(self.playlist_id, track_list[i : i + 100])
        self._invalidate_cache()

    def delete_songs(self, track_list: TrackId | Iterable[TrackId]) -> None:
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
        client: Any | None = None,
        user_id=None,
    ) -> "Playlist":
        """
        Create a new playlist from a list of track IDs.

        Parameters:
            - track_list: A list of track IDs to add to the playlist.
            - playlist_name: The name of the new playlist.
            - public: Whether the playlist should be public.
            - client: The Spotify client to use for creating the playlist.
            - user_id: The user ID of the playlist owner.
        """
        track_list = [cast_track_key(track, "uri") for track in track_list]

        # self.client = get_spotify_client(client, ensure_scope="playlist-modify-private playlist-modify-public")

        if client is None:
            scope = "playlist-modify-public playlist-modify-private"
            client = get_spotify_client(ensure_scope=scope)

        if user_id is None:
            user_id = client.me()["id"]

        # Create a new playlist
        playlist = client.user_playlist_create(
            user=user_id, name=playlist_name, public=public
        )
        playlist_id = playlist["id"]

        # Add tracks to the playlist in batches of 100
        for i in range(0, len(track_list), 100):
            client.playlist_add_items(playlist_id, track_list[i : i + 100])

        return cls(playlist_id, client=client)


def delete_playlist(playlist_id, verbose=DFLT_VERBOSE, *, ask_confirmation=True):
    # Authenticate with appropriate scope
    client = get_spotify_client(scope="playlist-modify-public playlist-modify-private")

    if ask_confirmation:
        response = input(
            "Are you sure you want to delete the playlist? (y/yes to confirm): "
        )
        if response.lower() not in ("y", "yes"):
            print("Playlist deletion aborted.")
            return

    # Unfollow (delete) the playlist
    client.current_user_unfollow_playlist(playlist_id)
    if verbose:
        print(f"Playlist {playlist_id} has been deleted (unfollowed).")


# --------------------------------------------------------------------------------------
# A data accessor for Spotify functionality


class SpotifyDacc:
    def __init__(self, client=None):
        self.client = get_spotify_client(client)

    def recently_played(self, *, extract="items.*.track.name", limit=50, **kwargs):
        client = get_spotify_client(
            self.client, ensure_scope="user-read-recently-played"
        )
        results = client.current_user_recently_played(limit=limit)
        extract = extractor.ensure_extractor(extract)
        return extract(results)

    def current_user_top_tracks(
        self, *, extract=None, limit=20, time_range="long_term", **kwargs
    ):
        """
        Get user's top tracks

        time_range: 'short_term', 'medium_term', 'long_term'

        To get names of artists, use extract='items.*.artists.*.name'
        """
        client = get_spotify_client(self.client, ensure_scope="user-top-read")
        results = client.current_user_top_tracks(
            limit=limit, time_range=time_range, **kwargs
        )
        extract = extractor.ensure_extractor(extract)
        return extract(results)
