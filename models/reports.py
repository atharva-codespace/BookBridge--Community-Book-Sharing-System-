"""
Modules/reports.py
Builds the PDF report with summary table, graph, and detailed records.
"""

import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from utils import ui


def generate_pdf(rows, summary, graph_path, report_title):
    os.makedirs("Reports", exist_ok=True)
    filename = report_title.replace(" ", "_") + "_Report.pdf"
    path = f"Reports/{filename}"

    doc = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph(f"BookBridge - {report_title} Report", styles["Title"]))
    content.append(Spacer(1, 20))

    content.append(Paragraph("Summary", styles["Heading2"]))
    summary_data = [["Metric", "Value"]] + [[k, v] for k, v in summary.items()]
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    content.append(summary_table)
    content.append(Spacer(1, 20))

    if graph_path and os.path.exists(graph_path):
        content.append(Paragraph("Graphical Overview", styles["Heading2"]))
        content.append(Image(graph_path, width=350, height=220))
        content.append(Spacer(1, 20))

    content.append(Paragraph("Detailed Records", styles["Heading2"]))
    if rows:
        headers = list(rows[0].keys())
        table_data = [headers] + [[str(r[h]) for h in headers] for r in rows]
        detail_table = Table(table_data, repeatRows=1)
        detail_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
        ]))
        content.append(detail_table)
    else:
        content.append(Paragraph("No records found.", styles["Normal"]))

    doc.build(content)
    ui.success(f"PDF created successfully: {path}")
    return path