# sung.chords_and_lyrics

Tools for chords and lyrics acquisition and processing.

Example usage. The song is inlined rather than read from a file so that the
`to='text'` examples below run as real doctests instead of being skipped:
an example that is never executed is free to drift away from the signature it
claims to demonstrate.

```pycon
>>> raw = '''[Verse 1]
... C       G
... Hello there my friend
... Am      F
... This is a line of lyrics
... '''
>>> print(render_chords_and_lyrics(raw, to='text'))
[Verse 1]
C       G
Hello there my friend
Am      F
This is a line of lyrics
```

The same call with `to='pdf'` writes a file instead of returning text:

```pycon
>>> render_chords_and_lyrics(raw, to='pdf', output_path='out.pdf', lyrics_font={'size':14})
```

New features:

Filter out non-lyrics content. The keyword is `apply_filter_non_lyrics`;
`filter_non_lyrics` is the standalone function it delegates to, and passing
*that* name as a keyword would land in `**kwargs` and be silently ignored.

```pycon
>>> print(render_chords_and_lyrics(raw, to='text', apply_filter_non_lyrics=True))
C       G
Hello there my friend
Am      F
This is a line of lyrics
>>> print(remove_non_lyrics(raw))
C       G
Hello there my friend
Am      F
This is a line of lyrics
```

Keep the section markers (`[Verse 1]` and friends) while filtering:

```pycon
>>> print(render_chords_and_lyrics(
...     raw, to='text', apply_filter_non_lyrics=True, keep_metadata_lines=True
... ))
[Verse 1]
C       G
Hello there my friend
Am      F
This is a line of lyrics
```

Pack lines for better space usage (not sure this works as intended):

```pycon
>>> packed_txt = render_chords_and_lyrics(raw, to='text', pack_lines=True, max_line_length=80)
>>> packed_txt = pack_song_text(raw, max_length=80)
```

Combine both features:

```pycon
>>> optimized = render_chords_and_lyrics(raw, to='text', apply_filter_non_lyrics=True, pack_lines=True)
```

### Module Attributes

