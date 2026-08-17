"""Run the doctests of the credential-free modules.

``sung/__init__.py``'s module docstring is a live tutorial: it searches
Spotify, creates a playlist and deletes it. Those examples are documentation,
not tests -- they need OAuth (an interactive browser consent) and they mutate a
real account, so they are deliberately not executed here.

The remaining modules' doctests are pure and are run as real gates, which is
why they are listed explicitly rather than swept up by ``--doctest-modules``:
an explicit list cannot quietly start executing a live example that someone
adds to the package docstring later.
"""

import doctest
import importlib

import pytest

CREDENTIAL_FREE_MODULES = [
    "sung.util",
    "sung.playlists",
    "sung.chords_and_lyrics",
    "sung.tools",
]

OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE


@pytest.mark.parametrize("module_name", CREDENTIAL_FREE_MODULES)
def test_module_doctests(module_name):
    module = importlib.import_module(module_name)
    results = doctest.testmod(module, optionflags=OPTIONFLAGS, verbose=False)
    assert results.failed == 0, f"{results.failed} doctest failure(s) in {module_name}"


def test_credential_free_modules_have_doctests():
    """Guard against the list above silently becoming a no-op.

    If a module loses all its examples the parametrized test still passes
    (zero failures out of zero), so assert the examples exist.
    """
    finder = doctest.DocTestFinder()
    for module_name in CREDENTIAL_FREE_MODULES:
        module = importlib.import_module(module_name)
        examples = sum(len(test.examples) for test in finder.find(module))
        assert examples > 0, f"{module_name} has no doctest examples"
