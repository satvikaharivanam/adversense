"""
PDF report generator.
Renders the report JSON into HTML via Jinja2, then converts to PDF with WeasyPrint.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

TEMPLATES_DIR = Path(__file__).parent / "templates"

SEVERITY_COLOURS = {
    "critical": "#dc2626",
    "high":     "#ea580c",
    "medium":   "#ca8a04",
    "low":      "#2563eb",
    "none":     "#6b7280",
}


def generate_pdf_report(report_data: Dict[str, Any], output_path: str) -> None:
    """
    Render report_data to a PDF file at output_path.
    """
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report.html")

    findings = report_data.get("findings", [])
    for f in findings:
        sev = f.get("severity", "none").lower()
        f["colour"] = SEVERITY_COLOURS.get(sev, SEVERITY_COLOURS["none"])

    html_content = template.render(
        model_description=report_data.get("model_description", "Unknown model"),
        model_url=report_data.get("model_url", ""),
        audit_date=report_data.get("audit_date", ""),
        job_id=report_data.get("job_id", ""),
        total_probes=report_data.get("total_probes", 0),
        executive_summary=report_data.get("executive_summary", ""),
        overall_grade=report_data.get("overall_grade", "N/A"),
        attack_surface=report_data.get("attack_surface", []),
        findings=findings,
        severity_distribution=report_data.get("severity_distribution", {}),
        recommendations=report_data.get("recommendations", []),
        conclusion=report_data.get("conclusion", ""),
    )

    base_css = CSS(string="""
        @page { size: A4; margin: 2cm 2.5cm; }
        body { font-family: Helvetica, Arial, sans-serif; font-size: 11pt; color: #1a1a1a; line-height: 1.5; }
        h1 { font-size: 22pt; color: #1e3a5f; margin-bottom: 4pt; }
        h2 { font-size: 14pt; color: #1e3a5f; border-bottom: 1px solid #cbd5e1; padding-bottom: 4pt; margin-top: 20pt; }
        table { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin-top: 8pt; }
        th { background: #1e3a5f; color: white; padding: 6pt 8pt; text-align: left; }
        td { padding: 5pt 8pt; border-bottom: 1px solid #e2e8f0; vertical-align: top; }
        tr:nth-child(even) td { background: #f8fafc; }
        .badge { display: inline-block; padding: 2pt 7pt; border-radius: 4pt; color: white; font-size: 8.5pt; font-weight: bold; }
        .grade { font-size: 18pt; font-weight: bold; }
        .meta { color: #64748b; font-size: 9pt; }
        ol { padding-left: 18pt; }
        ol li { margin-bottom: 5pt; }
    """)

    HTML(string=html_content, base_url=str(TEMPLATES_DIR)).write_pdf(
        output_path,
        stylesheets=[base_css],
    )