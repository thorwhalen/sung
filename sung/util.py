"""Utility functions for the sung package."""

# TODO: use openAPI definition to create pydantic models for data
#  see https://github.com/thorwhalen/sung/discussions/1#discussioncomment-10990012


import re
import os
from typing import (
    Literal,
    T,
    Callable,
    TypeVar,
    Optional,
    Dict,
    Union,
    Iterable,
    Any,
    Mapping,
)
from functools import partial

from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from glom import glom, Spec, Coalesce

from i2 import Sig

DFLT_LIMIT = 20

# TODO: Get automatically from pydantic model when available
SearchTypeT = Literal['artist', 'album', 'track', 'playlist', 'show', 'episode']


def identity(x: T) -> T:
    return x


Extractor = TypeVar('Extractor', bound=Callable)  # TODO: Specify more precisely


def extractor(spec: Union[Spec, str, Iterable[str], Mapping[str, str]]) -> Extractor:
    if isinstance(spec, str):
        return partial(glom, spec=spec, default=None)
    elif isinstance(spec, Iterable) and not isinstance(spec, Mapping):
        spec = {k: k for k in spec}
    return partial(glom, spec=coalesce_to_default(spec))


def is_extractor(x: Any) -> bool:
    return (
        callable(x)
        and hasattr(x, 'func')
        and getattr(x.func, '__name__', '') == 'glom'
        or x is identity
    )


def ensure_extractor(x: Any) -> Extractor:
    if x is None:
        return identity
    if is_extractor(x):
        return x
    else:
        return extractor(x)


extractor.is_extractor = is_extractor
extractor.ensure_extractor = ensure_extractor


def coalesce_string_values(d: dict, **coalece_kwargs) -> dict:
    def coalesced_items():
        for k, v in d.items():
            if isinstance(v, str):
                yield k, Coalesce(v, **coalece_kwargs)
            else:
                yield k, v

    return dict(coalesced_items())


coalesce_to_default = partial(coalesce_string_values, default=None)


def get_config(config_name: str) -> str:
    """Get the value of a configuration variable."""
    if config_name in os.environ:
        return os.environ[config_name]
    else:
        raise ValueError(
            f"Configuration variable {config_name} not found. "
            "Please set it in the environment. To get your Spotify API credentials, "
            "see https://developer.spotify.com/documentation/web-api/tutorials/getting-started"
        )


def pop_client_id_and_secret(kwargs) -> tuple[str, str]:
    client_id = kwargs.pop('client_id', get_config('SPOTIFY_API_CLIENT_ID'))
    client_secret = kwargs.pop('client_secret', get_config('SPOTIFY_API_CLIENT_SECRET'))
    return client_id, client_secret


def get_spotify_creds(**client_creds_kwargs) -> SpotifyClientCredentials:
    client_id, client_secret = pop_client_id_and_secret(client_creds_kwargs)
    return SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret,
        **client_creds_kwargs,
    )


def get_spotify_oauth_creds(**oauth_kwargs) -> SpotifyOAuth:
    client_id, client_secret = pop_client_id_and_secret(oauth_kwargs)
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        **oauth_kwargs,
    )


def _extract_scope_items(scope_string: str) -> Iterable[str]:
    if isinstance(scope_string, str):
        return re.findall('\S+', scope_string)
    else:
        assert isinstance(scope_string, Iterable)
        return scope_string


def _add_to_scope(scope, more_scope=''):
    """
    Add new_scope to scope, ensuring no duplicates.

    Examples:

    >>> _add_to_scope('user-top-read', 'user-read-recently-played')  # note the lexicographic order in output
    'user-read-recently-played user-top-read'
    >>> _add_to_scope('user-top-read', 'user-read-recently-played user-top-read')  # note the absence of duplicates in output
    'user-read-recently-played user-top-read'
    """
    scope_items = set(_extract_scope_items(scope))
    scope_items.update(_extract_scope_items(more_scope))
    return ' '.join(sorted(scope_items))


