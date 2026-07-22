"""
services/report_service.py
Module 6 (Administrative Dashboard & Analytics) menu orchestration. The
underlying data/graph/PDF/email logic already existed and worked correctly
in models/analytics.py, models/reports.py, and models/mail.py - it was just
never reachable from any menu in main.py. This file is the thin wiring
layer that connects them to the Admin Dashboard's "See All Reports" option:
it shows the analytics on screen and automatically emails the generated PDF
to the logged-in admin's own registered email, no extra prompts needed.

Presentation note: the raw-data table is now paired with a highlighted
summary stat panel, and graph/PDF generation runs behind a loading spinner.
The underlying data fetch, graph generation, PDF creation, and email
sending calls are all unchanged.
"""

from models.admin import Admin
from models.analytics import (
    fetch_books_data,
    fetch_books_summary,
    fetch_requests_data,
    fetch_requests_summary,
    fetch_reservations_data,
    fetch_reservations_summary,
    fetch_reviews_data,
    fetch_reviews_summary,
    fetch_users_data,
    fetch_users_summary,
    fetch_wishlist_data,
    fetch_wishlist_summary,
    generate_books_graph,
    generate_requests_graph,
    generate_reservations_graph,
    generate_reviews_graph,
    generate_users_graph,
    generate_wishlist_graph,
)
from models.mail import send_report_email
from models.reports import generate_pdf
from utils import ui
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

    def show_requests_report(self):
        self._show_and_email_report(
            rows_fn=fetch_requests_data, summary_fn=fetch_requests_summary,
            graph_fn=generate_requests_graph, report_title="Book Requests",
        )

    def show_reservations_report(self):
        self._show_and_email_report(
            rows_fn=fetch_reservations_data, summary_fn=fetch_reservations_summary,
            graph_fn=generate_reservations_graph, report_title="Reservations",
        )

    def show_reviews_report(self):
        self._show_and_email_report(
            rows_fn=fetch_reviews_data, summary_fn=fetch_reviews_summary,
            graph_fn=generate_reviews_graph, report_title="Reviews & Ratings",
        )

    def show_wishlist_report(self):
        self._show_and_email_report(
            rows_fn=fetch_wishlist_data, summary_fn=fetch_wishlist_summary,
            graph_fn=generate_wishlist_graph, report_title="Wishlist",
        )

    def _show_and_email_report(self, rows_fn, summary_fn, graph_fn, report_title):
        rows = rows_fn()
        summary = summary_fn()
        print_table(rows, title=f"{report_title.upper()} - RAW DATA")
        ui.stat_panel(f"{report_title} Summary", summary)

        try:
            with ui.spinner("Generating report graph and PDF"):
                graph_path = graph_fn(summary)
                pdf_path = generate_pdf(rows, summary, graph_path, report_title)
        except Exception as e:
            ui.error(f"Failed to generate report graph/PDF: {e}")
            return

        admin = Admin.get_by_id(self.session.user_id)
        if not admin or not admin.email:
            ui.warning("No admin email on file - PDF was generated but not emailed.")
            return

        try:
            with ui.spinner("Emailing report"):
                send_report_email(admin.email, pdf_path, report_title)
            ui.success(f"Report emailed to {admin.email}.")
        except Exception as e:
            ui.warning(f"PDF generated, but failed to email it: {e}")
