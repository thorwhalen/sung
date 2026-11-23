# sung

Music data access: search and process chord sheets and lyrics from the chords&lyrics dataset, and search tracks and build playlists on Spotify.

[pypi](https://pypi.org/project/sung/) · [Documentation](https://thorwhalen.github.io/sung)


# Install

```bash
pip install sung
```


# Agent skill

`sung` ships a `sung-playlist` agent skill (build a Spotify playlist from a list of songs) inside the package, in `sung/data/skills/`. Install it with `gh skill install thorwhalen/sung sung-playlist`, or link it from your `pip install`ed copy: `ln -s "$(python -c 'import sung, pathlib; print(pathlib.Path(sung.__file__).parent / "data/skills/sung-playlist")')" .claude/skills/sung-playlist`.

# Chords and Lyrics Processing

The `sung` package provides powerful tools for processing chord sheets and lyrics, including parsing, filtering, formatting, and rendering to various formats.

## Basic Usage

```python
from sung import render_chords_and_lyrics, search_songs

# Search for songs in the dataset
songs = search_songs(title="wonderwall", artist="oasis")
print(f"Found {len(songs)} songs")

# Get the raw chord sheet text
raw_text = songs.iloc[0]["chords&lyrics"]

# Render to text (reconstruct the original format)
formatted_text = render_chords_and_lyrics(raw_text, to="text")
print(formatted_text)

# Render to PDF
render_chords_and_lyrics(raw_text, to="pdf", output_path="song.pdf")
```

## Advanced Features

### Filter Non-Lyrics Content

Remove extraneous text that isn't part of the actual song. The keyword is `apply_filter_non_lyrics` -- `filter_non_lyrics` is the standalone function it delegates to, and passing *that* name as a keyword is silently ignored:

```python
from sung import remove_non_lyrics

# Remove non-lyrics content (section headers, metadata, etc.)
clean_lyrics = render_chords_and_lyrics(
    raw_text, to="text", apply_filter_non_lyrics=True
)

# Keep metadata lines like [Verse], [Chorus]
clean_with_metadata = render_chords_and_lyrics(
    raw_text, to="text", apply_filter_non_lyrics=True, keep_metadata_lines=True
)

# Standalone function
clean_text = remove_non_lyrics(raw_text)
```

### Pack Lines for Better Space Usage

Combine short lines to make better use of horizontal space:

```python
from sung import pack_song_text

# Pack lines up to 80 characters
packed_text = render_chords_and_lyrics(
    raw_text, to="text", pack_lines=True, max_line_length=80
)

# Standalone function
packed = pack_song_text(raw_text, max_length=80)
```

### Combine Features

Use both filtering and packing together:

```python
# Clean and optimized output
optimized = render_chords_and_lyrics(
    raw_text,
    to="text",
    apply_filter_non_lyrics=True,
    pack_lines=True,
    max_line_length=80,
)
```

## PDF Rendering with Custom Styling

```python
# Custom fonts and spacing
render_chords_and_lyrics(
    raw_text,
    to="pdf",
    output_path="styled_song.pdf",
    page_size="LETTER",  # Can use strings like 'A4', 'LETTER', 'LEGAL'
    lyrics_font={"name": "Times-Roman", "size": 14, "color": "black"},
    chords_font={"name": "Helvetica-Bold", "size": 12, "color": "blue"},
    title_font={"name": "Helvetica-Bold", "size": 18, "color": "darkred"},
    margin=50,
    spacing_chord_lyrics=15,
    spacing_group=20,
)
```

## Dataset Access

The package provides access to a large dataset of songs with chords and lyrics:

<!-- wads-docs: skip needs the chords and lyrics dataset -->
```python
from sung import get_lyrics_and_chords_dataset

# Load the full dataset (cached after first load)
df = get_lyrics_and_chords_dataset()
print(f"Dataset contains {len(df)} songs")

# A local copy of the zip is read directly, with no Kaggle credentials:
# pass zip_path=, or set SUNG_CHORDS_AND_LYRICS_ZIP, or keep it where haggle
# downloads it ($HAGGLE_ROOTDIR/zips/eitanbentora/chords-and-lyrics-dataset.zip).
# usecols= loads only the columns you need (the CSV is ~650 MB).
df = get_lyrics_and_chords_dataset(
    usecols=["artist_name", "song_name", "chords&lyrics"]
)

# Search by multiple criteria
results = search_songs(
    title="hotel california", artist="eagles", lyrics="welcome to the hotel"
)
```

## Core Functions

- `render_chords_and_lyrics()`: Main function for rendering chord sheets
- `search_songs()`: Search the song database
- `parse_chord_lyrics()`: Parse raw chord/lyrics text into structured data
- `filter_non_lyrics()`: Remove non-lyrics content
- `pack_song_lines()`: Combine short lines for better formatting
- `extract_title()`: Extract song title from chord sheet
- `get_lyrics_and_chords_dataset()`: Access the full dataset


# Spotify 

For spotify tools, you'll also need spotify API access info:

```
export SPOTIFY_API_CLIENT_ID="your_api_client_id"
export SPOTIFY_API_CLIENT_SECRET="your_api_client_secrete"
export SPOTIPY_REDIRECT_URI="http://127.0.0.1:8000/callback"
export SPOTIPY_CLIENT_ID="$SPOTIFY_API_CLIENT_ID"
export SPOTIPY_CLIENT_SECRET="$SPOTIFY_API_CLIENT_SECRET"
```

## Spotify API credentials?

To obtain Spotify API credentials, follow these steps:

	1.	Create a Spotify Developer Account:

	•	Visit the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).

	•	Log in with your Spotify account or create a new one.

	2.	Register a New Application:

	•	Click on “Create an App.”

	•	Provide an App Name and App Description.

	•	Agree to the Developer Terms of Service.

	•	Click “Create.”

	3.	Retrieve Client ID and Client Secret:

	•	After creating the app, you’ll be directed to the app’s dashboard.

	•	Here, you’ll find your Client ID and Client Secret.

	•	Keep these credentials secure; they are essential for API authentication.

	4.	Set Redirect URIs (if applicable):

	•	In your app settings, click “Edit Settings.”

	•	Under “Redirect URIs,” add the URIs where Spotify should redirect after authentication.
  
	•	This is crucial for certain authorization flows.