# def get_spotify_client(client=None, *, ensure_scope=None, **kwargs) -> Spotify:
#     if ensure_scope is not None:
#         kwargs['scope'] = _add_to_scope(kwargs.get('scope', ''), ensure_scope)

#     spotify_kwargs = Sig(Spotify).map_arguments(
#         kwargs=kwargs, allow_partial=True, allow_excess=True
#     )
#     client_creds_kwargs = Sig(SpotifyClientCredentials).map_arguments(
#         kwargs=kwargs, allow_partial=True, allow_excess=True
#     )

#     if client is None:
#         return Spotify(
#             auth_manager=get_spotify_creds(**client_creds_kwargs),
#             **spotify_kwargs,
#         )
#     else:
#         # make a new client, with the updated kwargs
#         # extract the client_creds_kwargs and spotify_kwargs kwargs from client instance
#         # and update them with the new kwargs
#         # then create a new client with these updated kwargs
#         # return the new client

from i2 import Sig


spotify_client_sig = (
    Sig(Spotify)
    .merge_with_sig(Sig(SpotifyOAuth) - 'requests_timeout')
    .merge_with_sig(Sig(SpotifyClientCredentials) - 'requests_timeout')
)


@spotify_client_sig.inject_into_keyword_variadic
def get_spotify_client(client=None, *, ensure_scope='', scope='', **kwargs) -> Spotify:
    """
    Get a Spotify client.

    Parameters:
        - client - an existing Spotify client (optional)
        - ensure_scope - a scope to ensure is included in the client's auth_manager (optional)
        - scope - the scope to use for the client (optional)
        - **kwargs - additional arguments to pass to the Spotify client

    The purpose of having scope and ensure_scope is to allow you to ensure some needed
    scopes exist when a code block is asking for a Spotify client with it's own
    scope desires.

    """
    scope = _add_to_scope(kwargs.get('scope', ''), ensure_scope)
    kwargs['scope'] = scope

    spotify_kwargs = Sig(Spotify).map_arguments(
        kwargs=kwargs, allow_partial=True, allow_excess=True
    )

    if scope:
        client_creds_kwargs = Sig(SpotifyOAuth).map_arguments(
            kwargs=kwargs, allow_partial=True, allow_excess=True
        )
    else:
        client_creds_kwargs = Sig(SpotifyClientCredentials).map_arguments(
            kwargs=kwargs, allow_partial=True, allow_excess=True
        )

    if client is None:
        return Spotify(
            auth_manager=get_spotify_oauth_creds(**client_creds_kwargs),
            **spotify_kwargs,
        )
    else:
        # TODO: Should I use glom extractors here?
        # Extract existing spotify_kwargs from the client instance

        existing_spotify_kwargs = {
            'proxies': client.proxies,
            'requests_timeout': client.requests_timeout,
            'status_forcelist': client.status_forcelist,
            'retries': client.retries,
            'status_retries': client.status_retries,
            'backoff_factor': client.backoff_factor,
            'language': client.language,
            # 'chunked': client.chunked,
        }

        # Update existing spotify_kwargs with new spotify_kwargs
        spotify_kwargs = {**existing_spotify_kwargs, **spotify_kwargs}

        # Extract existing client_creds_kwargs from client.auth_manager
        existing_client_creds_kwargs = {}
        auth_manager = client.auth_manager

        if isinstance(auth_manager, SpotifyClientCredentials):
            existing_client_creds_kwargs = {
                'client_id': auth_manager.client_id,
                'client_secret': auth_manager.client_secret,
                'proxies': auth_manager.proxies,
                'requests_timeout': auth_manager.requests_timeout,
            }
        elif isinstance(auth_manager, SpotifyOAuth):
            existing_client_creds_kwargs = {
                'client_id': auth_manager.client_id,
                'client_secret': auth_manager.client_secret,
                'proxies': auth_manager.proxies,
                'requests_timeout': auth_manager.requests_timeout,
                'redirect_uri': auth_manager.redirect_uri,
                'scope': auth_manager.scope,
            }
        elif hasattr(auth_manager, 'client_id') and hasattr(
            auth_manager, 'client_secret'
        ):
            # For other auth managers that have client_id and client_secret
            existing_client_creds_kwargs = {
                'client_id': auth_manager.client_id,
                'client_secret': auth_manager.client_secret,
            }

        # Update existing client_creds_kwargs with new client_creds_kwargs
        client_creds_kwargs = {**existing_client_creds_kwargs, **client_creds_kwargs}

        # Create a new auth_manager with the updated client_creds_kwargs
        new_auth_manager = get_spotify_creds(**client_creds_kwargs)

        # Create a new Spotify client with the updated kwargs
        return Spotify(
            auth_manager=new_auth_manager,
            **spotify_kwargs,
        )


