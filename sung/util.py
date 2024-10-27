"""Utility functions for the sung package."""

# TODO: use openAPI definition to create pydantic models for data
#  see https://github.com/thorwhalen/sung/discussions/1#discussioncomment-10990012


import re
import os
from typing import Literal, T, Callable, TypeVar, Optional
from functools import partial

from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from glom import glom, Spec

from i2 import Sig

DFLT_LIMIT = 20

# TODO: Get automatically from pydantic model when available
SearchTypeT = Literal['artist', 'album', 'track', 'playlist', 'show', 'episode']


def identity(x: T) -> T:
    return x


Extractor = TypeVar('Extractor', bound=Callable)  # TODO: Specify more precisely


def extractor(spec: Spec) -> Extractor:
    return partial(glom, spec=spec)


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


def get_spotify_client(**kwargs) -> Spotify:
    spotify_kwargs = Sig(Spotify).map_arguments(
        kwargs=kwargs, allow_partial=True, allow_excess=True
    )
    client_creds_kwargs = Sig(SpotifyClientCredentials).map_arguments(
        kwargs=kwargs, allow_partial=True, allow_excess=True
    )
    return Spotify(
        auth_manager=get_spotify_creds(**client_creds_kwargs),
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


TrackKeyKinds = Literal["uri", "id", "url", "href"]


def cast_track_key(
    track_key,
    target_kind: TrackKeyKinds = "uri",
    *,
    src_kind: Optional[TrackKeyKinds] = None,
):
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
    patterns = {
        "uri": r"^spotify:track:[\w]{22}$",
        "id": r"^[\w]{22}$",
        "url": r"^https://open.spotify.com/track/[\w]{22}$",
        "href": r"^https://api.spotify.com/v1/tracks/[\w]{22}$",
    }

    # Detect src_kind if not provided
    if src_kind is None:
        for kind, pattern in patterns.items():
            if re.match(pattern, track_key):
                src_kind = kind
                break
        else:
            raise ValueError(
                "Could not detect source kind. Please specify a valid `src_kind`."
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
