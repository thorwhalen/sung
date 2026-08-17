"""Pytest configuration for the sung test suite.

Most of ``sung`` is credential-free: chord/lyric parsing, track-key casting,
song-descriptor parsing and dataframe shaping all run without ever talking to
Spotify. Those tests always run.

A small layer genuinely needs the live Spotify Web API. Those tests carry the
``spotify`` marker and are **deselected** -- not skipped -- when the backend is
unavailable. The distinction matters: a skipped test still shows up in a
"passed" run, so a suite that silently stopped exercising anything still reads
as green. A deselected item is reported as deselected, and the count of tests
that actually ran drops visibly.

"Available" is checked by *obtaining a token*, not merely by finding the
environment variables set. An env-var check would call a revoked or typo'd
credential "available" and turn a dead secret into a red build; asking the
token endpoint answers the question that the tests actually depend on.

Set ``SUNG_TEST_NO_SPOTIFY=1`` to force the Spotify layer off (useful for a
deterministic, network-free local run even when credentials are present).
"""

import os
from functools import lru_cache

SPOTIFY_MARKER = "spotify"

# Credentials sung itself reads (see sung.util.pop_client_id_and_secret).
CREDENTIAL_ENVVARS = ("SPOTIFY_API_CLIENT_ID", "SPOTIFY_API_CLIENT_SECRET")

# Opt-out switch: force the Spotify layer to be treated as unavailable.
DISABLE_ENVVAR = "SUNG_TEST_NO_SPOTIFY"

TOKEN_URL = "https://accounts.spotify.com/api/token"
TOKEN_REQUEST_TIMEOUT = 10  # seconds


@lru_cache(maxsize=1)
def spotify_availability() -> tuple:
    """Return ``(available, reason)`` for the live Spotify Web API.

    Cached, so the token request happens at most once per test session.
    """
    if os.environ.get(DISABLE_ENVVAR):
        return False, f"{DISABLE_ENVVAR} is set"

    missing = [name for name in CREDENTIAL_ENVVARS if not os.environ.get(name)]
    if missing:
        return False, "credentials not set: " + ", ".join(missing)

    try:
        import requests
    except ImportError:  # pragma: no cover - requests is a declared dependency
        return False, "requests is not installed"

    try:
        response = requests.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(
                os.environ["SPOTIFY_API_CLIENT_ID"],
                os.environ["SPOTIFY_API_CLIENT_SECRET"],
            ),
            timeout=TOKEN_REQUEST_TIMEOUT,
        )
    except Exception as error:
        return False, f"token request failed: {type(error).__name__}"

    if response.status_code != 200:
        return False, f"token endpoint returned HTTP {response.status_code}"
    if not response.json().get("access_token"):
        return False, "token endpoint returned no access_token"

    return True, "client-credentials token obtained"


def pytest_configure(config):
    """Register the ``spotify`` marker so ``--strict-markers`` runs stay clean."""
    config.addinivalue_line(
        "markers",
        f"{SPOTIFY_MARKER}: requires a reachable Spotify Web API "
        "(deselected when unavailable)",
    )


def pytest_collection_modifyitems(config, items):
    """Deselect ``spotify``-marked items when the live backend is unavailable.

    Deselection (rather than skipping) keeps an unavailable backend visible in
    the run summary instead of hiding it inside the passed count.
    """
    available, reason = spotify_availability()
    if available:
        return

    kept, deselected = [], []
    for item in items:
        target = deselected if item.get_closest_marker(SPOTIFY_MARKER) else kept
        target.append(item)

    if not deselected:
        return

    config.hook.pytest_deselected(items=deselected)
    items[:] = kept

    reporter = config.pluginmanager.get_plugin("terminalreporter")
    if reporter is not None:
        reporter.write_line(
            f"sung: deselected {len(deselected)} Spotify-dependent test(s) -- {reason}"
        )
