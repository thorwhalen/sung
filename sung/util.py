"""Utility functions for the sung package."""

# TODO: use openAPI definition to create pydantic models for data
#  see https://github.com/thorwhalen/sung/discussions/1#discussioncomment-10990012

from typing import Literal, T, Callable, TypeVar
from functools import partial
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from glom import glom, Spec

import os

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


def get_spotify_client() -> Spotify:
    return Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=get_config('SPOTIFY_API_CLIENT_ID'),
            client_secret=get_config('SPOTIFY_API_CLIENT_SECRET'),
        )
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


def ensure_client(client) -> Spotify:
    if callable(client):
        client_factory = client
        client = client_factory()
    return client
