"""Report exporters for Excel and PDF."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def _to_dataframe(results: pd.DataFrame | Mapping[str, Any] | Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    if isinstance(results, pd.DataFrame):
        return results
    if isinstance(results, Mapping):
        return pd.DataFrame([results])
    return pd.DataFrame(list(results))


def export_results_excel(
    results: pd.DataFrame | Mapping[str, Any] | Sequence[Mapping[str, Any]],
    output_path: str | Path,
) -> Path:
    """Export tabular results to an XLSX file."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    dataframe = _to_dataframe(results)
    dataframe.to_excel(output, index=False)
    return output


def export_summary_pdf(
    title: str,
    sections: Sequence[tuple[str, str]],
    output_path: str | Path,
) -> Path:
    """Export a compact text summary PDF."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    pdf = canvas.Canvas(str(output), pagesize=A4)
    width, height = A4

    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, title)
    y -= 30

    for section_title, section_text in sections:
        if y < 80:
            pdf.showPage()
            y = height - 50

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(40, y, section_title)
        y -= 18

        pdf.setFont("Helvetica", 10)
        for line in section_text.splitlines() or [""]:
            if y < 60:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 10)
            pdf.drawString(50, y, line[:120])
            y -= 14

        y -= 8

    pdf.save()
    return output
