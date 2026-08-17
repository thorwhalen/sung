"""Smoke tests: importing the package shouldn't blow up, and shouldn't need credentials.

The second half of that sentence is the point. ``sung`` is a Spotify client
library, so the cheapest way for it to become untestable is for an import to
reach for a credential. These tests pin the boundary: the whole public surface
must be importable with an empty environment.
"""

import os

import pytest


def test_import():
    import sung  # noqa: F401


def test_public_surface_is_importable():
    """Every name re-exported by ``sung/__init__.py`` resolves."""
    import sung

    expected = {
        "search_tracks",
        "Tracks",
        "PlaylistReader",
        "Playlist",
        "extract_extra_metadata",
        "df_extract_extra_metadata",
        "SpotifyDacc",
        "delete_playlist",
        "extractor",
        "cast_track_key",
        "ensure_track_id",
        "get_spotify_client",
        "ensure_playlist_id",
        "TracksAnalysis",
        "render_chords_and_lyrics",
        "search_songs",
        "remove_non_lyrics",
        "pack_song_text",
        "parse_song_descriptor",
        "resolve_song",
        "resolve_songs",
        "playlist_from_songs",
        "SongMatch",
    }
    missing = sorted(name for name in expected if not hasattr(sung, name))
    assert not missing, f"sung no longer exports: {missing}"


def test_submodules_import_without_credentials():
    """Importing any submodule must not read Spotify credentials.

    A module-level credential read would make the package unimportable on any
    machine without a Spotify app -- including CI and any downstream consumer
    that only wants the chord/lyric tooling.

    Run in a subprocess with the credentials stripped from the environment: an
    in-process ``importlib.reload`` would rebind module globals and leave every
    other test holding stale function objects.
    """
    import subprocess
    import sys

    module_names = (
        "sung",
        "sung.util",
        "sung.base",
        "sung.tools",
        "sung.playlists",
        "sung.chords_and_lyrics",
    )
    script = (
        "import importlib\n"
        f"for name in {module_names!r}:\n"
        "    module = importlib.import_module(name)\n"
        "    assert module.__doc__, name + ' has no module docstring'\n"
        "print('ok')\n"
    )
    env = {
        k: v for k, v in os.environ.items() if not k.startswith(("SPOTIFY", "SPOTIPY"))
    }
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().endswith("ok")


def test_get_config_raises_informative_error_when_unset(monkeypatch):
    """A missing credential must fail loudly, with a pointer to the fix."""
    from sung.util import get_config

    monkeypatch.delenv("SUNG_DEFINITELY_NOT_SET", raising=False)
    with pytest.raises(ValueError) as excinfo:
        get_config("SUNG_DEFINITELY_NOT_SET")
    message = str(excinfo.value)
    assert "SUNG_DEFINITELY_NOT_SET" in message
    assert "developer.spotify.com" in message


def test_get_config_reads_environment(monkeypatch):
    from sung.util import get_config

    monkeypatch.setenv("SUNG_TEST_CONFIG_VALUE", "hello")
    assert get_config("SUNG_TEST_CONFIG_VALUE") == "hello"
    assert os.environ["SUNG_TEST_CONFIG_VALUE"] == "hello"
