#!/usr/bin/env python3
"""Generate a LinkedIn carousel PDF from a JSON slides array.

Usage:
    python3 linkedin_carousel.py --slides /tmp/slides.json --output ~/Desktop/carousel.pdf

Slide types (set via "draw" key):
  (none)      — standard text slide
  "pipeline"  — vertical flow diagram; requires "steps": [{"label": ..., "note": ...}]
  "bars"      — horizontal bar chart; requires "bars": [{"label", "value", "display", "note"}]
  "fork"      — upstream→fork diagram; requires "upstream": {}, "fork": {}, "note": ""
  "cta": true — coral-background CTA slide (also auto-applied to last slide)
"""

import argparse
import json
import os
import sys

try:
    from fpdf import FPDF
except ImportError:
    print("fpdf2 required: pip install fpdf2", file=sys.stderr)
    sys.exit(1)

# Prefer Arial Unicode for full Unicode support (bullets, em-dashes, etc.)
_UNICODE_FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"
_USE_UNICODE_FONT = os.path.exists(_UNICODE_FONT_PATH)

# Anthropic brand palette
_BG     = (28,  25,  23)   # #1C1917 warm near-black
_CARD   = (45,  41,  38)   # slightly lighter for card backgrounds
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
        if _USE_UNICODE_FONT:
            self.add_font("ArialUnicode", style="", fname=_UNICODE_FONT_PATH)
            self.add_font("ArialUnicode", style="B", fname=_UNICODE_FONT_PATH)

    def _font(self, style="", size=12):
        if _USE_UNICODE_FONT:
            self.set_font("ArialUnicode", style=style, size=size)
        else:
            self.set_font("Helvetica", style=style, size=size)

    def _bg(self):
        self.set_fill_color(*_BG)
        self.rect(0, 0, PAGE_W, PAGE_H, "F")

    def _accent_bar(self):
        self.set_fill_color(*_ACCENT)
        self.rect(0, 0, PAGE_W, 3, "F")

    def _slide_number(self, num, total):
        self._font(size=11)
        self.set_text_color(*_MUTED)
        self.set_xy(0, PAGE_H - 12)
        self.cell(PAGE_W - 14, 10, f"{num} / {total}", align="R")

    def _section_header(self, title, pad=16, start_y=12):
        """Draw title + accent underline. Returns y after underline."""
        self._font("B", 22)
        self.set_text_color(*_TITLE)
        self.set_xy(pad, start_y)
        self.multi_cell(PAGE_W - pad * 2, 10, title, align="L")
        y = self.get_y() + 3
        self.set_fill_color(*_ACCENT)
        self.rect(pad, y, 24, 2, "F")
        return y + 7

    def _arrow_down(self, cx, y_top, y_bot):
        """Draw a vertical arrow from y_top to y_bot centered on cx."""
        self.set_draw_color(*_ACCENT)
        self.set_line_width(0.5)
        self.line(cx, y_top, cx, y_bot - 3)
        self.set_fill_color(*_ACCENT)
        self.polygon([(cx, y_bot), (cx - 2.5, y_bot - 4), (cx + 2.5, y_bot - 4)], style="F")

    # ------------------------------------------------------------------ #
    # Standard text slide
    # ------------------------------------------------------------------ #
    def add_slide(self, title: str, body: str, emoji: str, num: int, total: int):
        self.add_page()
        self._bg()
        self._accent_bar()
        self._slide_number(num, total)

        pad = 16
        y = 24

        if emoji:
            self._font("B", 40)
            self.set_text_color(*_TITLE)
            self.set_xy(pad, y)
            self.cell(PAGE_W - pad * 2, 18, emoji, align="L")
            y += 20

        self._font("B", 28)
        self.set_text_color(*_TITLE)
        self.set_xy(pad, y)
        self.multi_cell(PAGE_W - pad * 2, 12, title, align="L")
        y = self.get_y()

        self.set_fill_color(*_ACCENT)
        self.rect(pad, y + 3, 28, 2, "F")
        y += 12

        if body:
            self._font(size=16)
            self.set_text_color(*_BODY)
            self.set_xy(pad, y)
            self.multi_cell(PAGE_W - pad * 2, 8.5, body, align="L")

    # ------------------------------------------------------------------ #
    # Pipeline flow diagram
    # ------------------------------------------------------------------ #
    def add_pipeline_slide(self, title: str, steps: list, num: int, total: int, caption: str = ""):
        self.add_page()
        self._bg()
        self._accent_bar()
        self._slide_number(num, total)

        pad = 16
        y = self._section_header(title, pad)

        box_w = PAGE_W - pad * 2
        n = len(steps)
        caption_reserve = 16 if caption else 0
        remaining = PAGE_H - y - 14 - caption_reserve
        # Scale box and arrow height to fit any number of steps
        arrow_h = max(5, min(8, int((remaining * 0.18) / max(n - 1, 1))))
        box_h = max(16, int((remaining - (n - 1) * arrow_h) / n))
        total_h = n * box_h + (n - 1) * arrow_h
        if total_h < remaining:
            y += (remaining - total_h) / 2

        cx = PAGE_W / 2

        for i, step in enumerate(steps):
            # Card
            self.set_fill_color(*_CARD)
            self.rect(pad, y, box_w, box_h, "F")
            # Left accent stripe
            self.set_fill_color(*_ACCENT)
            self.rect(pad, y, 3, box_h, "F")
            # Step number
            self._font("B", 11)
            self.set_text_color(*_ACCENT)
            self.set_xy(pad + 5, y + 4)
            self.cell(10, 6, str(i + 1), align="L")
            # Label
            label_y = y + 4 if not step.get("note") else y + 2
            self._font("B", 14)
            self.set_text_color(*_TITLE)
            self.set_xy(pad + 16, label_y)
            self.cell(box_w - 20, 8, step["label"], align="L")
            # Note
            if step.get("note"):
                self._font(size=10)
                self.set_text_color(*_BODY)
                self.set_xy(pad + 16, label_y + 9)
                self.multi_cell(box_w - 20, 6, step["note"], align="L")

            y += box_h
            if i < n - 1:
                self._arrow_down(cx, y + 1, y + arrow_h - 1)
                y += arrow_h

        if caption:
            self._font(size=8)
            self.set_text_color(*_MUTED)
            self.set_xy(pad, PAGE_H - 14 - caption_reserve + 2)
            self.multi_cell(box_w, 5, caption, align="L")

    # ------------------------------------------------------------------ #
    # Horizontal bar chart
    # ------------------------------------------------------------------ #
    def add_bars_slide(self, title: str, bars: list, num: int, total: int):
        self.add_page()
        self._bg()
        self._accent_bar()
        self._slide_number(num, total)

        pad = 16
        y = self._section_header(title, pad)

        label_w = 48
        val_w = 24
        bar_area = PAGE_W - pad * 2 - label_w - val_w
        max_val = max(b["value"] for b in bars)

        remaining = PAGE_H - y - 14
        row_h = max(26, min(50, int(remaining / len(bars))))
        bar_h = max(11, int(row_h * 0.38))
        total_h = len(bars) * row_h
        if total_h < remaining:
            y += (remaining - total_h) / 2

        for i, bar in enumerate(bars):
            ratio = bar["value"] / max_val
            fill_w = max(bar_area * ratio, 1)

            # Label
            self._font("B", 14)
            self.set_text_color(*_TITLE)
            self.set_xy(pad, y + (row_h - 11) / 2)
            self.cell(label_w, 11, bar["label"], align="L")

            # Background track
            bx = pad + label_w
            by = y + (row_h - bar_h) / 2
            self.set_fill_color(*_CARD)
            self.rect(bx, by, bar_area, bar_h, "F")

            # Fill — coral at full brightness for highest bar, dimmed for others
            if i == 0:
                fill_color = _ACCENT
            else:
                dim = 0.45 + 0.45 * ratio
                fill_color = tuple(int(c * dim) for c in _ACCENT)
            self.set_fill_color(*fill_color)
            self.rect(bx, by, fill_w, bar_h, "F")

            # Value label
            self._font("B", 14)
            self.set_text_color(*(_ACCENT if i == 0 else _BODY))
            self.set_xy(bx + bar_area + 3, y + (row_h - 11) / 2)
            self.cell(val_w - 3, 11, bar.get("display", str(bar["value"])), align="L")

            # Sub-note
            if bar.get("note"):
                self._font(size=10)
                self.set_text_color(*_MUTED)
                self.set_xy(bx, by + bar_h + 1)
                self.cell(bar_area, 5, bar["note"], align="L")

            y += row_h

    # ------------------------------------------------------------------ #
    # Fork diagram
    # ------------------------------------------------------------------ #
    def add_fork_slide(self, title: str, upstream: dict, fork: dict, note: str, num: int, total: int):
        self.add_page()
        self._bg()
        self._accent_bar()
        self._slide_number(num, total)

        pad = 16
        y = self._section_header(title, pad)

        box_w = PAGE_W - pad * 2
        box_h = 36
        arrow_h = 22
        total_h = box_h * 2 + arrow_h
        remaining = PAGE_H - y - 24
        if total_h < remaining:
            y += (remaining - total_h) / 2

        cx = PAGE_W / 2

        # Upstream box (muted stripe)
        self.set_fill_color(*_CARD)
        self.rect(pad, y, box_w, box_h, "F")
        self.set_fill_color(*_MUTED)
        self.rect(pad, y, 3, box_h, "F")
        self._font("B", 15)
        self.set_text_color(*_BODY)
        self.set_xy(pad + 9, y + 6)
        self.cell(box_w - 13, 10, upstream["name"], align="L")
        if upstream.get("tag"):
            self._font(size=10)
            self.set_text_color(*_MUTED)
            self.set_xy(pad + 9, y + 18)
            self.cell(box_w - 13, 7, upstream["tag"], align="L")
        if upstream.get("note"):
            self._font(size=11)
            self.set_text_color(*_MUTED)
            self.set_xy(pad + 9, y + 26)
            self.cell(box_w - 13, 7, upstream["note"], align="L")
        y += box_h

        # Arrow with label
        self._arrow_down(cx, y + 2, y + arrow_h - 2)
        self._font(size=11)
        self.set_text_color(*_MUTED)
        self.set_xy(cx + 5, y + arrow_h / 2 - 3)
        self.cell(50, 6, "custom fork", align="L")
        y += arrow_h

        # Fork box (coral stripe)
        self.set_fill_color(*_CARD)
        self.rect(pad, y, box_w, box_h, "F")
        self.set_fill_color(*_ACCENT)
        self.rect(pad, y, 3, box_h, "F")
        self._font("B", 15)
        self.set_text_color(*_TITLE)
        self.set_xy(pad + 9, y + 6)
        self.cell(box_w - 13, 10, fork["name"], align="L")
        if fork.get("tag"):
            self._font(size=10)
            self.set_text_color(*_ACCENT)
            self.set_xy(pad + 9, y + 18)
            self.cell(box_w - 13, 7, fork["tag"], align="L")
        if fork.get("note"):
            self._font(size=11)
            self.set_text_color(*_BODY)
            self.set_xy(pad + 9, y + 26)
            self.cell(box_w - 13, 7, fork["note"], align="L")
        y += box_h + 7

        if note:
            lines = note.split("\n")
            # First line treated as a label (e.g. "What I added:")
            self._font("B", 11)
            self.set_text_color(*_ACCENT)
            self.set_xy(pad, y)
            self.cell(box_w, 7, lines[0], align="L")
            y += 8
            # Remaining lines as body bullets
            self._font(size=11)
            self.set_text_color(*_BODY)
            self.set_xy(pad, y)
            self.multi_cell(box_w, 7, "\n".join(lines[1:]), align="L")

    # ------------------------------------------------------------------ #
    # Query fan-out diagram
    # Shows: [topic] -> [Claude Haiku] -> [X query | HN query | Reddit]
    # ------------------------------------------------------------------ #
    def add_query_fan_slide(self, title: str, topic: str, outputs: list, caption: str, num: int, total: int):
        self.add_page()
        self._bg()
        self._accent_bar()
        self._slide_number(num, total)

        pad = 16
        y = self._section_header(title, pad)

        box_w = PAGE_W - pad * 2
        cx = PAGE_W / 2

        # ---- topic input box ----
        input_h = 18
        y += 4
        self.set_fill_color(*_CARD)
        self.rect(pad, y, box_w, input_h, "F")
        self.set_fill_color(*_MUTED)
        self.rect(pad, y, 3, input_h, "F")
        self._font(size=10)
        self.set_text_color(*_MUTED)
        self.set_xy(pad + 8, y + 2)
        self.cell(box_w - 12, 6, "weekly topic intent", align="L")
        self._font("B", 14)
        self.set_text_color(*_TITLE)
        self.set_xy(pad + 8, y + 8)
        self.cell(box_w - 12, 8, topic, align="L")
        y += input_h

        # ---- arrow down ----
        arrow1_h = 10
        self._arrow_down(cx, y + 1, y + arrow1_h - 1)
        y += arrow1_h

        # ---- Claude Haiku box (coral) ----
        claude_h = 20
        self.set_fill_color(*_ACCENT)
        self.rect(pad, y, box_w, claude_h, "F")
        self._font("B", 14)
        self.set_text_color(*_TITLE)
        self.set_xy(pad, y + 3)
        self.cell(box_w, 8, "Claude Haiku generates queries at runtime", align="C")
        self._font(size=10)
        self.set_text_color(*_TITLE)
        self.set_xy(pad, y + 12)
        self.cell(box_w, 6, "reads the topic intent, writes platform-specific search queries", align="C")
        y += claude_h

        # ---- fan-out arrows to N columns ----
        fan_h = 12
        n = len(outputs)
        col_w = box_w / n
        col_centers = [pad + col_w * i + col_w / 2 for i in range(n)]

        # horizontal bar + drop lines
        bar_y = y + 3
        self.set_draw_color(*_ACCENT)
        self.set_line_width(0.5)
        self.line(col_centers[0], bar_y, col_centers[-1], bar_y)
        for cc in col_centers:
            self.line(cc, bar_y, cc, y + fan_h - 1)
            # arrowhead
            self.set_fill_color(*_ACCENT)
            self.polygon([(cc, y + fan_h), (cc - 2, y + fan_h - 3), (cc + 2, y + fan_h - 3)], style="F")
        y += fan_h

        # ---- output boxes ----
        out_box_h = 38
        for j, out in enumerate(outputs):
            bx = pad + col_w * j
            bw = col_w - 2
            self.set_fill_color(*_CARD)
            self.rect(bx, y, bw, out_box_h, "F")
            # top accent stripe
            self.set_fill_color(*_ACCENT)
            self.rect(bx, y, bw, 2, "F")
            # platform label
            self._font("B", 11)
            self.set_text_color(*_ACCENT)
            self.set_xy(bx + 3, y + 4)
            self.cell(bw - 6, 6, out["platform"], align="L")
            # query text
            self._font(size=10)
            self.set_text_color(*_BODY)
            self.set_xy(bx + 3, y + 12)
            self.multi_cell(bw - 6, 6, out["query"], align="L")

        y += out_box_h + 4

        # ---- caption ----
        if caption:
            self._font(size=10)
            self.set_text_color(*_MUTED)
            self.set_xy(pad, y)
            self.multi_cell(box_w, 6, caption, align="L")

    # ------------------------------------------------------------------ #
    # Output preview slide
    # Shows a representative sample of the digest email content
    # ------------------------------------------------------------------ #
    def add_output_preview_slide(self, title: str, header: str, insights: list, stats: str, repos: list, num: int, total: int):
        self.add_page()
        self._bg()
        self._accent_bar()
        self._slide_number(num, total)

        pad = 16
        y = self._section_header(title, pad)
        box_w = PAGE_W - pad * 2

        # ---- digest header bar ----
        self.set_fill_color(*_CARD)
        self.rect(pad, y, box_w, 12, "F")
        self.set_fill_color(*_ACCENT)
        self.rect(pad, y, 3, 12, "F")
        self._font("B", 10)
        self.set_text_color(*_ACCENT)
        self.set_xy(pad + 7, y + 2)
        self.cell(box_w - 10, 8, header, align="L")
        y += 14

        # ---- insights ----
        for insight in insights:
            label = insight.get("label", "")
            body  = insight.get("body", "")
            card_h = 26
            self.set_fill_color(*_CARD)
            self.rect(pad, y, box_w, card_h, "F")
            # label
            self._font("B", 10)
            self.set_text_color(*_TITLE)
            self.set_xy(pad + 5, y + 3)
            self.cell(box_w - 10, 6, label, align="L")
            # body
            self._font(size=9)
            self.set_text_color(*_BODY)
            self.set_xy(pad + 5, y + 11)
            self.multi_cell(box_w - 10, 5.5, body, align="L")
            y += card_h + 3

        # ---- stats bar ----
        self.set_fill_color(38, 34, 32)
        self.rect(pad, y, box_w, 10, "F")
        self._font(size=9)
        self.set_text_color(*_MUTED)
        self.set_xy(pad + 5, y + 2)
        self.cell(box_w - 10, 6, stats, align="L")
        y += 13

        # ---- trending repos ----
        self._font("B", 10)
        self.set_text_color(*_ACCENT)
        self.set_xy(pad, y)
        self.cell(box_w, 6, "Trending GitHub Repos", align="L")
        y += 8

        for repo in repos:
            self.set_fill_color(*_CARD)
            self.rect(pad, y, box_w, 14, "F")
            self._font("B", 10)
            self.set_text_color(*_TITLE)
            self.set_xy(pad + 5, y + 2)
            self.cell(box_w - 40, 6, repo["name"], align="L")
            self._font("B", 10)
            self.set_text_color(*_ACCENT)
            self.set_xy(PAGE_W - pad - 34, y + 2)
            self.cell(34, 6, repo["stars"], align="R")
            self._font(size=9)
            self.set_text_color(*_MUTED)
            self.set_xy(pad + 5, y + 9)
            self.cell(box_w - 10, 5, repo["desc"], align="L")
            y += 16

    # ------------------------------------------------------------------ #
    # CTA slide
    # ------------------------------------------------------------------ #
    def add_cta_slide(self, title: str, body: str, num: int, total: int):
        self.add_page()
        self.set_fill_color(*_BG)
        self.rect(0, 0, PAGE_W, PAGE_H, "F")
        self._accent_bar()
        self._slide_number(num, total)

        pad = 16
        self._font("B", 32)
        self.set_text_color(*_ACCENT)
        self.set_xy(pad, 50)
        self.multi_cell(PAGE_W - pad * 2, 14, title, align="C")
        y = self.get_y() + 10

        if body:
            self._font(size=17)
            self.set_text_color(*_BODY)
            self.set_xy(pad, y)
            self.multi_cell(PAGE_W - pad * 2, 9, body, align="C")


