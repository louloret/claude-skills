#!/usr/bin/env python3
"""Generate a LinkedIn carousel PDF from a JSON slides array.

Usage:
    python3 linkedin_carousel.py --slides /tmp/slides.json --output ~/Desktop/carousel.pdf
"""

import argparse
import json
import sys

try:
    from fpdf import FPDF
except ImportError:
    print("fpdf2 required: pip install fpdf2", file=sys.stderr)
    sys.exit(1)

# Anthropic brand palette
_BG     = (28,  25,  23)   # #1C1917 warm near-black
_ACCENT = (232, 98,  58)   # #E8623A coral
_TITLE  = (250, 249, 246)  # #FAF9F6 cream
_BODY   = (214, 211, 206)  # #D6D3CE warm light gray
_MUTED  = (107, 100, 97)   # #6B6461 muted gray

PAGE_W = 200  # mm — square (1:1), safe for LinkedIn
PAGE_H = 200


class CarouselPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format=(PAGE_W, PAGE_H))
        self.set_auto_page_break(False)
        self.set_margins(0, 0, 0)

    def _bg(self):
        self.set_fill_color(*_BG)
        self.rect(0, 0, PAGE_W, PAGE_H, "F")

    def _accent_bar(self):
        self.set_fill_color(*_ACCENT)
        self.rect(0, 0, PAGE_W, 3, "F")

    def _slide_number(self, num, total):
        self.set_font("Helvetica", size=9)
        self.set_text_color(*_MUTED)
        self.set_xy(0, PAGE_H - 12)
        self.cell(PAGE_W - 14, 10, f"{num} / {total}", align="R")

    def add_slide(self, title: str, body: str, emoji: str, num: int, total: int):
        self.add_page()
        self._bg()
        self._accent_bar()
        self._slide_number(num, total)

        pad = 16
        y = 24

        # Emoji
        if emoji:
            self.set_font("Helvetica", "B", 32)
            self.set_text_color(*_TITLE)
            self.set_xy(pad, y)
            self.cell(PAGE_W - pad * 2, 14, emoji, align="L")
            y += 16

        # Title
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*_TITLE)
        self.set_xy(pad, y)
        self.multi_cell(PAGE_W - pad * 2, 9, title, align="L")
        y = self.get_y()

        # Accent underline
        self.set_fill_color(*_ACCENT)
        self.rect(pad, y + 3, 28, 2, "F")
        y += 10

        # Body
        if body:
            self.set_font("Helvetica", size=12)
            self.set_text_color(*_BODY)
            self.set_xy(pad, y)
            self.multi_cell(PAGE_W - pad * 2, 6.5, body, align="L")

    def add_cta_slide(self, title: str, body: str, num: int, total: int):
        """Final slide: accent-colored background."""
        self.add_page()
        self.set_fill_color(*_ACCENT)
        self.rect(0, 0, PAGE_W, PAGE_H, "F")
        self._slide_number(num, total)

        pad = 16
        # Title
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(*_TITLE)
        self.set_xy(pad, 60)
        self.multi_cell(PAGE_W - pad * 2, 11, title, align="C")
        y = self.get_y() + 8

        # Body
        if body:
            self.set_font("Helvetica", size=13)
            self.set_text_color(*_TITLE)
            self.set_xy(pad, y)
            self.multi_cell(PAGE_W - pad * 2, 7, body, align="C")


def main():
    parser = argparse.ArgumentParser(description="Generate LinkedIn carousel PDF")
    parser.add_argument("--slides", required=True, help="JSON file with slides array")
    parser.add_argument("--output", default="carousel.pdf", help="Output PDF path")
    args = parser.parse_args()

    with open(args.slides) as f:
        slides = json.load(f)

    if not slides:
        print("No slides found in JSON", file=sys.stderr)
        sys.exit(1)

    pdf = CarouselPDF()
    total = len(slides)

    for i, slide in enumerate(slides, 1):
        title = slide.get("title", "")
        body  = slide.get("body", "")
        emoji = slide.get("emoji", "")
        is_cta = slide.get("cta", False) or i == total

        if is_cta:
            pdf.add_cta_slide(title, body, i, total)
        else:
            pdf.add_slide(title, body, emoji, i, total)

    pdf.output(args.output)
    print(f"Generated: {args.output} ({total} slides)")


if __name__ == "__main__":
    main()