| [`CHORDS_AND_LYRICS_ZIP_ENVVAR`](#sung.chords_and_lyrics.CHORDS_AND_LYRICS_ZIP_ENVVAR)   | Environment variable naming a local copy of the corpus zip.   |
|---------------------------------------------------------------------------------|---------------------------------------------------------------|

### Functions

| `complete_font_spec`(spec, default)                                                                 |                                                                                        |
|-----------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| [`ensure_parsed_song`](#sung.chords_and_lyrics.ensure_parsed_song)(song)                           | If song is a string, parse it and return (list_of_sections, raw_text).                 |
| `extract_title`(raw_text)                                                                           |                                                                                        |
| [`filter_non_lyrics`](#sung.chords_and_lyrics.filter_non_lyrics)(song[, keep_metadata_lines])     | Filter out non-lyrics content from a song.                                             |
| `get_color`(col_str)                                                                                |                                                                                        |
| [`get_lyrics_and_chords_dataset`](#sung.chords_and_lyrics.get_lyrics_and_chords_dataset)(\*[, zip_path, ...]) | Load the Kaggle chords-and-lyrics corpus (~135K songs) as a DataFrame.                 |
| `is_chord_line`(line)                                                                               |                                                                                        |
| [`is_likely_lyrics`](#sung.chords_and_lyrics.is_likely_lyrics)(line[, has_chords_before])        | Determine if a line is likely to contain lyrics.                                       |
| [`local_chords_and_lyrics_zip`](#sung.chords_and_lyrics.local_chords_and_lyrics_zip)()                      | Return the path of a local copy of the chords-and-lyrics zip, or `None`.               |
| [`pack_song_lines`](#sung.chords_and_lyrics.pack_song_lines)(song[, max_line_length, ...])      | Pack multiple short lines together to make better use of horizontal space.             |
| [`pack_song_text`](#sung.chords_and_lyrics.pack_song_text)(song[, max_length])                 | Convenience function to pack lines and return as text.                                 |
| [`parse_chord_lyrics`](#sung.chords_and_lyrics.parse_chord_lyrics)(raw_text)                       | Generator: parse fixed-width chords/lyrics and yield dicts with 'chords' and 'lyrics'. |
| [`remove_non_lyrics`](#sung.chords_and_lyrics.remove_non_lyrics)(song[, keep_metadata])           | Convenience function to filter non-lyrics and return as text.                          |
| [`render_chords_and_lyrics`](#sung.chords_and_lyrics.render_chords_and_lyrics)(song[, to, ...])          | Aggregator: render to 'pdf' or 'text'.                                                 |
| [`render_chords_and_lyrics_to_pdf`](#sung.chords_and_lyrics.render_chords_and_lyrics_to_pdf)(song, \*, ...)     | Render song to PDF with styling parameters.                                            |
| [`render_chords_and_lyrics_to_text`](#sung.chords_and_lyrics.render_chords_and_lyrics_to_text)(song)             | Reconstruct fixed-width text from parsed song data.                                    |
| [`resolve_page_size`](#sung.chords_and_lyrics.resolve_page_size)(page_size)                       | Resolve page size from string or return the object as-is.                              |
| [`search_songs`](#sung.chords_and_lyrics.search_songs)([title, lyrics, artist, data])        | Search for a song by title, lyrics, or artist.                                         |

### Classes

| [`FontSpec`](#sung.chords_and_lyrics.FontSpec)(\*\*data)   |    |
|-----------------------------------------------------------------------|----|

### sung.chords_and_lyrics.CHORDS_AND_LYRICS_ZIP_ENVVAR *= 'SUNG_CHORDS_AND_LYRICS_ZIP'*

Environment variable naming a local copy of the corpus zip.

### *class* sung.chords_and_lyrics.FontSpec(\*\*data)

Bases: `BaseModel`

#### model_config *: [ClassVar](https://docs.python.org/3/library/typing.html#typing.ClassVar)[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].

### sung.chords_and_lyrics.ensure_parsed_song(song)

If song is a string, parse it and return (list_of_sections, raw_text).
If song is already iterable of dicts, return (list(song), None).

* **Return type:**
  [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)], [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)]

### sung.chords_and_lyrics.filter_non_lyrics(song, keep_metadata_lines=False)

Filter out non-lyrics content from a song.

* **Parameters:**
  * **song** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)]) – Raw text or parsed song data
  * **keep_metadata_lines** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, keep lines that start with [ (like [Verse])
* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)]
* **Returns:**
  Filtered list of song sections

### sung.chords_and_lyrics.get_lyrics_and_chords_dataset(, zip_path=None, usecols=None)

Load the Kaggle chords-and-lyrics corpus (~135K songs) as a DataFrame.

A local zip is read directly, with no Kaggle credentials: `zip_path` if
given, else [`local_chords_and_lyrics_zip()`](#sung.chords_and_lyrics.local_chords_and_lyrics_zip). Only when there is no local
copy is the dataset downloaded through `haggle` (which needs credentials).

* **Parameters:**
  * **zip_path** – Path to the dataset zip (as downloaded from Kaggle).
  * **usecols** – Columns to load. The CSV is ~650 MB; loading only the columns
    you need roughly halves the time and memory.

### sung.chords_and_lyrics.is_likely_lyrics(line, has_chords_before=False)

Determine if a line is likely to contain lyrics.

* **Parameters:**
  * **line** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The line to check
  * **has_chords_before** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – Whether the previous line contained chords
* **Return type:**
  [`bool`](https://docs.python.org/3/builtins/functions.html#bool)
* **Returns:**
  True if the line is likely lyrics, False otherwise

### sung.chords_and_lyrics.local_chords_and_lyrics_zip()

Return the path of a local copy of the chords-and-lyrics zip, or `None`.

Looks at `$SUNG_CHORDS_AND_LYRICS_ZIP` first, then at where `haggle`
keeps its downloads (`$HAGGLE_ROOTDIR/zips/<owner>/<dataset>.zip`, root
defaulting to `~/haggle`). The haggle layout is replicated rather than
asked of haggle, because importing haggle imports `kaggle`, which
authenticates against Kaggle at import time, even for a cached file.

### sung.chords_and_lyrics.pack_song_lines(song, max_line_length=80, preserve_chord_alignment=True)

Pack multiple short lines together to make better use of horizontal space.

* **Parameters:**
  * **song** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)]) – Raw text or parsed song data
  * **max_line_length** ([`int`](https://docs.python.org/3/builtins/functions.html#int)) – Maximum length of packed lines
  * **preserve_chord_alignment** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, keep chord alignment intact
* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)]
* **Returns:**
  List of song sections with packed lines

### sung.chords_and_lyrics.pack_song_text(song, max_length=80)

Convenience function to pack lines and return as text.

* **Parameters:**
  * **song** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)]) – Raw text or parsed song data
  * **max_length** ([`int`](https://docs.python.org/3/builtins/functions.html#int)) – Maximum length for packed lines
* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
* **Returns:**
  Packed song as text

### sung.chords_and_lyrics.parse_chord_lyrics(raw_text)

Generator: parse fixed-width chords/lyrics and yield dicts with ‘chords’ and ‘lyrics’.
Each ‘chords’ is List of (chord_name, start_index).

### sung.chords_and_lyrics.remove_non_lyrics(song, keep_metadata=False)

Convenience function to filter non-lyrics and return as text.

* **Parameters:**
  * **song** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)]) – Raw text or parsed song data
  * **keep_metadata** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, keep metadata lines (like [Verse])
* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
* **Returns:**
  Filtered song as text

### sung.chords_and_lyrics.render_chords_and_lyrics(song, to='pdf', output_path=None, apply_filter_non_lyrics=False, keep_metadata_lines=False, pack_lines=False, max_line_length=80, \*\*kwargs)

Aggregator: render to ‘pdf’ or ‘text’.

- to=’pdf’: writes file to output_path (required).
- to=’text’: returns reconstructed text.

* **Parameters:**
  * **song** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)]) – Raw text or parsed song data
  * **to** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Output format (‘pdf’ or ‘text’)
  * **output_path** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Path for PDF output (required for PDF)
  * **apply_filter_non_lyrics** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, filter out non-lyrics content
  * **keep_metadata_lines** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, keep metadata lines (like [Verse]) when filtering
  * **pack_lines** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, pack short lines together for better space usage
  * **max_line_length** ([`int`](https://docs.python.org/3/builtins/functions.html#int)) – Maximum length for packed lines
  * **\*\*kwargs** – Additional arguments passed to rendering functions
* **Return type:**
  [`None`](https://docs.python.org/3/builtins/constants.html#None) | [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### sung.chords_and_lyrics.render_chords_and_lyrics_to_pdf(song, , output_path, title=None, page_size='A4', margin=72, lyrics_font=None, chords_font=None, title_font=None, spacing_chord_lyrics=None, spacing_group=None, spacing_paragraph=None)

Render song to PDF with styling parameters. Accepts raw text or parsed song.

### sung.chords_and_lyrics.render_chords_and_lyrics_to_text(song)

Reconstruct fixed-width text from parsed song data.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### sung.chords_and_lyrics.resolve_page_size(page_size)

Resolve page size from string or return the object as-is.

* **Parameters:**
  **page_size** – Either a string (like “A4”, “LETTER”, “LEGAL”) or a page size object
* **Returns:**
  The appropriate page size object from reportlab

### sung.chords_and_lyrics.search_songs(title='', , lyrics='', artist='', data=None)

Search for a song by title, lyrics, or artist.
