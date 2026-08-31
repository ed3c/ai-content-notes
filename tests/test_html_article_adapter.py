"""The text plane an anchor indexes has to be one function's fixed output."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import html_article_adapter as article  # noqa: E402


def test_script_and_style_bodies_never_reach_the_text() -> None:
    text = article.extract_text(
        "<p>kept</p><script>var secret = 1;</script><style>p{color:red}</style><p>also kept</p>"
    )
    assert "secret" not in text
    assert "color:red" not in text
    assert text == "kept\n\nalso kept\n"


def test_block_boundaries_become_newlines_and_inline_ones_do_not() -> None:
    """A block open and the preceding block close each emit one newline."""
    assert article.extract_text("<p>one</p><p>two</p>") == "one\n\ntwo\n"
    assert article.extract_text("<p>in<em>li</em>ne</p>") == "inline\n"
    assert article.extract_text("<li>a<br>b</li>") == "a\nb\n"


def test_entities_are_unescaped_after_tags_are_removed() -> None:
    """An escaped tag in the prose must stay prose, never become markup."""
    assert article.extract_text("<p>write &lt;div&gt; like this</p>") == "write <div> like this\n"
    assert article.extract_text("<p>a &amp;&amp; b</p>") == "a && b\n"


def test_whitespace_is_collapsed_to_one_shape() -> None:
    assert article.extract_text("<p>a   \t b</p>\n\n\n<p>c</p>") == "a b\n\nc\n"
    assert article.extract_text("<p>  padded  </p>") == "padded\n"
    assert article.extract_text("<div><div><div>deep</div></div></div>") == "deep\n"


def test_extraction_is_a_function_of_its_input_only() -> None:
    markup = (REPOSITORY_ROOT / "sources" / "sqlite-testing" / "article.raw.html").read_text(
        encoding="utf-8"
    )
    assert article.extract_text(markup) == article.extract_text(markup)


def test_check_mode_catches_a_stale_text_plane(tmp_path: Path) -> None:
    source = tmp_path / "a.html"
    source.write_text("<p>current</p>", encoding="utf-8")
    stale = tmp_path / "a.txt"
    stale.write_text("previous\n", encoding="utf-8")

    with pytest.raises(article.ArticleError, match="stale"):
        article.main(["--html", str(source), "--check", str(stale)])

    assert article.main(["--html", str(source), "--output", str(stale)]) == 0
    assert article.main(["--html", str(source), "--check", str(stale)]) == 0


def test_absent_inputs_and_ambiguous_modes_fail_closed(tmp_path: Path) -> None:
    source = tmp_path / "a.html"
    source.write_text("<p>x</p>", encoding="utf-8")
    with pytest.raises(article.ArticleError, match="missing retained HTML"):
        article.main(["--html", str(tmp_path / "absent.html"), "--output", str(tmp_path / "o.txt")])
    with pytest.raises(article.ArticleError, match="exactly one"):
        article.main(["--html", str(source)])
    with pytest.raises(article.ArticleError, match="missing text plane"):
        article.main(["--html", str(source), "--check", str(tmp_path / "absent.txt")])
