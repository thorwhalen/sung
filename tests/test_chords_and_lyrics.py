"""Tests for :mod:`sung.chords_and_lyrics` -- the fully credential-free layer.

Chord/lyric handling never touches Spotify. The central invariant is that
parsing and text rendering are inverses: a chord chart round-trips through
``parse_chord_lyrics`` -> ``render_chords_and_lyrics_to_text`` unchanged, which
is what makes column-aligned chord positions trustworthy.
"""

import pytest

from sung.chords_and_lyrics import (
    complete_font_spec,
    default_lyrics_font,
    ensure_parsed_song,
    extract_title,
    filter_non_lyrics,
    is_chord_line,
    is_likely_lyrics,
    pack_song_lines,
    pack_song_text,
    parse_chord_lyrics,
    remove_non_lyrics,
    render_chords_and_lyrics,
    render_chords_and_lyrics_to_text,
    resolve_page_size,
)

SONG = "\n".join(
    [
        "My Little Song",
        "[Verse 1]",
        "C       G",
        "Hello there my friend",
        "Am      F",
        "How are you today",
        "",
        "[Chorus]",
        "G",
        "Sing it loud",
    ]
)


# ---------------------------------------------------------------------------
# Chord line detection


@pytest.mark.parametrize(
    "line", ["C       G", "Am      F", "G", "Am7 F#m Bb", "C/G  Dsus4"]
)
def test_is_chord_line_accepts_chord_lines(line):
    assert is_chord_line(line)


@pytest.mark.parametrize(
    "line",
    [
        "",
        "   ",
        "Hello there my friend",
        "[Chorus]",
        "How are you today",
    ],
)
def test_is_chord_line_rejects_non_chord_lines(line):
    assert not is_chord_line(line)


def test_is_chord_line_requires_every_token_to_be_a_chord():
    """One lyric word is enough to disqualify the line.

    Otherwise a lyric starting with a chord-shaped word ("GO now") would be
    mistaken for a chord line and the following lyric line would be swallowed.
    """
    assert not is_chord_line("C G and then some words")


# ---------------------------------------------------------------------------
# Parsing


def test_parse_chord_lyrics_pairs_chords_with_the_following_line():
    sections = list(parse_chord_lyrics(SONG))
    with_chords = [s for s in sections if s["chords"]]
    assert [s["lyrics"] for s in with_chords] == [
        "Hello there my friend",
        "How are you today",
        "Sing it loud",
    ]


def test_parse_chord_lyrics_records_column_positions():
    """Chord column offsets are the whole point of a fixed-width chart."""
    (section,) = list(parse_chord_lyrics("C       G\nHello there my friend"))
    assert section["chords"] == [("C", 0), ("G", 8)]


def test_parse_chord_lyrics_keeps_plain_lines_chordless():
    sections = list(parse_chord_lyrics("just a line\nand another"))
    assert sections == [
        {"chords": [], "lyrics": "just a line"},
        {"chords": [], "lyrics": "and another"},
    ]


def test_ensure_parsed_song_accepts_text_and_parsed_forms():
    parsed, raw = ensure_parsed_song(SONG)
    assert raw == SONG
    reparsed, raw_again = ensure_parsed_song(parsed)
    assert reparsed == parsed
    assert raw_again is None


def test_extract_title_skips_chord_and_bracket_lines():
    assert extract_title(SONG) == "My Little Song"
    assert extract_title("[Intro]\nC  G\nReal Title") == "Real Title"
    assert extract_title("C  G\n") == ""


# ---------------------------------------------------------------------------
# Rendering


def test_text_rendering_round_trips_the_chart():
    """parse -> render must be the identity on a well-formed chart."""
    assert render_chords_and_lyrics_to_text(SONG) == SONG


def test_render_chords_and_lyrics_text_matches_direct_renderer():
    assert render_chords_and_lyrics(SONG, to="text") == (
        render_chords_and_lyrics_to_text(SONG)
    )
    assert render_chords_and_lyrics(SONG, to="txt") == (
        render_chords_and_lyrics_to_text(SONG)
    )


