#!/usr/bin/env python3
"""
Fetch Ed lessons for a course and export a consolidated PDF.

Usage:
  python ed_lessons_to_pdf.py --env local.env --course 16645 --out ed_lessons.pdf

Requirements:
  pip install requests reportlab
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests import Response
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem, Image, Preformatted
from PyPDF2 import PdfMerger
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
import xml.etree.ElementTree as ET
import io

ED_BASE = "https://edstem.org/api"
DEFAULT_COURSE_ID = 16645


# ----------------------------
# Utilities
# ----------------------------
def load_bearer_token(env_path: Path) -> str:
    """
    Minimal .env reader: expects a line like:
      ED_BEARER=eyJhbGciOi...
    Also tolerates ED_BEARER_TOKEN=... or BEARER=...
    """
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {env_path}")

    token_candidates = ["ED_BEARER", "ED_BEARER_TOKEN", "BEARER", "TOKEN", "ED_TOKEN"]
    token_map: Dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        token_map[k.strip()] = v.strip()

    for key in token_candidates:
        if key in token_map and token_map[key]:
            return token_map[key]

    raise KeyError(
        f"No bearer token found in {env_path}. "
        f"Please add a line like ED_BEARER=your_token_here"
    )


def backoff_sleep(attempt: int) -> None:
    # linear backoff is fine here
    time.sleep(0.8 * attempt)


def req_with_retries(
    method: str,
    url: str,
    session: requests.Session,
    headers: Dict[str, str],
    params: Optional[Dict[str, Any]] = None,
    max_attempts: int = 4,
) -> Response:
    last_exc: Optional[Exception] = None
    for attempt in range(1, max_attempts + 1):
        try:
            resp = session.request(method, url, headers=headers, params=params, timeout=30)
            # Retry on 429 or 5xx
            if resp.status_code == 429 or 500 <= resp.status_code < 600:
                backoff_sleep(attempt)
                continue
            return resp
        except requests.RequestException as e:
            last_exc = e
            backoff_sleep(attempt)
            continue
    if last_exc:
        raise last_exc
    raise RuntimeError(f"Failed to call {url} after {max_attempts} attempts.")


def strip_markup(ed_content: str, max_chars: int = 4000) -> str:
    """
    The lesson 'content' comes back as escaped <document> XML-ish markup.
    1) Unescape \u003c...\u003e to <...>
    2) Remove tags
    3) Collapse whitespace
    4) Trim to max_chars to keep the PDF readable
    """
    unescaped = html.unescape(ed_content or "")
    # strip tags like <paragraph>...</paragraph>
    no_tags = re.sub(r"<[^>]+>", "", unescaped)
    # normalise whitespace
    text = re.sub(r"[ \t\r\f\v]+", " ", no_tags)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    if len(text) > max_chars:
        text = text[: max_chars - 1].rstrip() + "…"
    return text


def ed_xml_to_reportlab_markup(node):
    """
    Recursively convert Edstem XML node to ReportLab markup string for inline tags,
    and return a tuple (markup, is_block) where is_block is True for block elements.
    """
    tag = node.tag.lower()
    # Inline tags
    if tag in ('bold', 'b'):
        return (f"<b>{''.join(ed_xml_to_reportlab_markup(child)[0] for child in node)}</b>" if list(node) else f"<b>{node.text or ''}</b>", False)
    if tag in ('i', 'italic'):
        return (f"<i>{''.join(ed_xml_to_reportlab_markup(child)[0] for child in node)}</i>" if list(node) else f"<i>{node.text or ''}</i>", False)
    if tag == 'code':
        return (f"<font face='Courier'>{''.join(ed_xml_to_reportlab_markup(child)[0] for child in node)}</font>" if list(node) else f"<font face='Courier'>{node.text or ''}</font>", False)
    # Block tags
    if tag == 'pre':
        # Preformatted block
        return (node.text or '', 'pre')
    if tag == 'heading':
        # Heading block
        level = int(node.attrib.get('level', 2))
        return (''.join(ed_xml_to_reportlab_markup(child)[0] for child in node) if list(node) else (node.text or ''), f'heading{level}')
    if tag == 'image':
        return (node.attrib, 'image')
    if tag == 'list':
        # List block
        items = []
        for item in node.findall('list-item'):
            # Each list-item may have paragraphs or inline
            item_content = []
            for child in item:
                markup, blocktype = ed_xml_to_reportlab_markup(child)
                if blocktype is False:
                    item_content.append(markup)
                elif blocktype == 'pre':
                    item_content.append(f'<font face="Courier">{markup}</font>')
                else:
                    item_content.append(markup)
            items.append(''.join(item_content))
        return (items, 'list')
    if tag == 'paragraph':
        # Paragraph block
        markup = ''
        if node.text:
            markup += html.escape(node.text)
        for child in node:
            child_markup, blocktype = ed_xml_to_reportlab_markup(child)
            markup += child_markup
            if child.tail:
                markup += html.escape(child.tail)
        return (markup, 'paragraph')
    # Fallback: treat as inline
    markup = ''
    if node.text:
        markup += html.escape(node.text)
    for child in node:
        child_markup, blocktype = ed_xml_to_reportlab_markup(child)
        markup += child_markup
        if child.tail:
            markup += html.escape(child.tail)
    return (markup, False)

def ed_content_to_flowables(content, styles, out_dir):
    def fetch_image(url):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return io.BytesIO(resp.content)
        except Exception:
            pass
        return None

    def inline_markup(node):
        tag = node.tag.lower()
        if tag in ('bold', 'b'):
            return f"<b>{''.join(inline_markup(child) for child in node) if list(node) else (node.text or '')}</b>"
        if tag in ('i', 'italic'):
            return f"<i>{''.join(inline_markup(child) for child in node) if list(node) else (node.text or '')}</i>"
        if tag == 'code':
            return f"<font face='Courier'>{''.join(inline_markup(child) for child in node) if list(node) else (node.text or '')}</font>"
        # Fallback: text and children
        text = html.escape(node.text) if node.text else ''
        for child in node:
            text += inline_markup(child)
            if child.tail:
                text += html.escape(child.tail)
        return text

    def block_to_flowable(node):
        tag = node.tag.lower()
        if tag == 'paragraph':
            markup = ''
            if node.text:
                markup += html.escape(node.text)
            for child in node:
                markup += inline_markup(child)
                if child.tail:
                    markup += html.escape(child.tail)
            return [Paragraph(markup, styles['BodyText'])]
        if tag == 'pre':
            if 'CustomCode' not in styles:
                custom_code = ParagraphStyle(
                    "CustomCode",
                    parent=styles["Code"] if "Code" in styles else styles["BodyText"],
                    fontName="Courier",
                    fontSize=9,
                    leading=11,
                    textColor=colors.darkblue,
                    leftIndent=12,
                    borderPadding=2,
                    backColor=colors.whitesmoke,
                    alignment=TA_LEFT,
                )
                styles.add(custom_code)
            return [Preformatted(node.text or '', styles['CustomCode'])]
        if tag == 'heading':
            level = int(node.attrib.get('level', 2))
            style = styles.get(f'Heading{level}', styles['Heading2'])
            markup = ''
            if node.text:
                markup += html.escape(node.text)
            for child in node:
                markup += inline_markup(child)
                if child.tail:
                    markup += html.escape(child.tail)
            return [Paragraph(markup, style)]
        if tag == 'list':
            items = []
            for item in node.findall('list-item'):
                item_markup = ''
                for child in item:
                    item_markup += inline_markup(child)
                    if child.tail:
                        item_markup += html.escape(child.tail)
                items.append(ListItem([Paragraph(item_markup, styles['BodyText'])]))
            return [ListFlowable(items, bulletType='bullet', leftIndent=12)]
        if tag == 'image':
            src = node.attrib.get('src')
            if src:
                img_data = fetch_image(src)
                if img_data:
                    width = int(node.attrib.get('width', 200))
                    height = int(node.attrib.get('height', 150))
                    return [Image(img_data, width=width, height=height)]
            return []
        # Fallback: treat as paragraph
        return [Paragraph(inline_markup(node), styles['BodyText'])]

    try:
        root = ET.fromstring(content)
        flow = []
        for node in root:
            flow.extend(block_to_flowable(node))
            flow.append(Spacer(1, 8))  # Add space between blocks
        return flow
    except Exception:
        return [Paragraph(html.escape(content), styles['BodyText'])]


# ----------------------------
# Data classes
# ----------------------------
@dataclass
class SlideSummary:
    id: int
    title: Optional[str]
    index: Optional[int]
    status: Optional[str]
    correct: Optional[bool]
    content_text: Optional[str]


@dataclass
class LessonSummary:
    id: int
    title: str
    created_at: Optional[str]
    outline: Optional[str]
    slide_count: int
    state: Optional[str]
    status: Optional[str]
    first_viewed_at: Optional[str]
    last_viewed_slide_id: Optional[int]
    slides: List[SlideSummary]


# ----------------------------
# API calls
# ----------------------------
def fetch_lessons_list(course_id: int, token: str) -> List[Dict[str, Any]]:
    url = f"{ED_BASE}/courses/{course_id}/lessons"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    with requests.Session() as s:
        resp = req_with_retries("GET", url, s, headers)
        if resp.status_code == 401:
            raise PermissionError("Unauthorised (401). Check your Bearer token.")
        if not resp.ok:
            raise RuntimeError(f"Failed to fetch lessons list: {resp.status_code} {resp.text}")
        data = resp.json()
    lessons = data.get("lessons", []) or []
    return lessons


def fetch_lesson_detail(lesson_id: int, token: str) -> Dict[str, Any]:
    url = f"{ED_BASE}/lessons/{lesson_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    with requests.Session() as s:
        resp = req_with_retries("GET", url, s, headers)
        if resp.status_code == 401:
            raise PermissionError("Unauthorised (401). Check your Bearer token.")
        if not resp.ok:
            raise RuntimeError(f"Failed to fetch lesson {lesson_id}: {resp.status_code} {resp.text}")
        return resp.json().get("lesson", {})


# ----------------------------
# Transform
# ----------------------------
def build_lesson_summary(lesson: Dict[str, Any]) -> LessonSummary:
    slides_raw: List[Dict[str, Any]] = lesson.get("slides", []) or []
    slides: List[SlideSummary] = []
    for s in slides_raw:
        content_text = None
        if s.get("content"):
            content_text = strip_markup(str(s["content"]))
        slides.append(
            SlideSummary(
                id=int(s.get("id")),
                title=s.get("title"),
                index=s.get("index"),
                status=s.get("status"),
                correct=s.get("correct"),
                content_text=content_text,
            )
        )

    return LessonSummary(
        id=int(lesson.get("id")),
        title=lesson.get("title") or "(untitled)",
        created_at=lesson.get("created_at"),
        outline=lesson.get("outline"),
        slide_count=int(lesson.get("slide_count") or 0),
        state=lesson.get("state"),
        status=lesson.get("status"),
        first_viewed_at=lesson.get("first_viewed_at"),
        last_viewed_slide_id=lesson.get("last_viewed_slide_id"),
        slides=slides,
    )


# ----------------------------
# PDF Export
# ----------------------------
def export_pdf(lessons: List[LessonSummary], out_path: Path) -> None:
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        "h1",
        parent=styles["Heading1"],
        spaceAfter=10,
    )
    h2 = ParagraphStyle(
        "h2",
        parent=styles["Heading2"],
        spaceBefore=6,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "body",
        parent=styles["BodyText"],
        leading=14,
        spaceAfter=6,
    )
    # Only add 'CustomCode' if not already present
    if 'CustomCode' not in styles:
        custom_code = ParagraphStyle(
            "CustomCode",
            parent=styles["Code"] if "Code" in styles else styles["BodyText"],
            fontName="Courier",
            fontSize=9,
            leading=11,
            textColor=colors.darkblue,
            leftIndent=12,
            borderPadding=2,
            backColor=colors.whitesmoke,
            alignment=TA_LEFT,
        )
        styles.add(custom_code)
    meta = ParagraphStyle(
        "meta",
        parent=styles["BodyText"],
        fontSize=9,
        leading=11,
        textColor="#444444",
        spaceAfter=6,
    )

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="Ed Lessons Export",
        author="ed_lessons_to_pdf.py",
    )

    story: List[Any] = []

    for i, lesson in enumerate(lessons, start=1):
        story.append(Paragraph(f"Lesson {i}: {html.escape(lesson.title)}", h1))
        meta_lines = []
        if lesson.created_at:
            meta_lines.append(f"<b>Created:</b> {html.escape(lesson.created_at)}")
        if lesson.outline:
            meta_lines.append(f"<i>Outline:</i> {html.escape(lesson.outline)}")
        if meta_lines:
            story.append(Paragraph(" &nbsp; | &nbsp; ".join(meta_lines), meta))

        # Slides
        if lesson.slides:
            story.append(Spacer(1, 6))
            sorted_slides = sorted(lesson.slides, key=lambda x: (x.index if x.index is not None else 10**9, getattr(x, 'id', 0)))
            for s in sorted_slides:
                if s.title:
                    story.append(Paragraph(f"{html.escape(s.title)}", h2))
                if s.content_text:
                    # Use new rich formatting
                    story.extend(ed_content_to_flowables(s.content_text, styles, out_path.parent))
                story.append(Spacer(1, 6))

        # Page break between lessons
        if i < len(lessons):
            story.append(PageBreak())

    doc.build(story)


# ----------------------------
# Main
# ----------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Export Ed lessons to a PDF.")
    parser.add_argument("--env", type=str, default="local.env", help="Path to local.env containing ED_BEARER=...")
    parser.add_argument("--course", type=int, default=DEFAULT_COURSE_ID, help="Course ID (default 16645)")
    parser.add_argument("--out-dir", type=str, default="ed_lessons_pdfs", help="Output directory for per-lesson PDFs")
    parser.add_argument("--max-lessons", type=int, default=0, help="Optional cap on number of lessons to fetch (0 = all)")
    args = parser.parse_args()

    env_path = Path(args.env).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        token = load_bearer_token(env_path)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    try:
        lessons_list = fetch_lessons_list(args.course, token)
    except Exception as e:
        print(f"[ERROR] Failed to fetch lessons list: {e}", file=sys.stderr)
        sys.exit(2)

    if args.max_lessons and args.max_lessons > 0:
        lessons_list = lessons_list[: args.max_lessons]

    # Fetch each lesson in detail
    lesson_summaries: List[LessonSummary] = []
    raw_dump: Dict[str, Any] = {"course_id": args.course, "lessons": []}

    def sanitize_filename(name: str) -> str:
        # Remove or replace characters not allowed in filenames
        name = name.strip().replace(' ', '_')
        name = re.sub(r'[^\w\-\.]', '', name)
        return name[:100]  # limit length for safety

    def download_pdf(url: str, dest_path: Path) -> bool:
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                # Write content to file
                dest_path.write_bytes(resp.content)
                # Check Content-Type header
                content_type = resp.headers.get('content-type', '').lower()
                if 'application/pdf' in content_type:
                    return True
                # If not, check file signature
                with open(dest_path, 'rb') as f:
                    start = f.read(5)
                    if start == b'%PDF-':
                        return True
                print(f"[WARN] Skipping non-PDF file (not detected as PDF): {url}", file=sys.stderr)
                dest_path.unlink(missing_ok=True)
                return False
            else:
                print(f"[WARN] Skipping failed download: {url}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"[WARN] Failed to download {url}: {e}", file=sys.stderr)
            return False

    for item in lessons_list:
        lid = item.get("id")
        if not lid:
            continue
        try:
            detail = fetch_lesson_detail(int(lid), token)
        except Exception as e:
            print(f"[WARN] Skipping lesson {lid}: {e}", file=sys.stderr)
            continue

        raw_dump["lessons"].append(detail)
        lesson_summary = build_lesson_summary(detail)
        lesson_summaries.append(lesson_summary)

        # Use lesson title for filename, sanitized
        title = lesson_summary.title or str(lid)
        safe_title = sanitize_filename(title)
        pdf_path = out_dir / f"{safe_title}.pdf"
        try:
            export_pdf([lesson_summary], pdf_path)
            # --- Append any slide file_url PDFs ---
            file_urls = []
            for slide in detail.get("slides", []):
                file_url = slide.get("file_url")
                if file_url:
                    file_urls.append(file_url)
            if file_urls:
                with tempfile.TemporaryDirectory() as tmpdir:
                    merger = PdfMerger()
                    merger.append(str(pdf_path))
                    for idx, url in enumerate(file_urls):
                        tmp_pdf = Path(tmpdir) / f"slidefile_{idx}.pdf"
                        if download_pdf(url, tmp_pdf):
                            merger.append(str(tmp_pdf))
                    merger.write(str(pdf_path))
                    merger.close()
            print(f"[OK] Wrote PDF for lesson {lid} as {pdf_path}")
        except Exception as e:
            print(f"[ERROR] Failed to generate PDF for lesson {lid}: {e}", file=sys.stderr)

        # Optionally, write per-lesson JSON
        json_path = out_dir / f"{safe_title}.json"
        try:
            json_path.write_text(json.dumps(detail, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"[WARN] Could not write JSON for lesson {lid}: {e}", file=sys.stderr)

    if not lesson_summaries:
        print("[INFO] No lessons found to export.")
        sys.exit(0)


if __name__ == "__main__":
    main()
