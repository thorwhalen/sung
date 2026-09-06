"""Check the *documented* calls of ``render_chords_and_lyrics`` against its signature.

``render_chords_and_lyrics`` ends in ``**kwargs`` and its ``to='text'`` branch
forwards nothing, so a keyword that does not exist is silently discarded: no
``TypeError``, no warning, just an unfiltered result for whoever copied the
example. That is precisely how ``filter_non_lyrics=True`` came to be
documented, in the README and in the module docstring alike -- the real
parameter is ``apply_filter_non_lyrics``, and ``filter_non_lyrics`` is a
module-level *function*.

Nothing caught it because neither form of documentation was executable: the
README's fenced blocks are never run, and the docstring examples carried
``# doctest: +SKIP``. So these tests read the documentation as data and check
every keyword in it against the signatures that actually consume keywords.
This is the cheap half of the guard; the other half is that the ``to='text'``
docstring examples are now real, unskipped doctests (see
``tests/test_doctests.py``).
"""

import ast
import doctest
import re
from inspect import Parameter, signature
from pathlib import Path

import pytest

import sung.chords_and_lyrics as chords_and_lyrics

DOCUMENTED_FUNCTION = "render_chords_and_lyrics"

# ``render_chords_and_lyrics`` passes its ``**kwargs`` on to whichever renderer
# the ``to=`` argument selects, so a documented keyword is legitimate if any of
# these three accepts it.
KEYWORD_CONSUMERS = (
    chords_and_lyrics.render_chords_and_lyrics,
    chords_and_lyrics.render_chords_and_lyrics_to_pdf,
    chords_and_lyrics.render_chords_and_lyrics_to_text,
)

README_PATH = Path(__file__).resolve().parent.parent / "README.md"

PYTHON_BLOCK_RE = re.compile(r"^```python\n(.*?)^```", re.MULTILINE | re.DOTALL)


def _accepted_keywords() -> set:
    """Every keyword name the documented function can really honour."""
    accepted = set()
    for func in KEYWORD_CONSUMERS:
        accepted.update(
            name
            for name, param in signature(func).parameters.items()
            if param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
        )
    return accepted


def _documented_keywords(source: str, origin: str) -> set:
    """Keyword names used in calls to the documented function in ``source``.

    ``origin`` only names the snippet in the error raised by an example that
    does not even parse -- documentation that cannot be parsed cannot be
    checked, and silently passing it would defeat the point of these tests.
    """

    def called_name(node: ast.Call) -> str:
        func = node.func
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return ""

    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise AssertionError(f"{origin} does not parse as Python: {error}") from error

    keywords = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and called_name(node) == DOCUMENTED_FUNCTION:
            keywords.update(kw.arg for kw in node.keywords if kw.arg is not None)
    return keywords


def _readme_blocks() -> list:
    """The README's ``python`` blocks that call the documented function."""
    if not README_PATH.is_file():  # pragma: no cover - README ships with the sdist
        pytest.skip(f"{README_PATH.name} is not part of this install")
    return [
        block
        for block in PYTHON_BLOCK_RE.findall(README_PATH.read_text())
        if DOCUMENTED_FUNCTION in block
    ]


def test_readme_blocks_are_present():
    """Guard against the block regex silently matching nothing."""
    assert _readme_blocks()


def test_readme_keywords_exist():
    """A README keyword that no renderer accepts is a silently wrong example."""
    accepted = _accepted_keywords()
    for number, block in enumerate(_readme_blocks(), 1):
        origin = f"README example {number}"
        unknown = _documented_keywords(block, origin) - accepted
        assert not unknown, f"{origin} uses unknown keyword(s) {sorted(unknown)}"


def test_docstring_keywords_exist():
    """Same check for the module docstring, including any ``+SKIP``ped example."""
    accepted = _accepted_keywords()
    docstring = chords_and_lyrics.__doc__ or ""
    examples = doctest.DocTestParser().get_examples(docstring)
    for number, example in enumerate(examples, 1):
        origin = f"docstring example {number}"
        unknown = _documented_keywords(example.source, origin) - accepted
        assert not unknown, f"{origin} uses unknown keyword(s) {sorted(unknown)}"
