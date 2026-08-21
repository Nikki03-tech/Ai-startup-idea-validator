"""
PDF Report Generator

Builds a professional, multi-section PDF of the AI Startup Idea
Validator's final validation report using ReportLab (Platypus).

This is a pure formatting/rendering utility - it never calls the LLM
pipeline and never invents data. It only renders whatever is already
in the real, generated `report` dict (see agents/report_agent.py for
its shape) plus the user's submitted idea recap.
"""

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ---------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------

_PRIMARY = colors.HexColor("#6b21a8")
_PRIMARY_LIGHT = colors.HexColor("#f3e8ff")
_TEXT = colors.HexColor("#1f1f24")
_MUTED = colors.HexColor("#5b5b66")
_BORDER = colors.HexColor("#d8b4fe")


def _build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=_PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=_MUTED,
        alignment=TA_CENTER,
        spaceAfter=18,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=17,
        textColor=_PRIMARY,
        spaceBefore=16,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="SubHeading",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=_TEXT,
        spaceBefore=8,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="Body",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=_TEXT,
        alignment=TA_LEFT,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="BodyMuted",
        parent=styles["Body"],
        textColor=_MUTED,
    ))

    styles.add(ParagraphStyle(
        name="BulletItem",
        parent=styles["Body"],
        spaceAfter=3,
    ))

    styles.add(ParagraphStyle(
        name="ScoreValue",
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=32,
        textColor=_PRIMARY,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name="ScoreLabel",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=_MUTED,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name="ReferenceItem",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1d4ed8"),
        spaceAfter=3,
    ))

    return styles


def _escape(text) -> str:
    """Escape text that will be placed inside a ReportLab Paragraph's XML-like markup."""

    text = text if text not in (None, "") else "Not available."
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _p(text, style):
    """Paragraph helper for plain (unformatted) text - always escapes its input."""

    return Paragraph(_escape(text), style)


def _labeled_p(label, value, style):
    """
    Paragraph helper for a "<b>Label:</b> value" line. The label is
    trusted static text (safe to leave as real markup); the value may
    come from LLM output or user input, so it is escaped before being
    inserted, without disturbing the bold tag around the label.
    """

    return Paragraph(f"<b>{label}:</b> {_escape(value)}", style)


def _raw_p(markup, style):
    """Paragraph helper for fully static, trusted markup (e.g. plain bold labels)."""

    return Paragraph(markup, style)


def _bullet_list(items, styles, empty_text="None reported."):
    """
    Render a list of strings (or dicts with a 'feature'/'risk'/'channel'
    key, matching the same extraction logic used in report_viewer.py)
    as a bulleted ListFlowable so long items wrap instead of overflowing.
    """

    if not items:
        return _p(empty_text, styles["BodyMuted"])

    entries = []
    for item in items:
        if isinstance(item, dict):
            text = (
                item.get("feature")
                or item.get("risk")
                or item.get("channel")
                or item.get("model")
                or str(item)
            )
        else:
            text = str(item)

        entries.append(ListItem(_p(text, styles["BulletItem"]), leftIndent=10))

    return ListFlowable(
        entries,
        bulletType="bullet",
        start="circle",
        leftIndent=12,
        bulletFontSize=6,
    )


def _divider():
    return HRFlowable(
        width="100%",
        thickness=0.75,
        color=_BORDER,
        spaceBefore=4,
        spaceAfter=10,
    )


# ---------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------

def _header_section(story, styles, display_title, idea):
    story.append(_p(f"Startup Validation Report", styles["ReportTitle"]))
    story.append(_p(display_title or "Your Startup", styles["ReportSubtitle"]))
    story.append(_p(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        styles["ReportSubtitle"],
    ))
    story.append(_divider())


def _score_section(story, styles, report):
    score = report.get("final_validation_score")
    score_text = f"{score}/100" if score is not None else "N/A"

    table = Table(
        [[_p(score_text, styles["ScoreValue"])],
         [_p("VALIDATION SCORE", styles["ScoreLabel"])]],
        colWidths=[2.2 * inch],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _PRIMARY_LIGHT),
        ("BOX", (0, 0), (-1, -1), 1, _BORDER),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    wrapper = Table([[table]], colWidths=[6.4 * inch])
    wrapper.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(wrapper)
    story.append(Spacer(1, 12))


