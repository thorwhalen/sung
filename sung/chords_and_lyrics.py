"""
Tools for chords and lyrics acquisition and processing.

Example usage:

>>> raw = open('song.txt').read()  # doctest: +SKIP
>>> render_chords_and_lyrics(raw, to='pdf', output_path='out.pdf', lyrics_font={'size':14})  # doctest: +SKIP
>>> txt = render_chords_and_lyrics(raw, to='text')  # doctest: +SKIP

New features:

Filter out non-lyrics content:
>>> clean_txt = render_chords_and_lyrics(raw, to='text', filter_non_lyrics=True)  # doctest: +SKIP
>>> clean_txt = remove_non_lyrics(raw)  # doctest: +SKIP

Pack lines for better space usage (not sure this works as intended):
>>> packed_txt = render_chords_and_lyrics(raw, to='text', pack_lines=True, max_line_length=80)  # doctest: +SKIP
>>> packed_txt = pack_song_text(raw, max_length=80)  # doctest: +SKIP

Combine both features:
>>> optimized = render_chords_and_lyrics(raw, to='text', filter_non_lyrics=True, pack_lines=True)  # doctest: +SKIP

"""

from functools import lru_cache


@lru_cache(maxsize=1)
def get_lyrics_and_chords_dataset():
    import pandas as pd
    import io
    from haggle import get_kaggle_dataset

    data = get_kaggle_dataset("eitanbentora/chords-and-lyrics-dataset")

    return pd.read_csv(io.BytesIO(data["chords_and_lyrics.csv"]))


def search_songs(title="", *, lyrics="", artist="", data=None):
    """Search for a song by title, lyrics, or artist."""
    if data is None:
        data = get_lyrics_and_chords_dataset()
    results = data[
        (data["song_name"].str.contains(title, case=False))
        & (data["chords&lyrics"].str.contains(lyrics, case=False))
        & (data["artist_name"].str.contains(artist, case=False))
    ]
    return results


# --------------------------------------------------------------------------------------
# Lyrics and Chords Formatting and Processing
import re
from pydantic import BaseModel, ValidationError
from typing import Union, Tuple, List, Dict
from collections.abc import Iterable

# Default font specifications
default_lyrics_font = {"name": "Courier", "size": 12, "color": "black", "alpha": 1}
default_chords_font = {"name": "Courier-Bold", "size": 10, "color": "black", "alpha": 1}
default_title_font = {
    "name": "Helvetica-Bold",
    "size": 16,
    "color": "black",
    "alpha": 1,
}


def get_color(col_str: str):
    from reportlab.lib import colors

    col_str = col_str.strip()
    if hasattr(colors, col_str):
        return getattr(colors, col_str)
    if re.match(r"^#([0-9A-Fa-f]{6})$", col_str):
        return colors.HexColor(col_str)
    return colors.black


class FontSpec(BaseModel):
    name: str
    size: float
    color: str
    alpha: float


def complete_font_spec(spec: dict, default: dict) -> FontSpec:
    merged = default.copy()
    if spec:
        merged.update(spec)
    try:
        return FontSpec(**merged)
    except ValidationError as e:
        raise ValueError(f"Invalid font spec: {e}")


def is_chord_line(line: str) -> bool:
    tokens = [t for t in line.strip().split() if t]
    return bool(tokens) and all(re.match(r"^[A-G][^\s]*$", t) for t in tokens)


def parse_chord_lyrics(raw_text: str):
    """
    Generator: parse fixed-width chords/lyrics and yield dicts with 'chords' and 'lyrics'.
    Each 'chords' is List of (chord_name, start_index).
    """
    lines = raw_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if (
            is_chord_line(line)
            and i + 1 < len(lines)
            and not is_chord_line(lines[i + 1])
        ):
            chord_line = line
            lyric_line = lines[i + 1]
            chords = [(m.group(), m.start()) for m in re.finditer(r"\S+", chord_line)]
            yield {"chords": chords, "lyrics": lyric_line}
            i += 2
        else:
            yield {"chords": [], "lyrics": line}
            i += 1


