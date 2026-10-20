# sung.chords_index

A SQLite + FTS5 index of the chords-and-lyrics corpus, read without the corpus in memory.

The corpus ([`sung.chords_and_lyrics.get_lyrics_and_chords_dataset()`](sung.chords_and_lyrics.html.md#sung.chords_and_lyrics.get_lyrics_and_chords_dataset)) is a
~650 MB CSV: as a DataFrame it costs about 1.1 GB per process. This module
writes it once to one SQLite file (titles, artists, language, popularity, each
chart zlib-compressed, and an FTS5 table of the charts’ words) and reads that
file back piecemeal: the short columns for matching, the words for lyrics
search, one chart at a time.

It imports only the standard library, so a web worker that serves from the
index never loads pandas (thorwhalen/sung#17). Building it does load the corpus
(through pandas), so run [`build_chords_index()`](#sung.chords_index.build_chords_index) once, apart from any server.
Ranking and fuzzy matching are the consumer’s business (`songleaf`,
`scoreseek`); this module only stores and fetches.

```pycon
>>> import os, tempfile
>>> rows = [
...     (1, "The Band", "Paper Boats", "G\nPaper boats drift", "en", 3),
...     (2, "Other", "Quiet Road", "C\nquiet road", "en", 1),
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
```

### Module Attributes

| [`CHORDS_AND_LYRICS_ZIP_ENVVAR`](#sung.chords_index.CHORDS_AND_LYRICS_ZIP_ENVVAR)   | Environment variable naming a local copy of the corpus zip.                                                                                           |
|---------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`INDEX_NAME`](#sung.chords_index.INDEX_NAME)                     | The index's file name; it lives beside the corpus zip by convention.                                                                                  |
| [`CHORDS_INDEX_ENVVAR`](#sung.chords_index.CHORDS_INDEX_ENVVAR)            | Environment variable naming the index file.                                                                                                           |
| [`CORPUS_COLUMNS`](#sung.chords_index.CORPUS_COLUMNS)                 | The corpus columns the index is built from, in the order `rows` gives them: song id, artist, title, chart (chords over lyrics), language, popularity. |
| [`COLUMN_NAMES`](#sung.chords_index.COLUMN_NAMES)                   | What [`read_columns()`](#sung.chords_index.read_columns) returns, in row order.                                                           |

### Functions

| [`build_chords_index`](#sung.chords_index.build_chords_index)(path, \*[, rows, batch_size])   | Write the index to `path`; return its song count, size and build time.                                         |
|-----------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| [`connect`](#sung.chords_index.connect)(path)                                      | A read-only connection to the index, closed on exit of a `with` block.                                         |
| [`corpus_rows`](#sung.chords_index.corpus_rows)(\*[, zip_path])                        | The corpus's rows, loaded through pandas (see `get_lyrics_and_chords_dataset`).                                |
| [`dataframe_rows`](#sung.chords_index.dataframe_rows)(df)                                 | The rows [`build_chords_index()`](#sung.chords_index.build_chords_index) takes, from a corpus DataFrame. |
| [`index_version`](#sung.chords_index.index_version)(path)                                | `(mtime_ns, size)` of the index file, or `None`: changes when it is rebuilt.                                   |
| [`local_chords_and_lyrics_zip`](#sung.chords_index.local_chords_and_lyrics_zip)()                      | Return the path of a local copy of the chords-and-lyrics zip, or `None`.                                       |
| [`local_chords_index`](#sung.chords_index.local_chords_index)()                               | Return the path of a local index file, or `None`.                                                              |
| [`read_chart`](#sung.chords_index.read_chart)(path, row)                              | The chart (chords over lyrics) of `row`; `""` for a row not in the index.                                      |
| [`read_columns`](#sung.chords_index.read_columns)(path)                                 | The short columns ([`COLUMN_NAMES`](#sung.chords_index.COLUMN_NAMES)), each a list in row order.   |
| [`read_meta`](#sung.chords_index.read_meta)(path)                                    | What the build recorded: song count and build time.                                                            |
| [`rows_with_words`](#sung.chords_index.rows_with_words)(path, words)                       | The rows whose chart contains every one of `words` (whole words, any case).                                    |

### sung.chords_index.CHORDS_AND_LYRICS_ZIP_ENVVAR *= 'SUNG_CHORDS_AND_LYRICS_ZIP'*

Environment variable naming a local copy of the corpus zip.

### sung.chords_index.CHORDS_INDEX_ENVVAR *= 'SUNG_CHORDS_INDEX'*

Environment variable naming the index file.

### sung.chords_index.COLUMN_NAMES *= ('ids', 'titles', 'artists', 'langs', 'popularity')*

What [`read_columns()`](#sung.chords_index.read_columns) returns, in row order.

### sung.chords_index.CORPUS_COLUMNS *= ('Unnamed: 0', 'artist_name', 'song_name', 'chords&lyrics', 'lang', 'popularity')*

The corpus columns the index is built from, in the order `rows` gives them:
song id, artist, title, chart (chords over lyrics), language, popularity.

### sung.chords_index.INDEX_NAME *= 'chords-and-lyrics.sqlite'*

The index’s file name; it lives beside the corpus zip by convention.

### sung.chords_index.build_chords_index(path, , rows=None, batch_size=5000)

Write the index to `path`; return its song count, size and build time.

`rows` are tuples in [`CORPUS_COLUMNS`](#sung.chords_index.CORPUS_COLUMNS) order (default:
[`corpus_rows()`](#sung.chords_index.corpus_rows), which loads the corpus). Row `n` of `rows` is row
`n` of the index. The file is written beside `path` and moved into place
when complete, so a reader never sees half an index.

* **Return type:**
  [`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)

### sung.chords_index.connect(path)

A read-only connection to the index, closed on exit of a `with` block.

One connection per call is safe across threads. Raises `FileNotFoundError`
when there is no index at `path`.

### sung.chords_index.corpus_rows(, zip_path=None)

The corpus’s rows, loaded through pandas (see `get_lyrics_and_chords_dataset`).

`zip_path` defaults to [`local_chords_and_lyrics_zip()`](#sung.chords_index.local_chords_and_lyrics_zip) (and, failing
that, a download through haggle): a consumer that keeps the zip elsewhere
passes it.

* **Return type:**
  [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)]

### sung.chords_index.dataframe_rows(df)

The rows [`build_chords_index()`](#sung.chords_index.build_chords_index) takes, from a corpus DataFrame.

* **Return type:**
  [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)]

### sung.chords_index.index_version(path)

`(mtime_ns, size)` of the index file, or `None`: changes when it is rebuilt.

### sung.chords_index.local_chords_and_lyrics_zip()

Return the path of a local copy of the chords-and-lyrics zip, or `None`.

Looks at `$SUNG_CHORDS_AND_LYRICS_ZIP` first, then at where `haggle`
keeps its downloads (`$HAGGLE_ROOTDIR/zips/<owner>/<dataset>.zip`, root
defaulting to `~/haggle`). The haggle layout is replicated rather than
asked of haggle, because importing haggle imports `kaggle`, which
authenticates against Kaggle at import time, even for a cached file.

### sung.chords_index.local_chords_index()

Return the path of a local index file, or `None`.

`$SUNG_CHORDS_INDEX` first (an error if it names no file), then
[`INDEX_NAME`](#sung.chords_index.INDEX_NAME) beside the local corpus zip
([`local_chords_and_lyrics_zip()`](#sung.chords_index.local_chords_and_lyrics_zip)). An index kept elsewhere (songleaf
keeps its own under its data root) is found only through the variable, or
passed by path to the readers.

### sung.chords_index.read_chart(path, row)

The chart (chords over lyrics) of `row`; `""` for a row not in the index.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### sung.chords_index.read_columns(path)

The short columns ([`COLUMN_NAMES`](#sung.chords_index.COLUMN_NAMES)), each a list in row order.

* **Return type:**
  [`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)]

### sung.chords_index.read_meta(path)

What the build recorded: song count and build time.

* **Return type:**
  [`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]

### sung.chords_index.rows_with_words(path, words)

The rows whose chart contains every one of `words` (whole words, any case).

Words are matched as FTS5 tokens (`unicode61`: `_` separates words,
accents are kept). Tokenizing a query is the caller’s business: pass words,
not a sentence. No words, no rows.

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`int`](https://docs.python.org/3/builtins/functions.html#int)]
