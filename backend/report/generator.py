"""
PDF report generator using ReportLab — works on all platforms including Render.
"""
from __future__ import annotations

from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

SEVERITY_COLOURS = {
    "critical": colors.HexColor("#dc2626"),
    "high":     colors.HexColor("#ea580c"),
    "medium":   colors.HexColor("#ca8a04"),
    "low":      colors.HexColor("#2563eb"),
    "none":     colors.HexColor("#6b7280"),
}

GRADE_COLOURS = {
    "A": colors.HexColor("#16a34a"),
    "B": colors.HexColor("#2563eb"),
    "C": colors.HexColor("#ca8a04"),
    "D": colors.HexColor("#ea580c"),
    "F": colors.HexColor("#dc2626"),
}


def generate_pdf_report(report_data: Dict[str, Any], output_path: str) -> None:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#1e3a5f"))
    h2_style = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13, textColor=colors.HexColor("#1e3a5f"))
    normal = styles["Normal"]
    small = ParagraphStyle("small", parent=normal, fontSize=9, textColor=colors.HexColor("#64748b"))

    story = []

    # Title
    story.append(Paragraph("AdverSense Robustness Audit Report", title_style))
    story.append(Spacer(1, 0.3 * cm))

    # Metadata
    story.append(Paragraph(f"<b>Model:</b> {report_data.get('model_description', '')}", small))
    story.append(Paragraph(f"<b>Endpoint:</b> {report_data.get('model_url', '')}", small))
    story.append(Paragraph(f"<b>Date:</b> {report_data.get('audit_date', '')}", small))
    story.append(Paragraph(f"<b>Job ID:</b> {report_data.get('job_id', '')}", small))
    story.append(Paragraph(f"<b>Total Probes:</b> {report_data.get('total_probes', 0)}", small))

    # Grade
    grade = report_data.get("overall_grade", "N/A")
    grade_letter = grade[0] if grade else "N"
    grade_colour = GRADE_COLOURS.get(grade_letter, colors.gray)
    grade_style = ParagraphStyle("grade", parent=normal, fontSize=22, textColor=grade_colour)
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(f"<b>Overall Grade: {grade}</b>", grade_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))

    # Executive Summary
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Executive Summary", h2_style))
    story.append(Paragraph(report_data.get("executive_summary", ""), normal))

    # Severity Distribution
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Severity Distribution", h2_style))
    dist = report_data.get("severity_distribution", {})
    sev_data = [["Severity", "Count"]]
    for sev in ["critical", "high", "medium", "low"]:
        sev_data.append([sev.upper(), str(dist.get(sev, 0))])
    sev_table = Table(sev_data, colWidths=[8 * cm, 4 * cm])
    sev_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(sev_table)

    # Findings
    story.append(Spacer(1, 0.3 * cm))
    findings = report_data.get("findings", [])
    story.append(Paragraph(f"Findings ({len(findings)})", h2_style))

    if findings:
        find_data = [["Sev", "Category", "Probe", "Response", "Explanation"]]
        for f in findings:
            find_data.append([
                f.get("severity", "").upper()[:4],
                f.get("category", "")[:15],
                f.get("probe", "")[:40],
                f.get("response", "")[:20],
                f.get("explanation", f.get("reason", ""))[:60],
            ])
        find_table = Table(find_data, colWidths=[1.5*cm, 3*cm, 5*cm, 3*cm, 5*cm])
        find_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(find_table)
    else:
        story.append(Paragraph("No failures discovered.", normal))

    # Recommendations
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Recommendations", h2_style))
    recs = report_data.get("recommendations", [])
    if recs:
        for i, rec in enumerate(recs, 1):
            story.append(Paragraph(f"{i}. {rec}", normal))
            story.append(Spacer(1, 0.1 * cm))
    else:
        story.append(Paragraph("None generated.", normal))

    # Conclusion
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Conclusion", h2_style))
    story.append(Paragraph(report_data.get("conclusion", ""), normal))

    # Footer
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
    story.append(Paragraph(
        f"Generated by AdverSense · Powered by Amazon Nova 2 Lite · {report_data.get('audit_date', '')}",
        ParagraphStyle("footer", parent=normal, fontSize=7, textColor=colors.HexColor("#94a3b8"))
    ))

    doc.build(story)