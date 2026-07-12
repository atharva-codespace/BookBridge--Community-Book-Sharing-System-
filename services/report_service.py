"""
services/report_service.py
Module 6 (Administrative Dashboard & Analytics) menu orchestration. The
underlying data/graph/PDF/email logic already existed and worked correctly
in models/analytics.py, models/reports.py, and models/mail.py - it was just
never reachable from any menu in main.py. This file is the thin wiring
layer that connects them to the Admin Dashboard's "See All Reports" option:
it shows the analytics on screen and automatically emails the generated PDF
to the logged-in admin's own registered email, no extra prompts needed.
"""

from models.admin import Admin
from models.analytics import (
    fetch_books_data,
    fetch_books_summary,
    fetch_users_data,
    fetch_users_summary,
    generate_books_graph,
    generate_users_graph,
)
from models.mail import send_report_email
from models.reports import generate_pdf
from utils.helpers import print_table


class ReportService:
    """Implements the admin 'See All Reports' operation."""

    def __init__(self, session):
        self.session = session

    def show_user_report(self):
        self._show_and_email_report(
            rows_fn=fetch_users_data, summary_fn=fetch_users_summary,
            graph_fn=generate_users_graph, report_title="User Management",
        )

    def show_book_report(self):
        self._show_and_email_report(
            rows_fn=fetch_books_data, summary_fn=fetch_books_summary,
            graph_fn=generate_books_graph, report_title="Book Listing",
        )

    def _show_and_email_report(self, rows_fn, summary_fn, graph_fn, report_title):
        rows = rows_fn()
        summary = summary_fn()
        print_table(rows, title=f"{report_title.upper()} - RAW DATA")
        print_table([{"Metric": k, "Value": v} for k, v in summary.items()],
                    title=f"{report_title} Summary")

        try:
            graph_path = graph_fn(summary)
            pdf_path = generate_pdf(rows, summary, graph_path, report_title)
        except Exception as e:
            print(f"Failed to generate report graph/PDF: {e}")
            return

        admin = Admin.get_by_id(self.session.user_id)
        if not admin or not admin.email:
            print("No admin email on file - PDF was generated but not emailed.")
            return
        
        try:
            send_report_email(admin.email, pdf_path, report_title)
        except Exception as e:
            print(f"PDF generated, but failed to email it: {e}")
