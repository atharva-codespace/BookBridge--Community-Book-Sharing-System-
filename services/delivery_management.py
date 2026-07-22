"""
services/delivery_management.py
Admin-only operations for the Delivery module: creating delivery boy
accounts (only an admin may do this - no self-registration), viewing /
activating / deactivating / deleting them, and assigning a delivery boy to
an approved request's Delivery record. Every method here assumes the
caller has already passed the Authorization.require_admin() check in
main.py.

Presentation note: only the printed messages/prompts/tables have been
upgraded to utils/ui.py styling. Every field, validation rule, and
database call is unchanged.
"""

from models.delivery import Delivery
from models.delivery_boy import DeliveryBoy
from services.validation import Validation
from utils.hashing import Hashing
from utils import ui
from utils.helpers import confirm_action, print_table

DELIVERY_BOY_FIELDS = ["Delivery_Boy_ID", "Username", "Full_Name", "Email",
                       "Phone_Number", "Vehicle_Info", "Account_Status"]
DELIVERY_FIELDS = ["Delivery_ID", "Request_ID", "Book_Name", "Delivery_Boy_ID",
                   "Pickup_Location", "Drop_Location", "Expected_Delivery_Date", "Status"]


def _delivery_boy_to_row(d):
    return {"Delivery_Boy_ID": d.delivery_boy_id, "Username": d.username,
            "Full_Name": d.full_name, "Email": d.email, "Phone_Number": d.phone_number,
            "Vehicle_Info": d.vehicle_info, "Account_Status": d.account_status}


def _delivery_to_row(d):
    return {"Delivery_ID": d.delivery_id, "Request_ID": d.request_id, "Book_Name": d.book_name,
            "Delivery_Boy_ID": d.delivery_boy_id, "Pickup_Location": d.pickup_location,
            "Drop_Location": d.drop_location, "Expected_Delivery_Date": d.expected_delivery_date,
            "Status": d.status}


class DeliveryManagement:
    """Implements every admin-side Delivery Management operation."""

    def __init__(self, session):
        self.session = session

    # ==================== REGISTER DELIVERY BOY (admin-only) ====================
    def register_delivery_boy(self):
        ui.section_header("REGISTER NEW DELIVERY BOY", icon="🚚")
        try:
            full_name = ui.prompt("Full Name").strip()
            if not Validation.validate_name(full_name):
                ui.error("Invalid name. Registration cancelled.")
                return

            email = ui.prompt("Email").strip()
            if not Validation.validate_email(email):
                ui.error("Invalid email format. Registration cancelled.")
                return
            if DeliveryBoy.get_by_email(email):
                ui.error("A delivery boy with this email already exists.")
                return

            phone = ui.prompt("Phone Number (10 digits)").strip()
            if not Validation.validate_phone(phone):
                ui.error("Invalid phone number. Registration cancelled.")
                return

            username = ui.prompt("Username").strip()
            if not Validation.validate_not_empty(username):
                ui.error("Username cannot be empty.")
                return
            if DeliveryBoy.get_by_username(username):
                ui.error("This username is already taken.")
                return

            password = ui.prompt("Password", password=True).strip()
            valid, reason = Validation.validate_password_strength(password)
            if not valid:
                ui.error(reason)
                return
            confirm_password = ui.prompt("Confirm Password", password=True).strip()
            if password != confirm_password:
                ui.error("Passwords do not match. Registration cancelled.")
                return

            vehicle_info = ui.prompt("Vehicle Info (e.g. Bike - MH12AB1234, optional)").strip() or None

            password_hash = Hashing.hash_password(password)
            DeliveryBoy.create(full_name, email, phone, username, password_hash,
                               vehicle_info, created_by=self.session.username)
            ui.success(f"Delivery boy '{username}' registered successfully.")

        except Exception as e:
            ui.error(f"Failed to register delivery boy: {e}")

    # ==================== VIEW / ACTIVATE / DEACTIVATE / DELETE ====================
    def view_delivery_boys(self):
        boys = DeliveryBoy.get_all()
        print_table([_delivery_boy_to_row(d) for d in boys], headers=DELIVERY_BOY_FIELDS,
                    title="ALL DELIVERY BOYS")

    def activate_delivery_boy(self):
        boy = self._select_delivery_boy_by_id("activate")
        if boy:
            DeliveryBoy.update_status(boy.delivery_boy_id, "Active")
            ui.success(f"Delivery boy '{boy.username}' has been activated.")

    def deactivate_delivery_boy(self):
        boy = self._select_delivery_boy_by_id("deactivate")
        if boy:
            DeliveryBoy.update_status(boy.delivery_boy_id, "Inactive")
            ui.success(f"Delivery boy '{boy.username}' has been deactivated.")

    def delete_delivery_boy(self):
        boy = self._select_delivery_boy_by_id("delete")
        if boy and confirm_action(f"Confirm permanent deletion of '{boy.username}'?"):
            DeliveryBoy.delete(boy.delivery_boy_id)
            ui.success(f"Delivery boy '{boy.username}' has been deleted.")
        elif boy:
            ui.warning("Deletion cancelled.")

    def _select_delivery_boy_by_id(self, action_name):
        did = ui.prompt(f"Enter Delivery Boy ID to {action_name}").strip()
        if not did.isdigit():
            ui.error("Invalid Delivery Boy ID.")
            return None
        boy = DeliveryBoy.get_by_id(int(did))
        if not boy:
            ui.error("Delivery boy not found.")
        return boy

    # ==================== ASSIGNMENT ====================
    def view_unassigned_deliveries(self):
        deliveries = Delivery.get_unassigned()
        print_table([_delivery_to_row(d) for d in deliveries], headers=DELIVERY_FIELDS,
                    title="UNASSIGNED DELIVERIES")

    def view_all_deliveries(self):
        deliveries = Delivery.get_all()
        print_table([_delivery_to_row(d) for d in deliveries], headers=DELIVERY_FIELDS,
                    title="ALL DELIVERIES")

    def assign_delivery_boy(self):
        deliveries = Delivery.get_unassigned()
        print_table([_delivery_to_row(d) for d in deliveries], headers=DELIVERY_FIELDS,
                    title="UNASSIGNED DELIVERIES")
        if not deliveries:
            return

        did = ui.prompt("Enter Delivery ID to assign (or press Enter to go back)").strip()
        if not did:
            return
        if not did.isdigit():
            ui.error("Invalid Delivery ID.")
            return
        delivery = Delivery.get_by_id(int(did))
        if not delivery or delivery.status != "Pending":
            ui.error("No unassigned delivery with that ID.")
            return

        boys = DeliveryBoy.get_all_active()
        print_table([_delivery_boy_to_row(d) for d in boys], headers=DELIVERY_BOY_FIELDS,
                    title="ACTIVE DELIVERY BOYS")
        if not boys:
            ui.warning("No active delivery boys to assign. Register one first.")
            return

        bid = ui.prompt("Enter Delivery Boy ID to assign this delivery to").strip()
        if not bid.isdigit():
            ui.error("Invalid Delivery Boy ID.")
            return
        boy = DeliveryBoy.get_by_id(int(bid))
        if not boy or boy.account_status != "Active":
            ui.error("No active delivery boy with that ID.")
            return

        Delivery.assign(delivery.delivery_id, boy.delivery_boy_id)
        ui.success(f"Delivery #{delivery.delivery_id} ('{delivery.book_name}') assigned to "
                   f"{boy.full_name} ({boy.username}).")