def export_images(pdf_path: str, out_dir: str, dpi: int = 250) -> list[str]:
    """Render each PDF page to a PNG. Returns list of created paths."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("PyMuPDF required for image export: pip install pymupdf", file=sys.stderr)
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    doc = fitz.open(pdf_path)
    paths = []
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out = os.path.join(out_dir, f"slide_{i:02d}.png")
        pix.save(out)
        paths.append(out)
    doc.close()
    return paths


def export_images(pdf_path: str, out_dir: str, dpi: int = 150) -> list[str]:
    """Render each PDF page to a PNG. Returns list of created paths."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("PyMuPDF required for image export: pip install pymupdf", file=sys.stderr)
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    doc = fitz.open(pdf_path)
    paths = []
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out = os.path.join(out_dir, f"slide_{i:02d}.png")
        pix.save(out)
        paths.append(out)
    doc.close()
    return paths


def main():
    parser = argparse.ArgumentParser(description="Generate LinkedIn carousel PDF")
    parser.add_argument("--slides", required=True, help="JSON file with slides array")
    parser.add_argument("--output", default="carousel.pdf", help="Output PDF path")
    parser.add_argument("--images", metavar="DIR", help="Also export each slide as a PNG into DIR")
    parser.add_argument("--dpi", type=int, default=250, help="Image export resolution (default 250)")
    args = parser.parse_args()

    with open(args.slides) as f:
        slides = json.load(f)

    if not slides:
        print("No slides found in JSON", file=sys.stderr)
        sys.exit(1)

    pdf = CarouselPDF()
    total = len(slides)

    for i, slide in enumerate(slides, 1):
        draw = slide.get("draw")
        is_cta = slide.get("cta", False) or (i == total and draw not in ("pipeline", "bars", "fork", "output-preview", "query-fan"))

        if draw == "pipeline":
            pdf.add_pipeline_slide(slide["title"], slide.get("steps", []), i, total, caption=slide.get("caption", ""))
        elif draw == "query-fan":
            pdf.add_query_fan_slide(
                slide["title"],
                slide.get("topic", ""),
                slide.get("outputs", []),
                slide.get("caption", ""),
                i, total,
            )
        elif draw == "output-preview":
            pdf.add_output_preview_slide(
                slide["title"],
                slide.get("header", ""),
                slide.get("insights", []),
                slide.get("stats", ""),
                slide.get("repos", []),
                i, total,
            )
        elif draw == "bars":
            pdf.add_bars_slide(slide["title"], slide.get("bars", []), i, total)
        elif draw == "fork":
            pdf.add_fork_slide(
                slide["title"],
                slide.get("upstream", {}),
                slide.get("fork", {}),
                slide.get("note", ""),
                i, total,
            )
        elif is_cta:
            pdf.add_cta_slide(slide.get("title", ""), slide.get("body", ""), i, total)
        else:
            pdf.add_slide(
                slide.get("title", ""),
                slide.get("body", ""),
                slide.get("emoji", ""),
                i, total,
            )

    pdf.output(args.output)
    print(f"Generated: {args.output} ({total} slides)")

    if args.images:
        paths = export_images(args.output, args.images, dpi=args.dpi)
        for p in paths:
            print(f"  {p}")


if __name__ == "__main__":
    main()
