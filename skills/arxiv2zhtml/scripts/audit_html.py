#!/usr/bin/env python3
"""Audit structural and offline-integrity differences between two HTML files.

Uses only the Python standard library. It is intentionally conservative: the
report supplies deterministic evidence, while task-specific authorization and
semantic review remain human decisions.
"""

from __future__ import annotations

import argparse
import base64
import collections
import difflib
import hashlib
import html.parser
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote_to_bytes, urlparse

SKIP_TEXT = {"script", "style", "noscript", "template"}
BIB_HINT = re.compile(r"(?:^|[-_:])(bib|bibliography|reference|ref)(?:[-_:]|$)", re.I)
FOOT_HINT = re.compile(r"(?:^|[-_:])(footnote|footnotes|fn)(?:[-_:]|$)", re.I)
CITE_HINT = re.compile(r"(?:^|[-_:])(cite|citation)(?:[-_:]|$)", re.I)
RESOURCE_ATTRS = {"src", "srcset", "poster"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_space(text: str) -> str:
    return " ".join(text.split())


def attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    return {k.lower(): (v or "") for k, v in attrs}


def stable_attrs(attrs: list[tuple[str, str | None]], omit: Iterable[str] = ()) -> str:
    ignored = set(omit)
    return " ".join(f'{k}="{v or ""}"' for k, v in sorted(attrs) if k not in ignored)


def decode_data_uri(uri: str) -> tuple[str, bytes] | None:
    if not uri.startswith("data:") or "," not in uri:
        return None
    header, payload = uri[5:].split(",", 1)
    mime = header.split(";", 1)[0] or "text/plain"
    try:
        raw = base64.b64decode(payload, validate=False) if ";base64" in header.lower() else unquote_to_bytes(payload)
    except (ValueError, base64.binascii.Error):
        return None
    return mime, raw


class AuditParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: collections.Counter[str] = collections.Counter()
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.visible_chunks: list[str] = []
        self.hidden_depth = 0
        self.stack: list[str] = []
        self.math_depth = 0
        self.math_buffer: list[str] = []
        self.math_hashes: list[str] = []
        self.tables: list[dict[str, Any]] = []
        self.table: dict[str, Any] | None = None
        self.row: list[dict[str, int]] | None = None
        self.images: list[dict[str, Any]] = []
        self.internal_links: list[dict[str, str]] = []
        self.external_links: list[str] = []
        self.external_dependencies: list[dict[str, str]] = []
        self.bibliography_ids: set[str] = set()
        self.footnote_ids: set[str] = set()
        self.citation_containers = 0
        self.figure_ids: list[str] = []
        self.styles: list[str] = []
        self.style_depth = 0
        self.style_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        data = attrs_dict(attrs)
        self.tags[tag] += 1
        self.stack.append(tag)
        if tag in SKIP_TEXT:
            self.hidden_depth += 1
        if tag == "style":
            self.style_depth += 1
            self.style_buffer = []
        ident = data.get("id", "")
        if ident:
            if ident in self.ids:
                self.duplicate_ids.add(ident)
            self.ids.add(ident)
            if BIB_HINT.search(ident):
                self.bibliography_ids.add(ident)
            if FOOT_HINT.search(ident):
                self.footnote_ids.add(ident)
        classes = data.get("class", "")
        role = data.get("role", "")
        if CITE_HINT.search(" ".join((ident, classes, role))):
            self.citation_containers += 1
        if tag == "figure":
            self.figure_ids.append(ident)
        if tag == "math":
            self.math_depth = 1
            self.math_buffer = [f"<math {stable_attrs(attrs)}>" if attrs else "<math>"]
        elif self.math_depth:
            self.math_depth += 1
            self.math_buffer.append(f"<{tag} {stable_attrs(attrs)}>" if attrs else f"<{tag}>")
        if tag == "table":
            self.table = {"id": ident, "rows": [], "caption": ""}
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            try:
                rowspan = max(1, int(data.get("rowspan", "1")))
                colspan = max(1, int(data.get("colspan", "1")))
            except ValueError:
                rowspan, colspan = 1, 1
            self.row.append({"rowspan": rowspan, "colspan": colspan, "header": int(tag == "th")})
        if tag == "img":
            src = data.get("src", "")
            decoded = decode_data_uri(src)
            item: dict[str, Any] = {"id": ident, "alt": data.get("alt", ""), "is_data_uri": bool(decoded), "source": src[:120]}
            if decoded:
                item.update({"mime": decoded[0], "byte_length": len(decoded[1]), "sha256": sha256(decoded[1])})
            self.images.append(item)
        if tag == "a":
            href = data.get("href", "")
            if href.startswith("#"):
                self.internal_links.append({"source": ident, "target": href[1:]})
            elif href and urlparse(href).scheme in {"http", "https"}:
                self.external_links.append(href)
        self._check_dependencies(tag, data)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.math_depth:
            self.math_buffer.append(f"</{tag}>")
            self.math_depth -= 1
            if self.math_depth == 0:
                canonical = normalize_space("".join(self.math_buffer))
                self.math_hashes.append(sha256(canonical.encode("utf-8")))
                self.math_buffer = []
        if tag == "tr" and self.row is not None and self.table is not None:
            self.table["rows"].append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.table["grid"] = table_grid_signature(self.table["rows"])
            self.tables.append(self.table)
            self.table = None
        if tag == "style" and self.style_depth:
            self.styles.append("".join(self.style_buffer))
            self.style_depth -= 1
            self.style_buffer = []
        if tag in SKIP_TEXT and self.hidden_depth:
            self.hidden_depth -= 1
        if self.stack:
            if self.stack[-1] == tag:
                self.stack.pop()
            elif tag in self.stack:
                self.stack = self.stack[: len(self.stack) - 1 - self.stack[::-1].index(tag)]

    def handle_data(self, data: str) -> None:
        if self.style_depth:
            self.style_buffer.append(data)
        if self.math_depth:
            self.math_buffer.append(normalize_space(data))
        if not self.hidden_depth and not self.math_depth:
            text = normalize_space(data)
            if text:
                self.visible_chunks.append(text)

    def _check_dependencies(self, tag: str, data: dict[str, str]) -> None:
        for attr in RESOURCE_ATTRS:
            value = data.get(attr, "").strip()
            if not value:
                continue
            if attr == "srcset":
                values = [seg.split()[0] for seg in (part.strip() for part in value.split(",")) if seg]
            else:
                values = [value]
            for candidate in values:
                parsed = urlparse(candidate)
                if candidate.startswith("//") or parsed.scheme in {"http", "https"}:
                    self.external_dependencies.append({"tag": tag, "attribute": attr, "url": candidate})
        if tag == "link":
            rel = data.get("rel", "").lower()
            href = data.get("href", "")
            if any(word in rel for word in ("stylesheet", "preload", "font", "icon")) and (href.startswith("//") or urlparse(href).scheme in {"http", "https"}):
                self.external_dependencies.append({"tag": tag, "attribute": "href", "url": href})
        if tag == "script":
            src = data.get("src", "")
            if src:
                self.external_dependencies.append({"tag": tag, "attribute": "src", "url": src})

    def finish(self) -> None:
        css_url = re.compile(r"(?:@import\s+(?:url\()?|url\()\s*['\"]?([^'\")\s;]+)", re.I)
        for style in self.styles:
            for value in css_url.findall(style):
                if value.startswith("//") or urlparse(value).scheme in {"http", "https"}:
                    self.external_dependencies.append({"tag": "style", "attribute": "css-url", "url": value})


def table_grid_signature(rows: list[list[dict[str, int]]]) -> dict[str, Any]:
    occupied: dict[tuple[int, int], bool] = {}
    widths: list[int] = []
    spans: list[list[tuple[int, int, int]]] = []
    for r_index, row in enumerate(rows):
        col = 0
        row_spans: list[tuple[int, int, int]] = []
        for cell in row:
            while occupied.get((r_index, col)):
                col += 1
            rs, cs = cell["rowspan"], cell["colspan"]
            row_spans.append((rs, cs, cell["header"]))
            for rr in range(r_index, r_index + rs):
                for cc in range(col, col + cs):
                    occupied[(rr, cc)] = True
            col += cs
        width = max((cc for rr, cc in occupied if rr == r_index), default=-1) + 1
        widths.append(width)
        spans.append(row_spans)
    return {"row_count": len(rows), "row_widths": widths, "cells": spans}


def parse_file(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    parser = AuditParser()
    parser.feed(text)
    parser.close()
    parser.finish()
    visible = "\n".join(parser.visible_chunks)
    broken = sorted({edge["target"] for edge in parser.internal_links if edge["target"] and edge["target"] not in parser.ids})
    return {
        "path": str(path.resolve()),
        "file_sha256": sha256(raw),
        "bytes": len(raw),
        "tag_counts": dict(sorted(parser.tags.items())),
        "ids": sorted(parser.ids),
        "duplicate_ids": sorted(parser.duplicate_ids),
        "visible_text": visible,
        "visible_text_sha256": sha256(visible.encode("utf-8")),
        "mathml": {"count": len(parser.math_hashes), "hashes": parser.math_hashes},
        "tables": parser.tables,
        "figures": {"count": parser.tags["figure"], "ids": parser.figure_ids},
        "images": parser.images,
        "bibliography_ids": sorted(parser.bibliography_ids),
        "footnote_ids": sorted(parser.footnote_ids),
        "citation_containers": parser.citation_containers,
        "internal_links": parser.internal_links,
        "broken_internal_targets": broken,
        "external_links": sorted(set(parser.external_links)),
        "external_dependencies": parser.external_dependencies,
    }


def text_diff(a: str, b: str, limit: int) -> dict[str, Any]:
    a_lines, b_lines = a.splitlines(), b.splitlines()
    changes = list(difflib.unified_diff(a_lines, b_lines, fromfile="baseline-visible", tofile="candidate-visible", lineterm=""))
    return {"changed": a != b, "diff_line_count": len(changes), "truncated": len(changes) > limit, "preview": changes[:limit]}


def compare(base: dict[str, Any], cand: dict[str, Any], diff_limit: int) -> dict[str, Any]:
    fields = ["tag_counts", "ids", "mathml", "tables", "figures", "bibliography_ids", "footnote_ids", "citation_containers", "internal_links"]
    differences = {field: {"equal": base[field] == cand[field]} for field in fields}
    base_hashes = [item.get("sha256") for item in base["images"]]
    cand_hashes = [item.get("sha256") for item in cand["images"]]
    differences["image_hashes"] = {"equal": base_hashes == cand_hashes, "baseline": base_hashes, "candidate": cand_hashes}
    differences["visible_text"] = text_diff(base["visible_text"], cand["visible_text"], diff_limit)
    blockers: list[str] = []
    if cand["duplicate_ids"]:
        blockers.append("candidate contains duplicate IDs")
    if cand["broken_internal_targets"]:
        blockers.append("candidate contains broken internal fragment targets")
    if cand["external_dependencies"]:
        blockers.append("candidate contains external rendering dependencies")
    if any(not item["is_data_uri"] for item in cand["images"]):
        blockers.append("candidate contains images that are not data URIs")
    return {"differences": differences, "candidate_blockers": blockers}


def summarized(doc: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in doc.items() if key != "visible_text"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare baseline and candidate HTML structure, embedded resources, links, and visible text; output JSON without starting a server.")
    ap.add_argument("baseline", type=Path, help="immutable source or previous-version HTML")
    ap.add_argument("candidate", type=Path, help="new candidate HTML")
    ap.add_argument("--json", dest="json_path", type=Path, help="write the JSON report to this path")
    ap.add_argument("--diff-limit", type=int, default=200, help="maximum visible-text diff lines included (default: 200)")
    ap.add_argument("--strict-layout", action="store_true", help="also fail when visible text, MathML, tables, figures, image hashes, bibliography/footnotes, citation edges, or IDs differ")
    args = ap.parse_args()
    for path in (args.baseline, args.candidate):
        if not path.is_file():
            ap.error(f"file not found: {path}")
    baseline = parse_file(args.baseline)
    candidate = parse_file(args.candidate)
    comparison = compare(baseline, candidate, max(0, args.diff_limit))
    strict_fields = ["ids", "mathml", "tables", "figures", "image_hashes", "bibliography_ids", "footnote_ids", "citation_containers", "internal_links"]
    strict_failures = [field for field in strict_fields if not comparison["differences"][field]["equal"]]
    if args.strict_layout and comparison["differences"]["visible_text"]["changed"]:
        strict_failures.append("visible_text")
    report = {
        "schema_version": 1,
        "baseline": summarized(baseline),
        "candidate": summarized(candidate),
        "comparison": comparison,
        "strict_layout_failures": strict_failures,
        "notes": [
            "Visible-text differences require a task-specific whitelist and semantic review.",
            "The parser checks deterministic structure but does not replace Chromium file:// visual acceptance.",
            "External hyperlinks may remain; external rendering dependencies are blockers.",
        ],
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json_path:
        args.json_path.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    failed = bool(comparison["candidate_blockers"] or (args.strict_layout and strict_failures))
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