For detailed information on authorization flows and using your credentials, refer to [Spotify’s Authorization Guide](https://developer.spotify.com/documentation/web-api/concepts/authorization).

Ensure you handle your Client Secret securely and adhere to [Spotify’s Developer Terms of Service](https://developer.spotify.com/terms/).

> **Note on redirect URIs.** Spotify rejects `http://localhost` as
> "Insecure" since April 2025. Use `http://127.0.0.1:PORT/callback` and
> add that exact value (no trailing slash, exact case) in your app
> dashboard's Redirect URIs.

> **Note on audio features.** Spotify [removed `/audio-features`
> access](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api)
> for apps registered after Nov 2024. `sung` degrades gracefully:
> `Tracks.audio_features` returns `{}` with a one-time warning, and
> `Tracks.data` / `Playlist.data` fall back to metadata-only.


# Building a Spotify Playlist from a List of Song Names

Got a list of song names (from a setlist, a chat, a markdown doc) and want a playlist? Use `playlist_from_songs` — it searches Spotify for each song, picks the best match (preferring exact title + artist matches and filtering out covers/karaoke), and creates the playlist in one call.

```python
from sung import playlist_from_songs

songs = [
    ("Clocks", "Coldplay"),
    "Fix You — Coldplay",  # also: "Title - Artist", "Title by Artist"
    {"name": "Believer", "artist": "Imagine Dragons"},
    "Radioactive",  # title only is fine, but match quality drops
]

playlist, matches = playlist_from_songs(
    songs,
    playlist_name="My Mix",
    # public=True,           # default
    # market="US",           # optional ISO market code
    # search_limit=10,       # candidates to consider per song
    # skip_missing=True,     # drop unresolved instead of raising
)

print(playlist.playlist_url)
for m in matches:
    print(m.summary())
    if m.ambiguous:
        for c in m.candidates[:3]:
            print(
                "   alt:",
                c["name"],
                "—",
                ", ".join(c["artists"]),
                "pop=",
                c["popularity"],
            )
```

`matches` is a `list[SongMatch]`. Each match exposes `track_id`, `track_name`, `artist_names`, `album_name`, `popularity`, plus `ambiguous: bool` (top two candidates are different songs/artists scoring within 10 points — worth showing alternatives) and `not_found: bool`.

## CLI

For one-shot use from a file (or stdin), the same logic is wrapped as `python -m sung.playlists`:

```bash
# songs.txt — one song per line; "Title - Artist" or just "Title".
# Comment lines (#), markdown bullets (-, *, 1.), and **bold** are tolerated.
python -m sung.playlists songs.txt --name "My Mix"

# Inspect matches without creating the playlist:
python -m sung.playlists songs.txt --dry-run

# JSON report (for chaining):
python -m sung.playlists songs.txt --name "My Mix" --json

# stdin works too:
cat songs.txt | python -m sung.playlists - --name "My Mix"
```

Other flags: `--private` (default is public), `--market US`.

## Lower-level building blocks

If you want to inspect matches before creating anything (or hand-tune ranking), the helper is a thin layer over:

- `parse_song_descriptor(...)` — turn a descriptor into `(name, artist)`
- `resolve_song(...)` / `resolve_songs(...)` — search + rank, return `SongMatch`(es)
- `Playlist.create_from_track_list(...)` — actually creates the playlist
- `delete_playlist(playlist_id, ask_confirmation=False)` — clean up

A longer worked session (search results as a DataFrame, audio features, audio analysis) is in [misc/docs/spotify_notebook.md](https://github.com/thorwhalen/sung/blob/main/misc/docs/spotify_notebook.md).
