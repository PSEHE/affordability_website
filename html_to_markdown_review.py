#!/usr/bin/env python3
"""Extract editable page text from the website HTML into simple Markdown files."""

from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


WEBSITE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = WEBSITE_DIR / "markdown_for_review"
DEFAULT_INPUTS = [WEBSITE_DIR / "home-page.html"]
DEFAULT_INPUTS.extend(sorted((WEBSITE_DIR / "pages").glob("*.html")))

VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}

SKIP_TAGS = {
    "aside",
    "button",
    "canvas",
    "footer",
    "form",
    "iframe",
    "nav",
    "noscript",
    "script",
    "style",
    "svg",
}

BLOCK_TAGS = {
    "address",
    "article",
    "blockquote",
    "dd",
    "details",
    "div",
    "dl",
    "dt",
    "figcaption",
    "figure",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hr",
    "li",
    "main",
    "ol",
    "p",
    "pre",
    "section",
    "summary",
    "table",
    "ul",
}


@dataclass
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["Node | str"] = field(default_factory=list)


class TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.root = Node("[document]")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        node = Node(tag, {name.lower(): value or "" for name, value in attrs})
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(html.unescape(data))

    def handle_entityref(self, name: str) -> None:
        self.handle_data(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.handle_data(f"&#{name};")


def class_names(node: Node) -> set[str]:
    return set(node.attrs.get("class", "").split())


def has_class(node: Node, name: str) -> bool:
    return name in class_names(node)


def find_all(node: Node, predicate) -> list[Node]:
    matches: list[Node] = []
    if predicate(node):
        matches.append(node)
    for child in node.children:
        if isinstance(child, Node):
            matches.extend(find_all(child, predicate))
    return matches


def split_html_documents(text: str) -> list[str]:
    starts = [match.start() for match in re.finditer(r"(?i)<!doctype\s+html\b", text)]
    if len(starts) <= 1:
        return [text]
    starts.append(len(text))
    return [text[starts[index] : starts[index + 1]] for index in range(len(starts) - 1)]


def parse_html(text: str) -> Node:
    parser = TreeBuilder()
    parser.feed(text)
    parser.close()
    return parser.root


def selected_content(root: Node, source: Path) -> list[Node]:
    if source.name == "home-page.html":
        hero = find_all(root, lambda node: node.tag == "header" and has_class(node, "hero"))
        sections = find_all(root, lambda node: node.tag == "section")
        return hero[:1] + sections

    page_header = find_all(root, lambda node: node.tag == "header" and has_class(node, "page-header"))
    page_main = find_all(root, lambda node: node.tag == "main" and has_class(node, "page-content"))
    if page_header or page_main:
        return page_header[:1] + page_main[:1]

    body = find_all(root, lambda node: node.tag == "body")
    return body[:1] if body else [root]


def should_skip(node: Node) -> bool:
    if node.tag in SKIP_TAGS:
        return True

    classes = class_names(node)
    skip_classes = {
        "breadcrumbs",
        "btn",
        "card-link",
        "hero-actions",
        "mobile-menu-toggle",
        "source-icon",
        "step-circle",
        "step-line",
        "step-tag",
        "toc-sidebar",
    }
    if classes & skip_classes:
        return True

    return False


def is_block_link(node: Node) -> bool:
    return node.tag == "a" and any(
        isinstance(child, Node) and child.tag in BLOCK_TAGS for child in node.children
    )


def clean_inline(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([(])\s+", r"\1", text)
    text = re.sub(r"\s+([)])", r"\1", text)
    return text.strip()


def render_inline_children(node: Node) -> str:
    parts = [render_inline(child) for child in node.children]
    return clean_inline(" ".join(part for part in parts if part))


def render_inline(item: Node | str) -> str:
    if isinstance(item, str):
        return clean_inline(item)

    if should_skip(item):
        return ""

    if item.tag == "br":
        return "\n"
    if item.tag == "img":
        return ""
    if item.tag in {"strong", "b"}:
        text = render_inline_children(item)
        return f"**{text}**" if text else ""
    if item.tag in {"em", "i"}:
        text = render_inline_children(item)
        return f"*{text}*" if text else ""
    if item.tag == "code":
        text = render_inline_children(item)
        return f"`{text}`" if text else ""
    if item.tag == "sub":
        text = render_inline_children(item)
        return f"~{text}~" if text else ""
    if item.tag == "sup":
        text = render_inline_children(item)
        return f"^{text}^" if text else ""
    if item.tag == "a":
        text = render_inline_children(item)
        href = item.attrs.get("href", "").strip()
        if text and href and href != "#":
            return f"[{text}]({href})"
        return text

    return render_inline_children(item)


def render_table(node: Node) -> list[str]:
    rows: list[list[str]] = []
    for row in find_all(node, lambda item: item.tag == "tr"):
        cells = [
            clean_inline(render_inline_children(cell)).replace("|", "\\|")
            for cell in row.children
            if isinstance(cell, Node) and cell.tag in {"th", "td"}
        ]
        if cells:
            rows.append(cells)

    if not rows:
        return []

    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    lines = ["| " + " | ".join(normalized[0]) + " |"]
    lines.append("| " + " | ".join("---" for _ in range(width)) + " |")
    for row in normalized[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return ["\n".join(lines)]


def render_list(node: Node, indent: int = 0) -> list[str]:
    lines: list[str] = []
    counter = 1
    ordered = node.tag == "ol"

    for child in node.children:
        if not isinstance(child, Node) or child.tag != "li" or should_skip(child):
            continue

        bullet = f"{counter}." if ordered else "-"
        counter += 1
        nested_blocks: list[str] = []
        direct_parts: list[str] = []

        for item in child.children:
            if isinstance(item, Node) and item.tag in {"ul", "ol"}:
                nested_blocks.extend(render_list(item, indent + 1))
            elif isinstance(item, Node) and item.tag in BLOCK_TAGS and item.tag != "p":
                block_text = "\n".join(render_blocks(item, indent + 1))
                if block_text:
                    direct_parts.append(block_text)
            else:
                rendered = render_inline(item)
                if rendered:
                    direct_parts.append(rendered)

        direct_text = clean_inline(" ".join(direct_parts))
        prefix = "  " * indent + bullet + " "
        if direct_text:
            lines.append(prefix + direct_text)
        else:
            lines.append(prefix.rstrip())
        lines.extend(nested_blocks)

    return lines


def render_blocks(node: Node, list_indent: int = 0) -> list[str]:
    if should_skip(node):
        return []

    if node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        text = render_inline_children(node)
        if not text:
            return []
        level = int(node.tag[1])
        return [f"{'#' * level} {text}"]

    if node.tag in {"p", "summary", "dt", "dd", "figcaption"}:
        text = render_inline_children(node)
        return [text] if text else []

    if node.tag == "pre":
        text = "".join(child if isinstance(child, str) else render_inline(child) for child in node.children)
        text = text.strip("\n")
        return [f"```\n{text}\n```"] if text else []

    if node.tag in {"ul", "ol"}:
        lines = render_list(node, list_indent)
        return ["\n".join(lines)] if lines else []

    if node.tag == "blockquote":
        child_blocks = render_child_blocks(node, list_indent)
        quoted = []
        for block in child_blocks:
            quoted.append("\n".join("> " + line if line else ">" for line in block.splitlines()))
        return quoted

    if node.tag == "table":
        return render_table(node)

    if node.tag == "hr":
        return ["---"]

    if is_block_link(node):
        return render_child_blocks(node, list_indent)

    return render_child_blocks(node, list_indent)


def render_child_blocks(node: Node, list_indent: int = 0) -> list[str]:
    blocks: list[str] = []
    inline_parts: list[str] = []

    def flush_inline() -> None:
        text = clean_inline(" ".join(inline_parts))
        inline_parts.clear()
        if text:
            blocks.append(text)

    for child in node.children:
        if isinstance(child, Node) and (child.tag in BLOCK_TAGS or is_block_link(child)):
            flush_inline()
            blocks.extend(render_blocks(child, list_indent))
        else:
            rendered = render_inline(child)
            if rendered:
                inline_parts.append(rendered)

    flush_inline()
    return blocks


def markdown_for_file(source: Path, document_policy: str) -> tuple[str, list[str]]:
    text = source.read_text(encoding="utf-8")
    documents = split_html_documents(text)
    warnings: list[str] = []
    if len(documents) > 1:
        warnings.append(f"{source}: found {len(documents)} HTML documents; using {document_policy}")

    if document_policy == "first":
        documents_to_render = [documents[0]]
    elif document_policy == "all":
        documents_to_render = documents
    else:
        documents_to_render = [documents[-1]]

    blocks: list[str] = []
    for document in documents_to_render:
        root = parse_html(document)
        for node in selected_content(root, source):
            blocks.extend(render_blocks(node))

    blocks = dedupe_adjacent_blocks(blocks)
    return "\n\n".join(blocks).strip() + "\n", warnings


def dedupe_adjacent_blocks(blocks: Iterable[str]) -> list[str]:
    cleaned: list[str] = []
    for block in blocks:
        block = re.sub(r"\n{3,}", "\n\n", block).strip()
        if block and (not cleaned or cleaned[-1] != block):
            cleaned.append(block)
    return cleaned


def output_name(source: Path) -> str:
    return source.with_suffix(".md").name


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert the website's page text into one simple Markdown file per HTML page."
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        help="HTML files to convert. Defaults to home-page.html and pages/*.html.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for generated Markdown files. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--document-policy",
        choices=("last", "first", "all"),
        default="last",
        help="Which HTML document to use if a file contains multiple complete documents.",
    )
    args = parser.parse_args()

    inputs = args.inputs or DEFAULT_INPUTS
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    all_warnings: list[str] = []
    for source in inputs:
        source = source.resolve()
        if not source.exists():
            raise FileNotFoundError(source)

        markdown, warnings = markdown_for_file(source, args.document_policy)
        all_warnings.extend(warnings)
        target = output_dir / output_name(source)
        target.write_text(markdown, encoding="utf-8")
        print(f"Wrote {target.relative_to(WEBSITE_DIR)}")

    for warning in all_warnings:
        print(f"Warning: {warning}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