def test_render_chords_and_lyrics_requires_output_path_for_pdf():
    with pytest.raises(ValueError, match="output_path is required"):
        render_chords_and_lyrics(SONG, to="pdf")


def test_render_chords_and_lyrics_rejects_unknown_format():
    with pytest.raises(ValueError, match="Unknown render format"):
        render_chords_and_lyrics(SONG, to="markdown")


def test_render_chords_and_lyrics_to_pdf_writes_a_pdf(tmp_path):
    output = tmp_path / "song.pdf"
    render_chords_and_lyrics(SONG, to="pdf", output_path=str(output))
    assert output.exists()
    assert output.read_bytes().startswith(b"%PDF")


# ---------------------------------------------------------------------------
# Filtering


def test_is_likely_lyrics_classification():
    assert is_likely_lyrics("")  # blank lines are intentional spacing
    assert is_likely_lyrics("Hello there my friend")
    assert not is_likely_lyrics("[Verse 1]")
    assert not is_likely_lyrics("C       G")
    assert not is_likely_lyrics("CHORUS")
    assert not is_likely_lyrics("-------")


def test_remove_non_lyrics_drops_section_markers_by_default():
    cleaned = remove_non_lyrics(SONG)
    assert "[Verse 1]" not in cleaned
    assert "[Chorus]" not in cleaned
    assert "Hello there my friend" in cleaned
    assert "C       G" in cleaned  # chord lines survive


def test_remove_non_lyrics_keeps_section_markers_when_asked():
    """``keep_metadata=True`` must actually keep ``[Verse]``-style markers.

    Before this test the flag was dead: metadata lines were rejected by the
    ``is_likely_lyrics`` gate before the ``keep_metadata_lines`` branch was
    ever reached, so both settings produced identical output.
    """
    kept = remove_non_lyrics(SONG, keep_metadata=True)
    assert "[Verse 1]" in kept
    assert "[Chorus]" in kept
    assert kept != remove_non_lyrics(SONG, keep_metadata=False)


def test_filter_non_lyrics_preserves_section_order():
    sections = filter_non_lyrics(SONG, keep_metadata_lines=True)
    lyrics = [s["lyrics"] for s in sections]
    assert lyrics.index("[Verse 1]") < lyrics.index("[Chorus]")


# ---------------------------------------------------------------------------
# Packing


def test_pack_song_lines_combines_short_chordless_lines():
    packed = pack_song_lines("aa\nbb\ncc", max_line_length=80)
    assert [s["lyrics"] for s in packed] == ["aa bb cc"]
    assert pack_song_text("aa\nbb\ncc", max_length=80) == "aa bb cc"


def test_pack_song_lines_never_merges_across_a_chord_section():
    """Chord alignment is column-based; merging would desynchronize it."""
    packed = pack_song_lines(SONG, max_line_length=200)
    chord_sections = [s for s in packed if s["chords"]]
    assert [s["lyrics"] for s in chord_sections] == [
        "Hello there my friend",
        "How are you today",
        "Sing it loud",
    ]


def test_pack_song_lines_respects_max_line_length():
    packed = pack_song_lines("aaaa\nbbbb\ncccc", max_line_length=9)
    assert all(len(s["lyrics"]) <= 9 for s in packed)


# ---------------------------------------------------------------------------
# Rendering config


def test_complete_font_spec_merges_over_defaults():
    spec = complete_font_spec({"size": 20}, default_lyrics_font)
    assert spec.size == 20
    assert spec.name == default_lyrics_font["name"]


def test_complete_font_spec_rejects_invalid_values():
    with pytest.raises(ValueError, match="Invalid font spec"):
        complete_font_spec({"size": "not a number"}, default_lyrics_font)


def test_resolve_page_size_accepts_names_case_insensitively():
    assert resolve_page_size("A4") == resolve_page_size("a4")
    assert resolve_page_size("letter") == resolve_page_size("LETTER")


def test_resolve_page_size_passes_through_tuples():
    assert resolve_page_size((100, 200)) == (100, 200)


def test_resolve_page_size_rejects_unknown_names():
    with pytest.raises(ValueError, match="Unknown page size"):
        resolve_page_size("PAPYRUS")
