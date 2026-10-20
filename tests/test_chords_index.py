"""The chords-and-lyrics index: build, read back, and stay stdlib-only (thorwhalen/sung#17).

Synthetic rows only: no song text from the real corpus goes in the repo.
"""

import math
import os
import sqlite3
import subprocess
import sys

import pytest

from sung import chords_index as ci

ROWS = [
    (10, "The Band", "Paper Boats", "G   C\nPaper boats drift_away", "en", 3),
    (11, "Àrtist", "Quiet Road", "Am\nquiet road été", "fr", 1.5),
    (12, float("nan"), None, float("nan"), "en", float("nan")),
]


@pytest.fixture
def index(tmp_path):
    path = str(tmp_path / ci.INDEX_NAME)
    report = ci.build_chords_index(path, rows=ROWS, batch_size=2)
    assert report["songs"] == len(ROWS) and report["path"] == path
    return path


def test_columns_are_in_row_order_with_missing_values_blank(index):
    columns = ci.read_columns(index)
    assert list(columns) == list(ci.COLUMN_NAMES)
    assert columns["ids"] == ["10", "11", "12"]
    assert columns["titles"] == ["Paper Boats", "Quiet Road", ""]
    assert columns["artists"] == ["The Band", "Àrtist", ""]
    assert columns["langs"] == ["en", "fr", "en"]
    assert columns["popularity"] == [3.0, 1.5, 0.0]


def test_words_match_whole_tokens_any_case(index):
    assert ci.rows_with_words(index, ["PAPER", "boats"]) == [0]
    assert ci.rows_with_words(index, ["drift"]) == [0]  # "_" separates words
    assert ci.rows_with_words(index, ["été"]) == [1]  # accents kept
    assert ci.rows_with_words(index, ["ete"]) == []
    assert ci.rows_with_words(index, ["boat"]) == []  # whole words only
    assert ci.rows_with_words(index, ['quote"d']) == []  # quotes are escaped
    assert ci.rows_with_words(index, []) == []


def test_charts_round_trip(index):
    assert ci.read_chart(index, 1) == ROWS[1][3]
    assert ci.read_chart(index, 2) == ""  # a non-text chart is stored empty
    assert ci.read_chart(index, 99) == ""
    assert ci.read_meta(index)["songs"] == "3"


def test_schema_is_songleafs(index):
    """Files songleaf built before the move must stay readable: same tables and columns."""
    with ci.connect(index) as conn:
        columns = [r[1] for r in conn.execute("PRAGMA table_info(songs)")]
    assert columns == ["row", "id", "title", "artist", "lang", "popularity", "chart"]


def test_empty_index(tmp_path):
    path = str(tmp_path / "empty.sqlite")
    assert ci.build_chords_index(path, rows=[])["songs"] == 0
    assert ci.read_columns(path) == {name: [] for name in ci.COLUMN_NAMES}


def test_a_failed_build_leaves_the_old_index_and_no_scraps(index):
    before = ci.index_version(index)

    def broken():
        yield ROWS[0]
        raise RuntimeError("corpus read failed")

    with pytest.raises(RuntimeError):
        ci.build_chords_index(index, rows=broken())
    assert ci.index_version(index) == before
    assert os.listdir(os.path.dirname(index)) == [ci.INDEX_NAME]


def test_reads_are_read_only(index):
    with ci.connect(index) as conn, pytest.raises(sqlite3.OperationalError):
        conn.execute("DELETE FROM songs")


def test_missing_index_is_a_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        ci.read_columns(str(tmp_path / "nope.sqlite"))
    assert ci.index_version(str(tmp_path / "nope.sqlite")) is None


def test_dataframe_rows_take_the_corpus_columns():
    class Frame(
        dict
    ):  # the one DataFrame method dataframe_rows uses: df[name].tolist()
        def __getitem__(self, name):
            values = dict.__getitem__(self, name)
            return type("Col", (), {"tolist": lambda self: list(values)})()

    frame = Frame({name: [i, i + 1] for i, name in enumerate(ci.CORPUS_COLUMNS)})
    assert list(ci.dataframe_rows(frame)) == [(0, 1, 2, 3, 4, 5), (1, 2, 3, 4, 5, 6)]


def test_local_index_from_env_and_beside_the_zip(tmp_path, monkeypatch):
    monkeypatch.delenv(ci.CHORDS_INDEX_ENVVAR, raising=False)
    zip_path = tmp_path / "corpus.zip"
    zip_path.write_bytes(b"")
    monkeypatch.setenv("SUNG_CHORDS_AND_LYRICS_ZIP", str(zip_path))
    assert ci.local_chords_index() is None
    beside = tmp_path / ci.INDEX_NAME
    ci.build_chords_index(str(beside), rows=ROWS[:1])
    assert ci.local_chords_index() == str(beside)
    monkeypatch.setenv(ci.CHORDS_INDEX_ENVVAR, str(tmp_path / "missing.sqlite"))
    with pytest.raises(FileNotFoundError):
        ci.local_chords_index()


def test_finding_and_importing_the_index_load_only_the_standard_library():
    script = (
        "import sys\n"
        "import sung.chords_index as ci\n"
        "ci.local_chords_index()\n"
        "print(sorted({'pandas', 'pydantic', 'reportlab', 'spotipy'} & set(sys.modules)))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "[]"


def test_nan_helpers():
    assert ci._text_or_empty(math.nan) == "" and ci._number_or_zero("x") == 0.0


def test_bad_arguments_fail_loudly(index, tmp_path):
    with pytest.raises(ValueError):
        ci.build_chords_index(str(tmp_path / "x.sqlite"), rows=ROWS, batch_size=0)
    with pytest.raises(TypeError):
        ci.rows_with_words(index, "boats")
