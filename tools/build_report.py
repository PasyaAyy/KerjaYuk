"""Render the project report Markdown as a styled, selectable PDF."""

from __future__ import annotations

import re
from importlib.resources import files
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "laporan.md"
OUTPUT = ROOT / "docs" / "laporan.pdf"
INK = colors.HexColor("#051316")
RED = colors.HexColor("#EC2E3A")
PLUM = colors.HexColor("#541142")
MUTED = colors.HexColor("#5F5A5D")
PALE = colors.HexColor("#FFF4F6")


def register_fonts() -> tuple[str, str]:
    fonts = files("reportlab").joinpath("fonts")
    regular = Path(str(fonts.joinpath("Vera.ttf")))
    bold = Path(str(fonts.joinpath("VeraBd.ttf")))
    pdfmetrics.registerFont(TTFont("Vera", str(regular)))
    pdfmetrics.registerFont(TTFont("Vera-Bold", str(bold)))
    return "Vera", "Vera-Bold"


def inline_markup(text: str) -> str:
    value = escape(text.strip())
    value = re.sub(r"`([^`]+)`", r'<font name="Vera">\1</font>', value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<link href="\2" color="#EC2E3A">\1</link>', value)
    return value


def make_styles(font_regular: str, font_bold: str):
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle", parent=base["Title"], fontName=font_bold,
            fontSize=27, leading=33, textColor=INK, alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "Section", parent=base["Heading2"], fontName=font_bold,
            fontSize=16, leading=21, textColor=PLUM, spaceBefore=17,
            spaceAfter=7, keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "Subsection", parent=base["Heading3"], fontName=font_bold,
            fontSize=12, leading=16, textColor=INK, spaceBefore=11,
            spaceAfter=5, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName=font_regular,
            fontSize=9.5, leading=14.5, textColor=INK, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["BodyText"], fontName=font_regular,
            fontSize=9.3, leading=13.5, textColor=INK, spaceAfter=2,
        ),
        "table": ParagraphStyle(
            "Table", parent=base["BodyText"], fontName=font_regular,
            fontSize=8.2, leading=11, textColor=INK,
        ),
        "table_head": ParagraphStyle(
            "TableHead", parent=base["BodyText"], fontName=font_bold,
            fontSize=8.2, leading=11, textColor=colors.white,
        ),
    }


def build_story(markdown: str, styles: dict[str, ParagraphStyle]):
    lines = markdown.splitlines()
    story = []
    index = 0
    while index < len(lines):
        raw = lines[index].strip()
        if not raw:
            index += 1
            continue
        if raw.startswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                line = lines[index].strip()
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                    table_lines.append(cells)
                index += 1
            if table_lines:
                rows = []
                for row_number, row in enumerate(table_lines):
                    style = styles["table_head"] if row_number == 0 else styles["table"]
                    rows.append([Paragraph(inline_markup(cell), style) for cell in row])
                table = Table(rows, repeatRows=1, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), PLUM),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DED7DA")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]))
                story.extend([Spacer(1, 3), table, Spacer(1, 8)])
            continue
        if raw.startswith("# "):
            story.append(Paragraph(inline_markup(raw[2:]), styles["title"]))
            story.append(HRFlowable(width="30%", thickness=2, color=RED, hAlign="CENTER", spaceAfter=12))
            index += 1
            continue
        if raw.startswith("## "):
            story.append(Paragraph(inline_markup(raw[3:]), styles["h2"]))
            index += 1
            continue
        if raw.startswith("### "):
            story.append(Paragraph(inline_markup(raw[4:]), styles["h3"]))
            index += 1
            continue
        if raw.startswith("- "):
            while index < len(lines) and lines[index].strip().startswith("- "):
                item = inline_markup(lines[index].strip()[2:])
                story.append(Paragraph(f"- {item}", styles["bullet"]))
                index += 1
            continue
        story.append(Paragraph(inline_markup(raw), styles["body"]))
        index += 1
    return story


def footer(canvas, document) -> None:
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(colors.HexColor("#E6E0E1"))
    canvas.setLineWidth(0.5)
    canvas.line(document.leftMargin, 34, width - document.rightMargin, 34)
    canvas.setFont("Vera", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(document.leftMargin, 22, "KerjaYuk | Komputasi Awan | Studi kasus K09")
    canvas.drawRightString(width - document.rightMargin, 22, f"Halaman {document.page}")
    canvas.restoreState()


def main() -> None:
    regular, bold = register_fonts()
    styles = make_styles(regular, bold)
    story = build_story(SOURCE.read_text(encoding="utf-8"), styles)
    document = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=52, leftMargin=52,
        topMargin=48, bottomMargin=48,
        title="Laporan Proyek KerjaYuk",
        author="Tim KerjaYuk · Studi kasus K09",
    )
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"PDF laporan dibuat: {OUTPUT}")


if __name__ == "__main__":
    main()