def extract_title(raw_text: str) -> str:
    for line in raw_text.splitlines():
        txt = line.strip()
        if not txt or txt.startswith("[") or is_chord_line(line):
            continue
        return txt
    return ""


def ensure_parsed_song(
    song: str | Iterable[dict],
) -> tuple[list[dict], str | None]:
    """
    If song is a string, parse it and return (list_of_sections, raw_text).
    If song is already iterable of dicts, return (list(song), None).
    """
    if isinstance(song, str):
        parsed = list(parse_chord_lyrics(song))
        return parsed, song
    try:
        parsed = list(song)
        return parsed, None
    except TypeError:
        raise ValueError("Song must be raw text or iterable of sections.")


def render_chords_and_lyrics_to_pdf(
    song: str | Iterable[dict],
    *,
    output_path: str,
    title: str = None,
    page_size: str | tuple = "A4",
    margin: float = 72,
    lyrics_font: dict = None,
    chords_font: dict = None,
    title_font: dict = None,
    spacing_chord_lyrics: float = None,
    spacing_group: float = None,
    spacing_paragraph: float = None,
):
    """
    Render song to PDF with styling parameters. Accepts raw text or parsed song.
    """
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics

    page_size = resolve_page_size(page_size)

    song_data, raw = ensure_parsed_song(song)
    lyr_fs = complete_font_spec(lyrics_font or {}, default_lyrics_font)
    chd_fs = complete_font_spec(chords_font or {}, default_chords_font)
    ttl_fs = complete_font_spec(title_font or {}, default_title_font)

    if spacing_chord_lyrics is None:
        spacing_chord_lyrics = chd_fs.size * 1.2
    if spacing_group is None:
        spacing_group = lyr_fs.size * 1.5
    if spacing_paragraph is None:
        spacing_paragraph = lyr_fs.size * 2

    if title is None and raw:
        title = extract_title(raw)

    c = canvas.Canvas(output_path, pagesize=page_size)
    width, height = page_size
    char_width = pdfmetrics.stringWidth("M", lyr_fs.name, lyr_fs.size)
    y = height - margin

    # Title
    if title:
        c.setFont(ttl_fs.name, ttl_fs.size)
        c.setFillColor(get_color(ttl_fs.color))
        c.setFillAlpha(ttl_fs.alpha)
        c.drawString(margin, y, title)
        y -= ttl_fs.size * 1.5

    for section in song_data:
        chords = section["chords"]
        lyrics = section["lyrics"]
        if y < margin + lyr_fs.size * 3:
            c.showPage()
            y = height - margin
        c.setFont(chd_fs.name, chd_fs.size)
        c.setFillColor(get_color(chd_fs.color))
        c.setFillAlpha(chd_fs.alpha)
        for chord, pos in chords:
            x = margin + pos * char_width
            c.drawString(x, y, chord)
        c.setFont(lyr_fs.name, lyr_fs.size)
        c.setFillColor(get_color(lyr_fs.color))
        c.setFillAlpha(lyr_fs.alpha)
        y_lyr = y - spacing_chord_lyrics
        c.drawString(margin, y_lyr, lyrics)
        if not lyrics.strip():
            y = y_lyr - spacing_paragraph
        else:
            y = y_lyr - spacing_group

    c.save()


def render_chords_and_lyrics_to_text(
    song: str | Iterable[dict],
) -> str:
    """
    Reconstruct fixed-width text from parsed song data.
    """
    song_data, _ = ensure_parsed_song(song)
    lines = []
    for section in song_data:
        chords = section["chords"]
        lyrics = section["lyrics"]
        if chords:
            # Determine width
            max_pos = max(pos + len(ch) for ch, pos in chords)
            width = max(max_pos, len(lyrics))
            chord_line = list(" " * width)
            for ch, pos in chords:
                chord_line[pos : pos + len(ch)] = ch
            lines.append("".join(chord_line).rstrip())
        lines.append(lyrics)
    return "\n".join(lines)


