"""Tests for the credential-free helpers in :mod:`sung.util`.

Everything here is pure logic: key casting, date normalization, OAuth-scope
arithmetic, glom extractor construction and dataframe column ordering. None of
it touches the network.
"""

import pandas as pd
import pytest

from sung.util import (
    _add_to_scope,
    _extract_scope_items,
    cast_track_key,
    convert_date,
    ensure_extractor,
    ensure_playlist_id,
    ensure_track_id,
    extractor,
    identity,
    is_extractor,
    move_columns_to_back,
    move_columns_to_front,
    strip_values,
    track_ref_patterns,
)

TRACK_ID = "4iV5W9uYEdYUVa79Axb7Rh"

# ---------------------------------------------------------------------------
# Track key casting


@pytest.mark.parametrize(
    "target_kind,expected",
    [
        ("id", TRACK_ID),
        ("uri", f"spotify:track:{TRACK_ID}"),
        ("url", f"https://open.spotify.com/track/{TRACK_ID}"),
        ("href", f"https://api.spotify.com/v1/tracks/{TRACK_ID}"),
    ],
)
@pytest.mark.parametrize(
    "source",
    [
        TRACK_ID,
        f"spotify:track:{TRACK_ID}",
        f"https://open.spotify.com/track/{TRACK_ID}",
        f"https://api.spotify.com/v1/tracks/{TRACK_ID}",
    ],
)
def test_cast_track_key_is_total_over_known_kinds(source, target_kind, expected):
    """Every source form converts to every target form, and round-trips."""
    assert cast_track_key(source, target_kind) == expected


def test_cast_track_key_defaults_to_uri():
    assert cast_track_key(TRACK_ID) == f"spotify:track:{TRACK_ID}"


def test_ensure_track_id_normalizes_any_reference():
    for source in (
        TRACK_ID,
        f"spotify:track:{TRACK_ID}",
        f"https://open.spotify.com/track/{TRACK_ID}",
    ):
        assert ensure_track_id(source) == TRACK_ID


def test_cast_track_key_rejects_unrecognized_source():
    """An unparseable reference must raise, not silently pass through.

    Silently returning the input would push a malformed id all the way to a
    Spotify request, where the failure is far harder to trace.
    """
    with pytest.raises(ValueError, match="Could not detect source kind"):
        cast_track_key("not-a-track-reference")


def test_cast_track_key_rejects_unknown_target_kind():
    with pytest.raises(ValueError, match="Unsupported target kind"):
        cast_track_key(TRACK_ID, "playlist")


def test_track_ref_patterns_are_anchored():
    """Patterns must be anchored, else a 22-char id embedded in junk matches."""
    import re

    for kind, pattern in track_ref_patterns.items():
        assert pattern.startswith("^") and pattern.endswith("$"), kind
        assert not re.match(pattern, f"junk-{TRACK_ID}-junk"), kind


# ---------------------------------------------------------------------------
# Playlist ids


@pytest.mark.parametrize(
    "spec",
    [
        "37i9dQZF1DXcBWIGoYBM5M",
        "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
        "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
        "https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M",
    ],
)
def test_ensure_playlist_id(spec):
    assert ensure_playlist_id(spec) == "37i9dQZF1DXcBWIGoYBM5M"


def test_ensure_playlist_id_strips_share_query_string():
    """Spotify "copy link" URLs carry a ``?si=`` tracking parameter.

    Leaving it on produces a 404 from the API, so the strip is load-bearing.
    """
    url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=d6e0c7bc8f59"
    assert ensure_playlist_id(url) == "37i9dQZF1DXcBWIGoYBM5M"


# ---------------------------------------------------------------------------
# Dates


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("2020-05-03", "2020-05-03"),
        ("2020-05", "2020-05-01"),
        ("2020", "2020-01-01"),
    ],
)
def test_convert_date_normalizes_spotify_release_precisions(raw, expected):
    """Spotify returns year / year-month / full dates; all must normalize."""
    assert convert_date(raw) == expected


