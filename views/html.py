"""
views/html.py - HTML rendering via Jinja2
"""

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from core.analytics import ReportData, UNKNOWN_CATEGORY


# Templates folder is at the project root, next to this views/ folder
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def _make_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def render_html(report: ReportData) -> str:
    """Render the report to an HTML string."""
    env = _make_env()
    template = env.get_template("report.html")

    return template.render(
        report=report,
        unknown_category=UNKNOWN_CATEGORY,
        now=datetime.now().strftime("%d.%m.%Y %H:%M"),
    )


def save_html_report(report: ReportData, output_path: str = "reports/report.html") -> None:
    """Render and write report to disk."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    html = render_html(report)
    out_file.write_text(html, encoding="utf-8")

    print(f"\n💾 Report saved to: {out_file.resolve()}")