"""Build a readable proof-and-simulation PDF from the committed Markdown."""
from __future__ import annotations

from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Preformatted, Image, KeepTogether)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "GMT_Proofs_and_Simulations.pdf"
PAPER = ROOT / "paper" / "GMT_v0.1.md"
PROOFS = ROOT / "proofs" / "PROOFS.md"
NOVELTY = ROOT / "docs" / "NOVELTY_AND_SCOPE.md"
RESULTS = ROOT / "simulation" / "results"


def inline_markup(s: str) -> str:
    s = escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    s = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
               lambda m: f'<link href="{escape(m.group(2), quote=True)}" color="#245a87">{m.group(1)}</link>', s)
    return s


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d8dee8"))
    canvas.line(18 * mm, 15 * mm, 192 * mm, 15 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#526175"))
    canvas.drawString(18 * mm, 10 * mm, "Maths | GMT v0.1.0 | Mrityunjay K")
    canvas.drawRightString(192 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def parse_markdown(path: Path, styles, story) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    paragraph_lines: list[str] = []
    bullets: list[str] = []
    code_lines: list[str] = []
    in_code = False

    def flush_paragraph():
        nonlocal paragraph_lines
        if paragraph_lines:
            txt = " ".join(x.strip() for x in paragraph_lines)
            story.append(Paragraph(inline_markup(txt), styles["Body"]))
            story.append(Spacer(1, 3))
            paragraph_lines = []

    def flush_bullets():
        nonlocal bullets
        for item in bullets:
            story.append(Paragraph("• " + inline_markup(item), styles["BulletCustom"]))
        if bullets:
            story.append(Spacer(1, 3))
        bullets = []

    def flush_all():
        flush_paragraph()
        flush_bullets()

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("```"):
            flush_all()
            if in_code:
                story.append(Preformatted(escape("\n".join(code_lines), quote=False), styles["Code"]))
                story.append(Spacer(1, 5))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            flush_all()
            continue
        if line.startswith("!["):
            flush_all()
            continue
        if line.strip() in ("---", "***"):
            flush_all()
            story.append(Spacer(1, 6))
            story.append(Paragraph("—" * 42, styles["Small"]))
            story.append(Spacer(1, 6))
            continue
        if line.startswith("#"):
            flush_all()
            level = len(line) - len(line.lstrip("#"))
            text = line[level:].strip()
            if level == 1:
                style = styles["Heading1Custom"]
            elif level == 2:
                style = styles["Heading2Custom"]
            else:
                style = styles["Heading3Custom"]
            story.append(Paragraph(inline_markup(text), style))
            story.append(Spacer(1, 4))
            continue
        if line.startswith("- ") or line.startswith("* "):
            flush_paragraph()
            bullets.append(line[2:].strip())
            continue
        if re.match(r"^\d+\.\s+", line):
            flush_paragraph()
            bullets.append(re.sub(r"^\d+\.\s+", "— ", line).strip())
            continue
        # Treat residual table separators as compact text rather than dropping data.
        if re.match(r"^[|\s:|-]+$", line):
            continue
        paragraph_lines.append(line)

    flush_all()
    if in_code and code_lines:
        story.append(Preformatted(escape("\n".join(code_lines), quote=False), styles["Code"]))


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=25, leading=31, alignment=TA_CENTER,
                              textColor=colors.HexColor("#17365d"), spaceAfter=12))
    styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontSize=13, leading=18,
                              alignment=TA_CENTER, textColor=colors.HexColor("#43566f")))
    styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], fontName="Helvetica",
                              fontSize=9.1, leading=13, spaceAfter=4, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="BulletCustom", parent=styles["BodyText"], fontSize=8.9,
                              leading=12.5, leftIndent=12, firstLineIndent=0, spaceAfter=2))
    styles.add(ParagraphStyle(name="Heading1Custom", parent=styles["Heading1"], fontSize=17,
                              leading=21, textColor=colors.HexColor("#17365d"), spaceBefore=8))
    styles.add(ParagraphStyle(name="Heading2Custom", parent=styles["Heading2"], fontSize=12.5,
                              leading=16, textColor=colors.HexColor("#245a87"), spaceBefore=7))
    styles.add(ParagraphStyle(name="Heading3Custom", parent=styles["Heading3"], fontSize=10.5,
                              leading=14, textColor=colors.HexColor("#34465e"), spaceBefore=5))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10,
                              textColor=colors.HexColor("#667085")))
    styles.add(ParagraphStyle(name="Code", fontName="Courier", fontSize=7.4, leading=10,
                              leftIndent=7, rightIndent=7, borderWidth=0.4,
                              borderColor=colors.HexColor("#d8dee8"), borderPadding=6,
                              backColor=colors.HexColor("#f5f7fa"), spaceBefore=3, spaceAfter=7))

    doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                            topMargin=17*mm, bottomMargin=22*mm,
                            title="GMT Proofs and Simulations — Mrityunjay K",
                            author="Mrityunjay K",
                            subject="Gradient-Memory Transport model, theorem proofs, tests, and numerical experiments")
    story = [
        Spacer(1, 34*mm),
        Paragraph("Gradient-Memory Transport", styles["CoverTitle"]),
        Paragraph("Proofs, Numerical Simulations, and Research Scope", styles["CoverSub"]),
        Spacer(1, 12*mm),
        Paragraph("<b>Prepared for Mrityunjay K</b>", styles["CoverSub"]),
        Spacer(1, 5*mm),
        Paragraph("Research snapshot v0.1.0 · 13 October 2026", styles["CoverSub"]),
        Spacer(1, 16*mm),
        Paragraph("A proposed mathematical model of transport on finite graphs, with explicit assumptions, theorem proofs, automated numerical checks, and a reproducible research plan.", styles["Body"]),
        Spacer(1, 8*mm),
        Paragraph("<b>Scientific status:</b> exploratory mathematical research. Not peer reviewed, not experimentally validated as a physical law, and not a claim of 100% global novelty.", styles["Body"]),
        PageBreak(),
        Paragraph("Contents of this report", styles["Heading1Custom"]),
        Paragraph("Part I: manuscript and governing model", styles["Body"]),
        Paragraph("Part II: mathematical proofs", styles["Body"]),
        Paragraph("Part III: novelty and scope audit", styles["Body"]),
        Paragraph("Part IV: generated numerical figures", styles["Body"]),
        PageBreak(),
    ]

    parse_markdown(PAPER, styles, story)
    story.append(PageBreak())
    parse_markdown(PROOFS, styles, story)
    story.append(PageBreak())
    parse_markdown(NOVELTY, styles, story)

    figure_specs = [
        ("path_potentials.png", "Figure A. Node trajectories on the path graph."),
        ("energy_bound.png", "Figure B. Quadratic Lyapunov energy and the analytic rate bound."),
        ("tau_sweep.png", "Figure C. Numerical energy trajectories for the memory-timescale sweep."),
    ]
    existing = [(RESULTS / name, caption) for name, caption in figure_specs if (RESULTS / name).exists()]
    if existing:
        story.append(PageBreak())
        story.append(Paragraph("Generated simulation figures", styles["Heading1Custom"]))
        story.append(Paragraph("These figures are numerical checks of the specified model and do not constitute empirical evidence about a physical system.", styles["Body"]))
        for path, caption in existing:
            story.append(Spacer(1, 5))
            img = Image(str(path))
            img._restrictSize(165*mm, 95*mm)
            story.append(KeepTogether([img, Paragraph(caption, styles["Small"])]))
            story.append(Spacer(1, 8))

    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)
    print(f"Created {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