spotify_search_modifiers = {
    "album:": "Search within album titles.",
    "artist:": "Search within artist names.",
    "genre:": "Restrict search results to a specific genre. Example: genre:jazz.",
    "track:": "Search within track names.",
    "year:": "Filter by release year. Accepts ranges (e.g., year:2000-2020).",
    "tag:new": "Search for newly released songs.",
    "tag:hipster": "Search for music outside the mainstream (less popular).",
    "isrc:": "Search using the International Standard Recording Code.",
    "upc:": "Search using the Universal Product Code.",
}

spotify_scopes = {
    "ugc-image-upload": "Write access to user-provided images.",
    "user-read-playback-state": "Read access to a user’s player state.",
    "user-modify-playback-state": "Write access to a user’s playback state.",
    "user-read-currently-playing": "Read access to a user’s currently playing content.",
    "app-remote-control": "Remote control playback of Spotify (SDK use only).",
    "streaming": "Control playback of a Spotify track (requires Premium).",
    "playlist-read-private": "Read access to user's private playlists.",
    "playlist-read-collaborative": "Read access to collaborative playlists.",
    "playlist-modify-private": "Write access to user's private playlists.",
    "playlist-modify-public": "Write access to user's public playlists.",
    "user-follow-modify": "Write/delete access to user's followed artists and users.",
    "user-follow-read": "Read access to user's followed artists and users.",
    "user-read-playback-position": "Read access to user's playback position.",
    "user-top-read": "Read access to user's top artists and tracks.",
    "user-read-recently-played": "Read access to user's recently played tracks.",
    "user-library-modify": "Write/delete access to user's 'Your Music' library.",
    "user-library-read": "Read access to user's library.",
    "user-read-email": "Read access to user's email address.",
    "user-read-private": "Read access to user's subscription details.",
    "user-soa-link": "Link a partner user account to a Spotify user account.",
    "user-soa-unlink": "Unlink a partner user account from a Spotify account.",
    "soa-manage-entitlements": "Modify entitlements for linked users.",
    "soa-manage-partner": "Update partner information.",
    "soa-create-partner": "Create new partners (platform partners only).",
}


def ensure_client(client=None) -> Spotify:
    if client is None:
        return get_spotify_client()
    if callable(client):
        client_factory = client
        client = client_factory()
    return client


# Note here TrackId
TrackRef = str  # can be an id, a url, a uri, a href...
TrackId = str  # really, TrackId is a string with a specific format, but don't know how to specify that type
TrackKey = Union[TrackRef, int, slice, Iterable[TrackRef]]
TrackMetadata = Dict[str, Any]


# TODO: Maybe use dol.KeyTemplate to implement casting (and other parsing and generation)?
import dol

TrackKeyKinds = Literal["uri", "id", "url", "href"]


