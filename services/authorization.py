"""
services/authorization.py
Handles role-based access control (RBAC) for the application (Feature 13).
Only administrators may access the Admin Dashboard, User Management,
Admin Creation, and Promotion features. Any attempt by a regular user
(or an unauthenticated session) is denied.
"""


class Authorization:
    """Centralizes every access-control check used by main.py and the services."""

    @staticmethod
    def is_admin(session) -> bool:
        return session.is_authenticated and session.user_type == "admin"

    @staticmethod
    def is_user(session) -> bool:
        return session.is_authenticated and session.user_type == "user"

    @staticmethod
    def is_delivery_boy(session) -> bool:
        return session.is_authenticated and session.user_type == "delivery_boy"

    @staticmethod
    def require_admin(session) -> bool:
        """Returns True if allowed, otherwise prints ACCESS DENIED and returns False."""
        if not Authorization.is_admin(session):
            print("\nACCESS DENIED")
            return False
        return True

    @staticmethod
    def require_user(session) -> bool:
        """Returns True if allowed, otherwise prints ACCESS DENIED and returns False."""
        if not Authorization.is_user(session):
            print("\nACCESS DENIED")
            return False
        return True

    @staticmethod
    def require_delivery_boy(session) -> bool:
        """Returns True if allowed, otherwise prints ACCESS DENIED and returns False."""
        if not Authorization.is_delivery_boy(session):
            print("\nACCESS DENIED")
            return False
        return True