def test_convert_date_passes_through_unparseable_and_none():
    assert convert_date(None) is None
    assert convert_date("sometime in the 90s") == "sometime in the 90s"


# ---------------------------------------------------------------------------
# Scopes


def test_extract_scope_items_splits_on_any_whitespace():
    assert _extract_scope_items("a  b\tc") == ["a", "b", "c"]
    assert _extract_scope_items(["a", "b"]) == ["a", "b"]


def test_add_to_scope_deduplicates_and_sorts():
    assert (
        _add_to_scope("user-top-read", "user-read-recently-played user-top-read")
        == "user-read-recently-played user-top-read"
    )


def test_add_to_scope_is_idempotent():
    """Repeated widening must not grow the scope string.

    ``get_spotify_client`` calls this on every request that wants a scope; a
    non-idempotent merge would accumulate duplicates request after request.
    """
    scope = _add_to_scope("user-top-read", "playlist-modify-public")
    assert _add_to_scope(scope, "playlist-modify-public") == scope


def test_add_to_scope_with_empty_addition():
    assert _add_to_scope("user-top-read", "") == "user-top-read"
    assert _add_to_scope("", "") == ""


# ---------------------------------------------------------------------------
# Extractors


def test_extractor_from_string_spec_defaults_to_none():
    extract = extractor("album.name")
    assert extract({"album": {"name": "Parachutes"}}) == "Parachutes"
    assert extract({"album": {}}) is None


def test_extractor_from_iterable_spec_builds_identity_mapping():
    extract = extractor(["name", "id"])
    assert extract({"name": "Clocks", "id": "x"}) == {"name": "Clocks", "id": "x"}


def test_extractor_from_mapping_spec_tolerates_missing_paths():
    """A missing path yields ``None`` rather than raising.

    Spotify omits fields routinely (no preview url, no album images); a strict
    extractor would make a whole dataframe build fail on one sparse track.
    """
    extract = extractor({"artist": "artists.0.name", "missing": "nope.nothing"})
    assert extract({"artists": [{"name": "Coldplay"}]}) == {
        "artist": "Coldplay",
        "missing": None,
    }


def test_is_extractor_and_ensure_extractor():
    extract = extractor("name")
    assert is_extractor(extract)
    assert is_extractor(identity)
    assert not is_extractor("name")

    assert ensure_extractor(None) is identity
    assert ensure_extractor(extract) is extract
    assert ensure_extractor("name")({"name": "Clocks"}) == "Clocks"


def test_strip_values():
    assert strip_values({"a": "  x  ", "b": "y "}) == {"a": "x", "b": "y"}


# ---------------------------------------------------------------------------
# Column ordering


def test_move_columns_to_front_preserves_requested_order():
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
    assert list(move_columns_to_front(df, ["c", "b"]).columns) == ["c", "b", "a"]


def test_move_columns_to_back_preserves_requested_order():
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
    assert list(move_columns_to_back(df, ["a", "b"]).columns) == ["c", "a", "b"]


def test_move_columns_tolerates_absent_columns_by_default():
    """The default column lists name fields Spotify does not always return."""
    df = pd.DataFrame({"a": [1], "b": [2]})
    assert list(move_columns_to_front(df, ["b", "not_there"]).columns) == ["b", "a"]
    assert list(move_columns_to_back(df, ["a", "not_there"]).columns) == ["b", "a"]


def test_move_columns_can_be_strict():
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(AssertionError):
        move_columns_to_front(df, ["not_there"], allow_excess=False)
    with pytest.raises(AssertionError):
        move_columns_to_back(df, ["not_there"], allow_excess=False)


def test_move_columns_does_not_lose_columns():
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
    for moved in (
        move_columns_to_front(df, ["c"]),
        move_columns_to_back(df, ["a"]),
    ):
        assert set(moved.columns) == set(df.columns)
        assert len(moved) == len(df)