def render_chords_and_lyrics(
    song: str | Iterable[dict],
    to: str = "pdf",
    output_path: str = None,
    apply_filter_non_lyrics: bool = False,
    keep_metadata_lines: bool = False,
    pack_lines: bool = False,
    max_line_length: int = 80,
    **kwargs,
) -> None | str:
    """
    Aggregator: render to 'pdf' or 'text'.
    - to='pdf': writes file to output_path (required).
    - to='text': returns reconstructed text.

    Args:
        song: Raw text or parsed song data
        to: Output format ('pdf' or 'text')
        output_path: Path for PDF output (required for PDF)
        apply_filter_non_lyrics: If True, filter out non-lyrics content
        keep_metadata_lines: If True, keep metadata lines (like [Verse]) when filtering
        pack_lines: If True, pack short lines together for better space usage
        max_line_length: Maximum length for packed lines
        **kwargs: Additional arguments passed to rendering functions
    """
    # Apply filters and transformations if requested
    processed_song = song

    if apply_filter_non_lyrics:
        processed_song = filter_non_lyrics(
            processed_song, keep_metadata_lines=keep_metadata_lines
        )

    if pack_lines:
        processed_song = pack_song_lines(
            processed_song, max_line_length=max_line_length
        )

    fmt = to.lower()
    if fmt == "pdf":
        if not output_path:
            raise ValueError("output_path is required for PDF rendering")
        return render_chords_and_lyrics_to_pdf(
            processed_song, output_path=output_path, **kwargs
        )
    elif fmt in ("text", "txt"):
        return render_chords_and_lyrics_to_text(processed_song)
    else:
        raise ValueError(f"Unknown render format: {to}")


def is_likely_lyrics(line: str, has_chords_before: bool = False) -> bool:
    """
    Determine if a line is likely to contain lyrics.

    Args:
        line: The line to check
        has_chords_before: Whether the previous line contained chords

    Returns:
        True if the line is likely lyrics, False otherwise
    """
    line = line.strip()

    # Empty lines are kept (they might be intentional spacing)
    if not line:
        return True

    # Lines starting with [ are typically metadata (like [Verse], [Chorus])
    if line.startswith("["):
        return False

    # If it's a chord line, it's not lyrics
    if is_chord_line(line):
        return False

    # If the previous line had chords, this is likely lyrics
    if has_chords_before:
        return True

    # Look for common non-lyrics patterns
    # Lines that are all caps and short might be section headers
    if line.isupper() and len(line) < 20:
        return False

    # Lines with lots of dashes or equals might be separators
    if re.match(r"^[-=_]{3,}$", line):
        return False

    # Default to considering it lyrics if we're not sure
    return True


def filter_non_lyrics(
    song: str | Iterable[dict], keep_metadata_lines: bool = False
) -> list[dict]:
    """
    Filter out non-lyrics content from a song.

    Args:
        song: Raw text or parsed song data
        keep_metadata_lines: If True, keep lines that start with [ (like [Verse])

    Returns:
        Filtered list of song sections
    """
    song_data, _ = ensure_parsed_song(song)
    filtered = []

    for i, section in enumerate(song_data):
        line = section["lyrics"]
        chords = section["chords"]

        # Check if previous section had chords
        has_chords_before = bool(chords)

        # If this section has chords, it's definitely part of the song
        if chords:
            filtered.append(section)
            continue

        # Check if this is likely lyrics
        if is_likely_lyrics(line, has_chords_before):
            # Special case for metadata lines
            if line.strip().startswith("[") and not keep_metadata_lines:
                continue
            filtered.append(section)

    return filtered


