"""A SQLite + FTS5 index of the chords-and-lyrics corpus, read without the corpus in memory.

The corpus (:func:`sung.chords_and_lyrics.get_lyrics_and_chords_dataset`) is a
~650 MB CSV: as a DataFrame it costs about 1.1 GB per process. This module
writes it once to one SQLite file (titles, artists, language, popularity, each
chart zlib-compressed, and an FTS5 table of the charts' words) and reads that
file back piecemeal: the short columns for matching, the words for lyrics
search, one chart at a time.

It imports only the standard library, so a web worker that serves from the
index never loads pandas (thorwhalen/sung#17). Building it does load the corpus
(through pandas), so run :func:`build_chords_index` once, apart from any server.
Ranking and fuzzy matching are the consumer's business (``songleaf``,
``scoreseek``); this module only stores and fetches.

>>> import os, tempfile
>>> rows = [
...     (1, "The Band", "Paper Boats", "G\\nPaper boats drift", "en", 3),
...     (2, "Other", "Quiet Road", "C\\nquiet road", "en", 1),
... ]
>>> path = os.path.join(tempfile.mkdtemp(), INDEX_NAME)
>>> build_chords_index(path, rows=rows)["songs"]
2
>>> read_columns(path)["titles"]
['Paper Boats', 'Quiet Road']
>>> rows_with_words(path, ["boats"])
[0]
>>> print(read_chart(path, 0))
G
Paper boats drift
"""

from __future__ import annotations

import os
import sqlite3
import time
import zlib
from collections.abc import Iterable
from contextlib import closing
from itertools import islice
from pathlib import Path

CHORDS_AND_LYRICS_DATASET = "eitanbentora/chords-and-lyrics-dataset"
CHORDS_AND_LYRICS_CSV = "chords_and_lyrics.csv"
#: Environment variable naming a local copy of the corpus zip.
CHORDS_AND_LYRICS_ZIP_ENVVAR = "SUNG_CHORDS_AND_LYRICS_ZIP"


def local_chords_and_lyrics_zip():
    """Return the path of a local copy of the chords-and-lyrics zip, or ``None``.

    Looks at ``$SUNG_CHORDS_AND_LYRICS_ZIP`` first, then at where ``haggle``
    keeps its downloads (``$HAGGLE_ROOTDIR/zips/<owner>/<dataset>.zip``, root
    defaulting to ``~/haggle``). The haggle layout is replicated rather than
    asked of haggle, because importing haggle imports ``kaggle``, which
    authenticates against Kaggle at import time, even for a cached file.
    """
    explicit = os.environ.get(CHORDS_AND_LYRICS_ZIP_ENVVAR)
    if explicit:
        path = os.path.expanduser(explicit)
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"${CHORDS_AND_LYRICS_ZIP_ENVVAR} names {path}, which is not a file"
            )
        return path
    haggle_root = os.environ.get("HAGGLE_ROOTDIR", os.path.expanduser("~/haggle"))
    owner, dataset = CHORDS_AND_LYRICS_DATASET.split("/")
    path = os.path.join(haggle_root, "zips", owner, f"{dataset}.zip")
    return path if os.path.isfile(path) else None


#: The index's file name; it lives beside the corpus zip by convention.
INDEX_NAME = "chords-and-lyrics.sqlite"
#: Environment variable naming the index file.
CHORDS_INDEX_ENVVAR = "SUNG_CHORDS_INDEX"
#: The corpus columns the index is built from, in the order ``rows`` gives them:
#: song id, artist, title, chart (chords over lyrics), language, popularity.
CORPUS_COLUMNS = (
    "Unnamed: 0",
    "artist_name",
    "song_name",
    "chords&lyrics",
    "lang",
    "popularity",
)
#: What :func:`read_columns` returns, in row order.
COLUMN_NAMES = ("ids", "titles", "artists", "langs", "popularity")

