"""
services/delivery_service.py
Delivery Boy dashboard operations: view the deliveries assigned to me
(book, pickup details, drop details, expected date), and move each one
through the pickup -> delivered workflow.
"""

from datetime import date

from models.delivery import Delivery
from utils.helpers import print_table

MY_DELIVERY_FIELDS = ["Delivery_ID", "Book_Name", "Pickup_Name", "Pickup_Phone",
                      "Pickup_Location", "Drop_Name", "Drop_Phone", "Drop_Location",
                      "Expected_Delivery_Date", "Status"]


def _delivery_to_row(d):
    return {"Delivery_ID": d.delivery_id, "Book_Name": d.book_name,
            "Pickup_Name": d.pickup_name, "Pickup_Phone": d.pickup_phone,
            "Pickup_Location": d.pickup_location, "Drop_Name": d.drop_name,
            "Drop_Phone": d.drop_phone, "Drop_Location": d.drop_location,
            "Expected_Delivery_Date": d.expected_delivery_date, "Status": d.status}


class DeliveryService:
    """Implements every Delivery Boy dashboard operation."""

    def __init__(self, session):
        self.session = session

    def view_my_deliveries(self):
        deliveries = Delivery.get_by_delivery_boy(self.session.user_id)
        print_table([_delivery_to_row(d) for d in deliveries], headers=MY_DELIVERY_FIELDS,
                    title="MY ASSIGNED DELIVERIES")

    def mark_picked_up(self):
        delivery = self._select_own_delivery("Assigned")
        if not delivery:
            return
        Delivery.update_status(delivery.delivery_id, "Picked Up")
        print(f"Delivery #{delivery.delivery_id} ('{delivery.book_name}') marked as Picked Up.")

    def mark_delivered(self):
        delivery = self._select_own_delivery("Picked Up")
        if not delivery:
            return
        Delivery.update_status(delivery.delivery_id, "Delivered", delivered_date=date.today())
        print(f"Delivery #{delivery.delivery_id} ('{delivery.book_name}') marked as Delivered.")

    def _select_own_delivery(self, required_status):
        did = input("Enter Delivery ID: ").strip()
        if not did.isdigit():
            print("Invalid Delivery ID.")
            return None
        delivery = Delivery.get_by_id(int(did))
        if not delivery or delivery.delivery_boy_id != self.session.user_id:
            print("Delivery not found.")
            return None
        if delivery.status != required_status:
            print(f"This delivery must be '{required_status}' first (it is currently '{delivery.status}').")
            return None
        return delivery
