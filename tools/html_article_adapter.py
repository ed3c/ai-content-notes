#!/usr/bin/env python3
"""Turn a retained HTML article into the exact text its evidence anchors index.

A card anchored at `char:1234..1300` is only evidence if that offset means one
thing forever. Retaining the fetched HTML is not enough: every reader would
strip its markup slightly differently, and the offsets would move. So the text
plane is an artifact in its own right, retained beside the HTML and bound by
the same `source-manifest.json`, and this adapter is the one function that
produces it.

The extraction is deliberately dull, because a clever one would be a second
thing to keep stable:

- `<script>` and `<style>` bodies are dropped entirely;
- a block-level tag boundary becomes a newline, an inline one becomes nothing;
- entities are unescaped once, after tag removal, so an escaped `&lt;div&gt;`
  in the prose can never become a tag;
- horizontal whitespace collapses to one space, three or more newlines collapse
  to two, trailing spaces go, and the file ends with exactly one newline.

Determinism is the whole contract, so it is asserted rather than described:
`--check FILE` re-extracts and compares bytes, and `tests/test_html_article_adapter.py`
holds the retained SQLite article to its retained text plane.

Usage:
    python3 tools/html_article_adapter.py --html IN.html --output OUT.txt
    python3 tools/html_article_adapter.py --html IN.html --check OUT.txt
"""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Sequence

DROP = {"script", "style", "noscript", "template"}
BLOCK = {
    "address", "article", "aside", "blockquote", "br", "dd", "div", "dl", "dt",
    "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3",
    "h4", "h5", "h6", "header", "hr", "li", "main", "nav", "ol", "p", "pre",
    "section", "table", "tbody", "td", "tfoot", "th", "thead", "tr", "ul",
}


class ArticleError(RuntimeError):
    """Raised when the retained text plane cannot be produced or verified."""


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.chunks: list[str] = []
        self._muted = 0

    def handle_starttag(self, tag: str, attrs: object) -> None:
        del attrs
        if tag in DROP:
            self._muted += 1
        elif tag in BLOCK:
            self.chunks.append("\n")

    def handle_startendtag(self, tag: str, attrs: object) -> None:
        del attrs
        if tag in BLOCK:
            self.chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in DROP:
            self._muted = max(0, self._muted - 1)
        elif tag in BLOCK:
            self.chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._muted:
            self.chunks.append(data)

    def handle_entityref(self, name: str) -> None:
        if not self._muted:
            self.chunks.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self._muted:
            self.chunks.append(f"&#{name};")


def extract_text(markup: str) -> str:
    parser = _TextExtractor()
    parser.feed(markup)
    parser.close()
    text = html.unescape("".join(parser.chunks))
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace(" ", " ")
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract the text plane of a retained article")
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path, help="verify an existing text plane byte for byte")
    args = parser.parse_args(argv)

    if not args.html.is_file():
        raise ArticleError(f"missing retained HTML: {args.html}")
    if (args.output is None) == (args.check is None):
        raise ArticleError("give exactly one of --output or --check")

    payload = args.html.read_bytes()
    text = extract_text(payload.decode("utf-8"))

    if args.check is not None:
        if not args.check.is_file():
            raise ArticleError(f"missing text plane to check: {args.check}")
        if args.check.read_text(encoding="utf-8") != text:
            raise ArticleError(f"retained text plane is stale: {args.check}")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")

    print(
        f'{{"html_sha256": "{sha256_bytes(payload)}", '
        f'"text_sha256": "{sha256_bytes(text.encode("utf-8"))}", '
        f'"characters": {len(text)}}}'
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ArticleError as error:
        print(f"article adapter refused: {error}", file=sys.stderr)
        raise SystemExit(2) from error
