#!/usr/bin/env python3
"""Fetch figures from the latest arXiv HTML page and output a Markdown figure map.

Usage:
    python fetch_arxiv_figures.py 2512.23851 [--out assets/] [--inline]

- Resolves the bare arXiv id to its latest HTML version.
- Downloads every content figure (<img class="ltx_graphics">) into --out
  (default: ./assets/), skipping site UI icons.
- Prints a Markdown map: Figure N -> local path / remote URL, with caption.
- With --inline, emits ready-to-paste Markdown image tags using remote URLs
  (no download). Remote URLs are stable and let Zhihu/CSDN hotlink the image.
"""
import argparse
import html
import os
import re
import sys
import urllib.parse
import urllib.request
import urllib.error
from html.parser import HTMLParser

ARXIV_HTML = "https://arxiv.org/html/{aid}"
ID_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")

import unicodedata
# Mathematical alphanumeric symbols (bold 𝑯, italic 𝛀, etc.) decompose to
# their base letter under NFKD. Invisible math operators (U+2061 FUNCTION
# APPLICATION, U+2062 INVISIBLE TIMES) are dropped.
_INVISIBLE = {"\u2061", "\u2062", "\u2063", "\u2064"}
def _strip_mathalnum(s: str) -> str:
    out = []
    for ch in s:
        if ch in _INVISIBLE:
            continue
        if 0x1D400 <= ord(ch) <= 0x1D7FF:
            out.append(unicodedata.normalize("NFKD", ch)[0])
        else:
            out.append(ch)
    return "".join(out)


def clean_caption(text: str) -> str:
    t = _strip_mathalnum(html.unescape(text or ""))
    # LaTeXML emits both a Unicode glyph and a \command{...} text fallback;
    # drop the LaTeX entirely so we do not render the same symbol twice.
    t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})*", "", t)
    t = t.replace("\\", "")
    t = re.sub(r"[$^{}]", "", t)
    t = t.replace("−", "-").replace("–", "-")
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\s+([，。、：；）])", r"\1", t)
    return t.strip(" ()·-")


def resolve_latest(aid: str) -> tuple[str, str]:
    """Return (final_url, versioned_aid) for an arXiv id.

    A bare id (no 'vN') already serves the latest version from the same URL;
    arxiv answers it with the versioned <base> so we read it from the HTML.
    """
    url = ARXIV_HTML.format(aid=aid)
    req = urllib.request.Request(url, headers={"User-Agent": "paper-blog-skill/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        final_url = r.geturl()
        data = r.read().decode("utf-8", errors="replace")
    m = re.search(r"arXiv:(\d{4}\.\d{4,5}v\d+)", data)
    versioned = m.group(1) if m else aid
    return final_url, versioned, data


class FigureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.figures = []
        self._in_fig = False
        self._in_cap = False
        self._cur = None
        self._cap_text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "figure" and "ltx_figure" in (a.get("class") or ""):
            self._in_fig = True
            self._cur = {"id": a.get("id", ""), "src": None, "alt": ""}
        elif self._in_fig and tag == "img" and "ltx_graphics" in (a.get("class") or ""):
            self._cur["src"] = a.get("src")
            self._cur["alt"] = a.get("alt", "")
        elif self._in_fig and tag == "figcaption":
            self._in_cap = True

    def handle_endtag(self, tag):
        if tag == "figcaption":
            self._in_cap = False
        elif tag == "figure" and self._in_fig:
            if self._cur and self._cur["src"]:
                self._cur["caption"] = clean_caption("".join(self._cap_text))
                self.figures.append(self._cur)
            self._in_fig = False
            self._cur = None
            self._cap_text = []

    def handle_data(self, data):
        if self._in_cap:
            self._cap_text.append(data)


def absolutize(src: str, base_url: str) -> str:
    if src.startswith(("http://", "https://")):
        return src
    return urllib.parse.urljoin(base_url + "/", src)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arxiv_id", help="arXiv id, with or without version (e.g. 2512.23851)")
    ap.add_argument("--out", default="assets", help="directory for downloaded images")
    ap.add_argument("--inline", action="store_true",
                    help="output remote-URL Markdown only; do not download")
    args = ap.parse_args()

    aid = args.arxiv_id.strip()
    if not ID_RE.match(aid):
        sys.exit(f"Not a valid arXiv id: {aid!r}")

    print(f"Resolving latest version for arXiv:{aid} ...", file=sys.stderr)
    final_url, versioned, data = resolve_latest(aid)
    print(f"Latest: {versioned}  ({final_url})", file=sys.stderr)

    p = FigureParser()
    p.feed(data)
    if not p.figures:
        sys.exit("No content figures found on the arXiv HTML page.")

    if not args.inline:
        os.makedirs(args.out, exist_ok=True)

    print(f"\n# Figure map — arXiv:{versioned}\n")
    for i, fig in enumerate(p.figures, 1):
        abs_url = absolutize(fig["src"], final_url.rsplit("/", 1)[0])
        if args.inline:
            print(f"## Figure {i}")
            print(f"![Figure {i}]({abs_url})")
            if fig["caption"]:
                print(f"\n*{fig['caption']}*\n")
            continue

        ext = os.path.splitext(urllib.parse.urlparse(abs_url).path)[1] or ".png"
        local_name = f"figure_{i:02d}{ext}"
        local_path = os.path.join(args.out, local_name)
        try:
            urllib.request.urlretrieve(abs_url, local_path)
            size = os.path.getsize(local_path)
            print(f"## Figure {i}  `{local_path}` ({size} bytes)  id={fig['id']}")
            print(f"![Figure {i}]({args.out}/{local_name})")
        except (urllib.error.URLError, OSError) as e:
            print(f"## Figure {i}  DOWNLOAD FAILED ({e}) — using remote URL", file=sys.stderr)
            print(f"![Figure {i}]({abs_url})")
        if fig["caption"]:
            print(f"\n*{fig['caption']}*\n")

    print(f"\n{len(p.figures)} figure(s) processed.", file=sys.stderr)


if __name__ == "__main__":
    main()
