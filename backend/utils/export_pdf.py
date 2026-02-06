"""
PDF export utility for generating inception pack PDFs.

Uses WeasyPrint for HTML-to-PDF conversion with Jinja2 templating.
"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# Template directory
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def generate_pdf(pack: dict[str, Any], section: str | None = None) -> bytes:
    """
    Generate a PDF from an inception pack.

    Args:
        pack: The inception pack dictionary containing all sections.
        section: Optional section name to export only that section.
                 If None, exports the full pack.

    Returns:
        bytes: The generated PDF content.

    Raises:
        FileNotFoundError: If the template file is not found.
        jinja2.TemplateError: If template rendering fails.
    """
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=True,
    )
    template = env.get_template("inception_pack.html")
    html_content = template.render(pack=pack, section=section)
    return HTML(string=html_content).write_pdf()


def get_pdf_filename(session_id: str, section: str | None = None) -> str:
    """
    Generate a filename for the PDF export.

    Args:
        session_id: The session ID.
        section: Optional section name.

    Returns:
        str: The suggested filename.
    """
    short_id = session_id[:8]
    if section:
        return f"{section.replace('_', '-')}-{short_id}.pdf"
    return f"inception-pack-{short_id}.pdf"