def _idea_recap_section(story, styles, idea):
    story.append(_p("Submitted Idea", styles["SectionHeading"]))
    story.append(_labeled_p("Startup Idea", idea.get('idea', 'N/A'), styles["Body"]))
    story.append(_labeled_p("Target Audience", idea.get('target_audience', 'N/A'), styles["Body"]))
    story.append(_labeled_p("Industry", idea.get('industry', 'N/A'), styles["Body"]))
    story.append(_labeled_p("Problem Statement", idea.get('problem', 'N/A'), styles["Body"]))
    story.append(_labeled_p("Proposed Solution", idea.get('solution', 'N/A'), styles["Body"]))
    story.append(_divider())


def _executive_summary_section(story, styles, report):
    story.append(_p("Executive Summary", styles["SectionHeading"]))
    story.append(_p(report.get("executive_summary"), styles["Body"]))
    story.append(_divider())


def _market_analysis_section(story, styles, market_analysis):
    story.append(_p("Market Analysis", styles["SectionHeading"]))

    if not market_analysis:
        story.append(_p("Not available.", styles["BodyMuted"]))
    else:
        fields = [
            ("Market Size", "market_size"),
            ("Target Audience", "target_audience"),
            ("Industry Trends", "industry_trends"),
            ("Opportunities", "opportunities"),
            ("Market Potential", "market_potential"),
        ]
        for label, key in fields:
            story.append(_labeled_p(label, market_analysis.get(key, 'N/A'), styles["Body"]))

    story.append(_divider())


def _competitor_section(story, styles, competitors):
    story.append(_p("Competitor Analysis", styles["SectionHeading"]))

    if not competitors:
        story.append(_p("No competitors found.", styles["BodyMuted"]))
        story.append(_divider())
        return

    for competitor in competitors:
        if not isinstance(competitor, dict):
            competitor = {"name": str(competitor)}

        block = [
            _p(competitor.get("name", "Unknown"), styles["SubHeading"]),
        ]

        if competitor.get("website"):
            block.append(_labeled_p("Website", competitor['website'], styles["BodyMuted"]))

        if competitor.get("description"):
            block.append(_p(competitor["description"], styles["Body"]))

        strengths = competitor.get("strengths") or []
        weaknesses = competitor.get("weaknesses") or []

        combo_table = Table(
            [[
                [_raw_p("<b>Strengths</b>", styles["Body"]), _bullet_list(strengths, styles)],
                [_raw_p("<b>Weaknesses</b>", styles["Body"]), _bullet_list(weaknesses, styles)],
            ]],
            colWidths=[3.1 * inch, 3.1 * inch],
        )
        combo_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (0, 0), 14),
        ]))
        block.append(combo_table)
        block.append(Spacer(1, 8))

        story.append(KeepTogether(block))

    story.append(_divider())