# Unchanged from songleaf's ``kaggle_index``, so the index files it built stay valid.
SCHEMA = """
CREATE TABLE songs (
    row INTEGER PRIMARY KEY,
    id TEXT NOT NULL,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    lang TEXT NOT NULL,
    popularity REAL NOT NULL,
    chart BLOB NOT NULL
);
CREATE VIRTUAL TABLE chart_words USING fts5(
    chart, content='', tokenize='unicode61 remove_diacritics 0'
);
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def local_chords_index():
    """Return the path of a local index file, or ``None``.

    ``$SUNG_CHORDS_INDEX`` first (an error if it names no file), then
    :data:`INDEX_NAME` beside the local corpus zip
    (:func:`local_chords_and_lyrics_zip`). An index kept elsewhere (songleaf
    keeps its own under its data root) is found only through the variable, or
    passed by path to the readers.
    """
    explicit = os.environ.get(CHORDS_INDEX_ENVVAR)
    if explicit:
        path = os.path.expanduser(explicit)
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"${CHORDS_INDEX_ENVVAR} names {path}, which is not a file"
            )
        return path
    zip_path = local_chords_and_lyrics_zip()
    if zip_path is None:
        return None
    path = os.path.join(os.path.dirname(zip_path), INDEX_NAME)
    return path if os.path.isfile(path) else None


def dataframe_rows(df) -> Iterable[tuple]:
    """The rows :func:`build_chords_index` takes, from a corpus DataFrame."""
    return zip(*(df[name].tolist() for name in CORPUS_COLUMNS))


def corpus_rows(*, zip_path=None) -> Iterable[tuple]:
    """The corpus's rows, loaded through pandas (see ``get_lyrics_and_chords_dataset``).

    ``zip_path`` defaults to :func:`local_chords_and_lyrics_zip` (and, failing
    that, a download through haggle): a consumer that keeps the zip elsewhere
    passes it.
    """
    from sung.chords_and_lyrics import get_lyrics_and_chords_dataset

    df = get_lyrics_and_chords_dataset(zip_path=zip_path, usecols=CORPUS_COLUMNS)
    return dataframe_rows(df.reset_index(drop=True))


def build_chords_index(
    path: str, *, rows: Iterable[tuple] | None = None, batch_size: int = 5000
) -> dict:
    """Write the index to ``path``; return its song count, size and build time.

    ``rows`` are tuples in :data:`CORPUS_COLUMNS` order (default:
    :func:`corpus_rows`, which loads the corpus). Row ``n`` of ``rows`` is row
    ``n`` of the index. The file is written beside ``path`` and moved into place
    when complete, so a reader never sees half an index.
    """
    if batch_size < 1:
        raise ValueError(f"batch_size must be at least 1, not {batch_size!r}")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    started = time.time()
    rows = corpus_rows() if rows is None else rows
    building = f"{path}.{os.getpid()}.building"  # one per process: builds never mix
    try:
        songs = _write_index(building, rows, batch_size=batch_size)
        os.replace(building, path)
    finally:
        if os.path.exists(building):  # a failed build leaves nothing behind
            os.remove(building)
    return {
        "path": path,
        "songs": songs,
        "megabytes": round(os.path.getsize(path) / 1e6, 1),
        "seconds": round(time.time() - started, 1),
    }


def _write_index(building: str, rows: Iterable[tuple], *, batch_size: int) -> int:
    if os.path.exists(building):
        os.remove(building)
    records = (_record(row, fields) for row, fields in enumerate(rows))
    songs = 0
    with closing(sqlite3.connect(building)) as conn:
        conn.executescript(SCHEMA)
        while batch := list(islice(records, batch_size)):
            _insert(conn, batch)
            songs += len(batch)
        conn.executemany(
            "INSERT INTO meta VALUES (?, ?)",
            [("songs", str(songs)), ("built_at", time.strftime("%Y-%m-%d %H:%M:%S"))],
        )
        conn.execute("INSERT INTO chart_words(chart_words) VALUES ('optimize')")
        conn.commit()
    return songs


def _record(row: int, fields: tuple) -> tuple:
    song_id, artist, title, chart, lang, popularity = fields
    return (
        row,
        str(song_id),
        _text_or_empty(title),
        _text_or_empty(artist),
        str(lang),
        _number_or_zero(popularity),
        chart if isinstance(chart, str) else "",
    )


def _text_or_empty(value) -> str:
    return "" if value is None or value != value else str(value)  # NaN != NaN


def _number_or_zero(value) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return 0.0 if number != number else number


def _insert(conn, batch: list[tuple]) -> None:
    conn.executemany(
        "INSERT INTO songs VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(*fields[:-1], zlib.compress(fields[-1].encode("utf-8"))) for fields in batch],
    )
    conn.executemany(
        "INSERT INTO chart_words(rowid, chart) VALUES (?, ?)",
        [(fields[0], fields[-1]) for fields in batch],
    )


def connect(path: str):
    """A read-only connection to the index, closed on exit of a ``with`` block.

    One connection per call is safe across threads. Raises ``FileNotFoundError``
    when there is no index at ``path``.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No chords-and-lyrics index at {path}")
    uri = f"{Path(os.path.abspath(path)).as_uri()}?mode=ro"
    return closing(sqlite3.connect(uri, uri=True))


def index_version(path: str):
    """``(mtime_ns, size)`` of the index file, or ``None``: changes when it is rebuilt."""
    try:
        stat = os.stat(path)
    except OSError:
        return None
    return stat.st_mtime_ns, stat.st_size


def read_columns(path: str) -> dict[str, list]:
    """The short columns (:data:`COLUMN_NAMES`), each a list in row order."""
    with connect(path) as conn:
        rows = conn.execute(
            "SELECT id, title, artist, lang, popularity FROM songs ORDER BY row"
        ).fetchall()
    columns = list(map(list, zip(*rows))) or [[] for _ in COLUMN_NAMES]
    return dict(zip(COLUMN_NAMES, columns))


def rows_with_words(path: str, words: Iterable[str]) -> list[int]:
    """The rows whose chart contains every one of ``words`` (whole words, any case).

    Words are matched as FTS5 tokens (``unicode61``: ``_`` separates words,
    accents are kept). Tokenizing a query is the caller's business: pass words,
    not a sentence. No words, no rows.
    """
    if isinstance(words, str):
        raise TypeError(f"words must be an iterable of words, not the string {words!r}")
    quoted = ['"{}"'.format(word.replace('"', '""')) for word in words if word]
    if not quoted:
        return []
    with connect(path) as conn:
        found = conn.execute(
            "SELECT rowid FROM chart_words WHERE chart_words MATCH ? ORDER BY rowid",
            (" ".join(quoted),),
        ).fetchall()
    return [row for (row,) in found]


def read_chart(path: str, row: int) -> str:
    """The chart (chords over lyrics) of ``row``; ``""`` for a row not in the index."""
    with connect(path) as conn:
        found = conn.execute("SELECT chart FROM songs WHERE row = ?", (row,)).fetchone()
    return zlib.decompress(found[0]).decode("utf-8") if found else ""


def read_meta(path: str) -> dict[str, str]:
    """What the build recorded: song count and build time."""
    with connect(path) as conn:
        return dict(conn.execute("SELECT key, value FROM meta").fetchall())
