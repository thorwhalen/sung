"""Tests for the credential-free casting/shaping layer of :mod:`sung.base`.

``Tracks`` only calls Spotify when it is constructed from ids *and* asked for
metadata. Constructed from metadata it is a pure ``Mapping``, so the whole
key-casting, indexing and dataframe-shaping surface is testable offline. Every
test here passes a sentinel client, which makes any accidental network call an
``AttributeError`` rather than a silent live request.
"""

import pandas as pd
import pytest

from sung.base import (
    Tracks,
    extract_extra_metadata,
    process_track_columns,
    track_metas_to_track_ids,
)

TRACK_ID_1 = "4iV5W9uYEdYUVa79Axb7Rh"
TRACK_ID_2 = "1vrd6UOGamcKNGnSHJQlSt"


class NoClient:
    """A stand-in client that fails loudly if anything tries to use it."""

    def __getattr__(self, name):
        raise AssertionError(f"unexpected Spotify call: client.{name}")


def track_meta(
    track_id, name, artists, *, album="Some Album", release_date="2001-05-03"
):
    """Build a track metadata dict shaped like Spotify's track object."""
    return {
        "id": track_id,
        "name": name,
        "popularity": 50,
        "duration_ms": 210_000,
        "explicit": False,
        "track_number": 1,
        "type": "track",
        "uri": f"spotify:track:{track_id}",
        "artists": [{"name": artist} for artist in artists],
        "album": {
            "name": album,
            "release_date": release_date,
            "total_tracks": 10,
            "images": [],
        },
        "external_urls": {"spotify": f"https://open.spotify.com/track/{track_id}"},
    }


@pytest.fixture
def metas():
    return [
        track_meta(TRACK_ID_1, "Song One", ["Alice", "Bob"]),
        track_meta(TRACK_ID_2, "Song Two", ["Carol"], release_date="1999"),
    ]


@pytest.fixture
def tracks(metas):
    return Tracks(metas, client=NoClient())


# ---------------------------------------------------------------------------
# Extraction


def test_extract_extra_metadata_flattens_nested_fields(metas):
    extracted = extract_extra_metadata(metas[0])
    assert extracted["artist_list"] == ["Alice", "Bob"]
    assert extracted["first_artist"] == "Alice"
    assert extracted["album_name"] == "Some Album"
    assert extracted["album_release_date"] == "2001-05-03"
    assert extracted["url"] == f"https://open.spotify.com/track/{TRACK_ID_1}"


def test_track_metas_to_track_ids(metas):
    assert track_metas_to_track_ids(metas) == [TRACK_ID_1, TRACK_ID_2]


# ---------------------------------------------------------------------------
# Tracks as a Mapping


def test_tracks_is_a_mapping(tracks):
    assert len(tracks) == 2
    assert list(tracks) == [TRACK_ID_1, TRACK_ID_2]
    assert TRACK_ID_1 in tracks
    assert "not-a-real-track-id" not in tracks
    assert tracks[TRACK_ID_1]["name"] == "Song One"


def test_tracks_accepts_any_reference_form_and_normalizes_to_ids():
    """Mixed uri/url/id input must become a uniform id keyspace.

    Without normalization, ``tracks[some_url]`` and ``tracks[same_id]`` would
    be different keys for the same track.
    """
    tracks = Tracks(
        [
            f"spotify:track:{TRACK_ID_1}",
            f"https://open.spotify.com/track/{TRACK_ID_2}",
        ],
        client=NoClient(),
    )
    assert list(tracks) == [TRACK_ID_1, TRACK_ID_2]


def test_tracks_getitem_by_position_and_slice(tracks):
    assert tracks[0]["name"] == "Song One"
    assert tracks[-1]["name"] == "Song Two"
    assert [t["name"] for t in tracks[0:2]] == ["Song One", "Song Two"]
    assert [t["name"] for t in tracks[[TRACK_ID_2]]] == ["Song Two"]


def test_tracks_getitem_raises_on_unknown_key_and_bad_type(tracks):
    with pytest.raises(KeyError):
        tracks["not-a-real-track-id"]
    with pytest.raises(KeyError):
        tracks[[TRACK_ID_1, "not-a-real-track-id"]]
    with pytest.raises(TypeError):
        tracks[1.5]


def test_tracks_from_metadata_never_calls_the_client(metas):
    """Metadata in, metadata out -- no request may be issued."""
    tracks = Tracks(metas, client=NoClient())
    assert tracks.track_metas == metas  # would raise AssertionError on a call


# ---------------------------------------------------------------------------
# Dataframe shaping


def test_process_track_columns_adds_derived_columns(metas):
    df = pd.DataFrame(metas)
    processed = process_track_columns(df)
    assert list(processed["artists_names"]) == ["Alice; Bob", "Carol"]
    assert list(processed["album_release_year"]) == [2001, 1999]


def test_process_track_columns_normalizes_year_only_release_dates(metas):
    """A year-only ``release_date`` must still yield an integer year.

    ``album_release_year`` is cast to ``int``; without ``convert_date`` first,
    a bare ``"1999"`` would slice to ``"1999"`` here but a ``"1999-05"`` would
    slice to ``"1999"`` too -- the normalization is what keeps every precision
    on the same footing.
    """
    df = pd.DataFrame(
        [
            track_meta(TRACK_ID_1, "A", ["X"], release_date="1999"),
            track_meta(TRACK_ID_2, "B", ["Y"], release_date="2003-07"),
        ]
    )
    processed = process_track_columns(df)
    assert list(processed["album_release_year"]) == [1999, 2003]
    assert list(processed["album_release_date"]) == ["1999-01-01", "2003-07-01"]


def test_process_track_columns_rejects_duplicate_columns(metas):
    """Re-processing an already-processed frame must fail loudly, not overwrite."""
    df = process_track_columns(pd.DataFrame(metas))
    with pytest.raises(ValueError, match="duplicated"):
        process_track_columns(df)


def test_meta_dataframe_is_indexed_by_track_id_with_front_columns(tracks):
    df = tracks.meta_dataframe()
    assert list(df.index) == [TRACK_ID_1, TRACK_ID_2]
    assert df.columns[0] == "name"
    # 'id' is kept as a column as well as being the index
    assert "id" in df.columns
    # back columns really are at the back
    assert list(df.columns)[-1] == "external_urls"


def test_front_columns_are_actual_column_names(tracks):
    """Every entry of ``front_columns_for_track_metas`` must be a real column.

    A missing comma in that tuple silently concatenated two adjacent names
    into one entry that matched nothing, so both columns stayed buried in the
    middle of the frame -- with no error anywhere, because ``allow_excess``
    drops unknown names.
    """
    from sung.util import front_columns_for_track_metas

    df = tracks.meta_dataframe()
    matched = [c for c in front_columns_for_track_metas if c in df.columns]
    assert list(df.columns)[: len(matched)] == matched
    assert "artists_names" in matched
    assert "duration_ms" in matched


def test_dataframe_alias_is_meta_dataframe():
    assert Tracks.dataframe is Tracks.meta_dataframe