def _swot_section(story, styles, swot):
    story.append(_p("SWOT Analysis", styles["SectionHeading"]))

    if not swot:
        story.append(_p("Not available.", styles["BodyMuted"]))
        story.append(_divider())
        return

    quad_table = Table(
        [[
            [_raw_p("<b>Strengths</b>", styles["Body"]), _bullet_list(swot.get("strengths"), styles)],
            [_raw_p("<b>Weaknesses</b>", styles["Body"]), _bullet_list(swot.get("weaknesses"), styles)],
        ], [
            [_raw_p("<b>Opportunities</b>", styles["Body"]), _bullet_list(swot.get("opportunities"), styles)],
            [_raw_p("<b>Threats</b>", styles["Body"]), _bullet_list(swot.get("threats"), styles)],
        ]],
        colWidths=[3.1 * inch, 3.1 * inch],
    )
    quad_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(quad_table)

    risks = swot.get("risks") or []
    if risks:
        story.append(_p("Risks & Mitigation", styles["SubHeading"]))

        rows = [[
            _raw_p("<b>Risk</b>", styles["Body"]),
            _raw_p("<b>Severity</b>", styles["Body"]),
            _raw_p("<b>Mitigation</b>", styles["Body"]),
        ]]
        for risk in risks:
            rows.append([
                _p(risk.get("risk", "N/A"), styles["Body"]),
                _p(risk.get("severity", "N/A"), styles["Body"]),
                _p(risk.get("mitigation", "N/A"), styles["Body"]),
            ])

        risk_table = Table(rows, colWidths=[2.2 * inch, 0.9 * inch, 3.1 * inch], repeatRows=1)
        risk_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _PRIMARY_LIGHT),
            ("GRID", (0, 0), (-1, -1), 0.5, _BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(risk_table)

    story.append(_divider())


def _mvp_section(story, styles, mvp):
    story.append(_p("MVP Recommendation", styles["SectionHeading"]))

    if not mvp:
        story.append(_p("Not available.", styles["BodyMuted"]))
    else:
        story.append(_p("Must Have", styles["SubHeading"]))
        story.append(_bullet_list(mvp.get("must_have"), styles))

        story.append(_p("Nice to Have", styles["SubHeading"]))
        story.append(_bullet_list(mvp.get("nice_to_have"), styles))

        if mvp.get("prioritization_rationale"):
            story.append(_p("Prioritization Rationale", styles["SubHeading"]))
            story.append(_p(mvp["prioritization_rationale"], styles["Body"]))

    story.append(_divider())


def _gtm_section(story, styles, gtm):
    story.append(_p("Go-To-Market Strategy", styles["SectionHeading"]))

    if not gtm:
        story.append(_p("Not available.", styles["BodyMuted"]))
    else:
        if gtm.get("positioning_strategy"):
            story.append(_p(gtm["positioning_strategy"], styles["Body"]))

        story.append(_p("Customer Acquisition Channels", styles["SubHeading"]))
        story.append(_bullet_list(gtm.get("customer_acquisition_channels"), styles))

        story.append(_p("Launch Strategy", styles["SubHeading"]))
        story.append(_bullet_list(gtm.get("launch_strategy"), styles))

    story.append(_divider())


def _references_section(story, styles, references):
    story.append(_p("Sources & References", styles["SectionHeading"]))

    if not references:
        story.append(_p("No sources recorded for this run.", styles["BodyMuted"]))
        return

    for i, url in enumerate(references, start=1):
        story.append(_p(f"[{i}] {url}", styles["ReferenceItem"]))


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(_MUTED)
    canvas.drawCentredString(
        doc.pagesize[0] / 2,
        0.5 * inch,
        f"AI Startup Idea Validator - Page {doc.page}",
    )
    canvas.restoreState()


# ---------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------

def generate_pdf_report(report: dict, idea: dict) -> bytes:
    """
    Build a PDF of the actual generated validation report.

    Parameters
    ----------
    report:
        The `report` dict produced by ReportAgent / pipeline/graph.py
        (final_state["report"]). Must be the real, completed report -
        this function does not run the pipeline itself.

    idea:
        The idea recap dict already stored in st.session_state["idea"]
        (idea/target_audience/industry/problem/solution/display_title).

    Returns
    -------
    Raw PDF bytes, ready for st.download_button.
    """

    report = report or {}
    idea = idea or {}

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        title="Startup Validation Report",
    )

    styles = _build_styles()
    story = []

    display_title = idea.get("display_title") or idea.get("idea") or "Your Startup"

    _header_section(story, styles, display_title, idea)
    _score_section(story, styles, report)
    _idea_recap_section(story, styles, idea)
    _executive_summary_section(story, styles, report)
    _market_analysis_section(story, styles, report.get("market_analysis") or {})
    _competitor_section(story, styles, report.get("competitor_analysis") or [])
    _swot_section(story, styles, report.get("swot_analysis") or {})
    _mvp_section(story, styles, report.get("mvp_recommendation") or {})
    _gtm_section(story, styles, report.get("gtm_strategy") or {})
    _references_section(story, styles, report.get("references") or [])

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)

    return buffer.getvalue()