track_ref_patterns = {
    "uri": r"^spotify:track:[\w]{22}$",
    "id": r"^[\w]{22}$",
    "url": r"^https://open.spotify.com/track/[\w]{22}$",
    "href": r"^https://api.spotify.com/v1/tracks/[\w]{22}$",
}


def cast_track_key(
    track_key: TrackRef,
    target_kind: TrackKeyKinds = "uri",
    *,
    src_kind: Optional[TrackKeyKinds] = None,
) -> TrackRef:
    """
    Convert a Spotify track key between different formats.

    Parameters:
        - track_key - the track key to convert
        - target_kind - the format to convert to (one of 'uri', 'id', 'url', 'href')
        - src_kind - the format of the input track key (optional)

    Returns:
        The track key in the target format.


    Examples:

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

    """
    # Define possible patterns to detect the kind

    # Detect src_kind if not provided
    if src_kind is None:
        for kind, pattern in track_ref_patterns.items():
            if re.match(pattern, track_key):
                src_kind = kind
                break
        else:
            raise ValueError(
                f"Could not detect source kind for: {track_key=}"
                "Please specify a valid `src_kind`."
            )

    # Extract ID from the source format
    if src_kind == "uri":
        track_id = track_key.split(":")[-1]
    elif src_kind == "url" or src_kind == "href":
        track_id = track_key.split("/")[-1]
    elif src_kind == "id":
        track_id = track_key
    else:
        raise ValueError(f"Unsupported source kind: {src_kind}")

    # Convert to the target format
    if target_kind == "uri":
        return f"spotify:track:{track_id}"
    elif target_kind == "id":
        return track_id
    elif target_kind == "url":
        return f"https://open.spotify.com/track/{track_id}"
    elif target_kind == "href":
        return f"https://api.spotify.com/v1/tracks/{track_id}"
    else:
        raise ValueError(f"Unsupported target kind: {target_kind}")


ensure_track_id = partial(cast_track_key, target_kind="id")


# TODO: Make this complete
# TODO: Use dol.KeyTemplate to redo cast_track_key and the general playlist cast function
def ensure_playlist_id(playlist_spec: str) -> str:
    """
    Ensure that a playlist ID is in the correct format.

    Parameters:
        - playlist_id - the playlist ID to check

    Returns:
        The playlist ID in the correct format.

    Examples:

    >>> ensure_playlist_id("37i9dQZF1DXcBWIGoYBM5M")
    '37i9dQZF1DXcBWIGoYBM5M'
    >>> ensure_playlist_id("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M")
    '37i9dQZF1DXcBWIGoYBM5M'
    >>> ensure_playlist_id("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
    '37i9dQZF1DXcBWIGoYBM5M'
    >>> ensure_playlist_id("https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M")
    '37i9dQZF1DXcBWIGoYBM5M'
    """
    if playlist_spec.startswith('spotify:playlist:'):
        return playlist_spec.split(':')[-1]
    elif playlist_spec.startswith('https://'):
        return playlist_spec.split('/')[-1].split('?')[0]
    else:
        return (
            playlist_spec  # just cross your fingers and hope it's a valid playlist ID
        )


front_columns_for_track_metas = (
    'name',
    'first_artist',
    'duration_ms',
    'popularity',
    'explicit',
    'album_release_date',
    'album_release_year',
    'added_at_date',
    'url',
    'first_letter',
    'album_name',
    'id',
)


def move_columns_to_front(
    df: 'pd.DataFrame', columns: list[str], *, allow_excess=True
) -> 'pd.DataFrame':
    """
    Returns a copy of df with given columns in the front, in the order given.

    Parameters:
        - df - the DataFrame to modify
        - columns - the columns to move to the front
        - allow_excess - whether to allow columns not in the DataFrame (optional)

    Returns:
        The modified DataFrame.
    """
    if not allow_excess:
        assert set(columns) <= set(df.columns), "Columns not in DataFrame"
    columns = [col for col in columns if col in df.columns]
    return df[columns + [col for col in df.columns if col not in columns]]