# TODO: Make this work
def pack_song_lines(
    song: str | Iterable[dict],
    max_line_length: int = 80,
    preserve_chord_alignment: bool = True,
) -> list[dict]:
    """
    Pack multiple short lines together to make better use of horizontal space.

    Args:
        song: Raw text or parsed song data
        max_line_length: Maximum length of packed lines
        preserve_chord_alignment: If True, keep chord alignment intact

    Returns:
        List of song sections with packed lines
    """
    song_data, _ = ensure_parsed_song(song)

    if not song_data:
        return []

    packed = []
    current_packed_lyrics = ""
    current_packed_chords = []

    def finalize_current_pack():
        if current_packed_lyrics.strip() or current_packed_chords:
            packed.append(
                {
                    "chords": current_packed_chords,
                    "lyrics": current_packed_lyrics.rstrip(),
                }
            )

    for section in song_data:
        chords = section["chords"]
        lyrics = section["lyrics"]

        # If this section has chords, we need to be more careful about packing
        if chords:
            # If we have something in the current pack, finalize it first
            if current_packed_lyrics.strip() or current_packed_chords:
                finalize_current_pack()
                current_packed_lyrics = ""
                current_packed_chords = []

            # Add this section as-is (chord sections are typically already well-formatted)
            packed.append(section)
            continue

        # For lyrics-only sections, try to pack them
        if not lyrics.strip():
            # Empty line - finalize current pack and add empty line
            finalize_current_pack()
            current_packed_lyrics = ""
            current_packed_chords = []
            packed.append(section)
            continue

        # Check if we can add this line to the current pack
        potential_line = (
            current_packed_lyrics
            + (" " if current_packed_lyrics else "")
            + lyrics.strip()
        )

        if len(potential_line) <= max_line_length and not lyrics.strip().startswith(
            "["
        ):
            # Add to current pack
            current_packed_lyrics = potential_line
        else:
            # Finalize current pack and start new one
            finalize_current_pack()
            current_packed_lyrics = lyrics.strip()
            current_packed_chords = []

    # Don't forget the last pack
    finalize_current_pack()

    return packed


# Convenience functions for standalone use
def remove_non_lyrics(song: str | Iterable[dict], keep_metadata: bool = False) -> str:
    """
    Convenience function to filter non-lyrics and return as text.

    Args:
        song: Raw text or parsed song data
        keep_metadata: If True, keep metadata lines (like [Verse])

    Returns:
        Filtered song as text
    """
    filtered = filter_non_lyrics(song, keep_metadata_lines=keep_metadata)
    return render_chords_and_lyrics_to_text(filtered)


def pack_song_text(song: str | Iterable[dict], max_length: int = 80) -> str:
    """
    Convenience function to pack lines and return as text.

    Args:
        song: Raw text or parsed song data
        max_length: Maximum length for packed lines

    Returns:
        Packed song as text
    """
    packed = pack_song_lines(song, max_line_length=max_length)
    return render_chords_and_lyrics_to_text(packed)


def resolve_page_size(page_size):
    """
    Resolve page size from string or return the object as-is.

    Args:
        page_size: Either a string (like "A4", "LETTER", "LEGAL") or a page size object

    Returns:
        The appropriate page size object from reportlab
    """
    from reportlab.lib import pagesizes

    if isinstance(page_size, str):
        page_size_upper = page_size.upper()
        if hasattr(pagesizes, page_size_upper):
            return getattr(pagesizes, page_size_upper)
        else:
            # Try common variations
            size_map = {
                "A4": pagesizes.A4,
                "LETTER": pagesizes.LETTER,
                "LEGAL": pagesizes.LEGAL,
                "A3": pagesizes.A3,
                "A5": pagesizes.A5,
            }
            if page_size_upper in size_map:
                return size_map[page_size_upper]
            else:
                raise ValueError(
                    f"Unknown page size: {page_size}. Available sizes: {list(size_map.keys())}"
                )

    # If it's not a string, assume it's already a valid page size object
    return page_size
