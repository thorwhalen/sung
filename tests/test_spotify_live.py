"""Tests that genuinely need the live Spotify Web API.

Every test here carries the ``spotify`` marker, so ``conftest.py`` deselects
the whole module when no working credential is available (see its docstring for
why deselect and not skip).

These tests build their own **client-credentials** client and pass it in
explicitly. They do not go through ``sung.util.get_spotify_client``, which
builds an *OAuth* auth manager and would open a browser consent prompt -- the
exact reason this repo's CI had its pytest step commented out. Client
credentials cover the read-only surface (search, track lookup) with no user
interaction; anything requiring a user token (creating or deleting playlists,
reading a user's top tracks) stays out of the automated suite because it
mutates a real account.
"""

import os

import pytest

pytestmark = pytest.mark.spotify


@pytest.fixture(scope="module")
def client():
    """A non-interactive, read-only Spotify client.

    ``cache_handler=MemoryCacheHandler()`` is not optional. spotipy's default
    caches the access token in a ``.cache`` file in the working directory and
    reuses it *regardless of the client id and secret it was handed* -- so on a
    developer machine that has ever authenticated, these tests pass with
    deliberately wrong credentials. That makes the whole availability gate
    unfalsifiable locally. An in-memory cache forces a real token exchange with
    the credentials actually supplied, and leaves no file behind.
    """
    from spotipy import Spotify
    from spotipy.cache_handler import MemoryCacheHandler
    from spotipy.oauth2 import SpotifyClientCredentials

    return Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=os.environ["SPOTIFY_API_CLIENT_ID"],
            client_secret=os.environ["SPOTIFY_API_CLIENT_SECRET"],
            cache_handler=MemoryCacheHandler(),
        )
    )


def test_search_tracks_returns_track_objects(client):
    from sung.base import search_tracks

    results = search_tracks(query="Clocks Coldplay", limit=3, client=client)
    assert results, "live search returned no tracks"
    for track in results:
        assert track["type"] == "track"
        assert isinstance(track["id"], str)
        assert track["artists"]


def test_tracks_search_builds_a_usable_mapping(client):
    """The offline Mapping contract must hold over live data too."""
    from sung.base import Tracks

    tracks = Tracks.search(query="Coldplay", limit=3, client=client)
    assert 0 < len(tracks) <= 3
    ids = list(tracks)
    assert all(isinstance(track_id, str) for track_id in ids)
    assert tracks[ids[0]]["id"] == ids[0]

    df = tracks.meta_dataframe()
    assert list(df.index) == ids
    for column in ("name", "artists_names", "album_release_year"):
        assert column in df.columns
