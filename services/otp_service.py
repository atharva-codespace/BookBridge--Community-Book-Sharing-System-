"""
services/otp_service.py

Handles Email OTP generation, sending,
verification, expiry timer and resend OTP.

Presentation note: only the printed messages/prompts have been upgraded to
utils/ui.py styling. OTP generation, expiry, and attempt-counting logic is
unchanged.
"""

import random
from datetime import datetime, timedelta

from utils.email_sender import send_email_otp
from utils import ui


class OTPService:
    """Email OTP Verification Service"""

    OTP_LENGTH = 6
    OTP_VALIDITY_MINUTES = 5
    MAX_ATTEMPTS = 3

    def __init__(self):
        self.__otp = None
        self.__email = None
        self.__expiry_time = None
        self.__attempts = 0

    # =====================================================
    # Generate OTP
    # =====================================================

    def generate_otp(self):
        """Generate a random 6-digit OTP."""

        self.__otp = "".join(
            str(random.randint(0, 9))
            for _ in range(self.OTP_LENGTH)
        )

        self.__expiry_time = (
            datetime.now()
            + timedelta(minutes=self.OTP_VALIDITY_MINUTES)
        )

        self.__attempts = 0

        return self.__otp

    # =====================================================
    # Check Expiry
    # =====================================================

    def is_expired(self):

        if self.__expiry_time is None:
            return True

        return datetime.now() > self.__expiry_time

    # =====================================================
    # Verify OTP
    # =====================================================

    def verify_otp(self, entered_otp):

        if self.is_expired():
            ui.error("OTP has expired.")
            return False

        self.__attempts += 1

        if entered_otp == self.__otp:
            return True

        remaining = self.MAX_ATTEMPTS - self.__attempts

        if remaining > 0:
            ui.error(f"Incorrect OTP. Attempts Remaining: {remaining}")
        else:
            ui.error("Maximum attempts exceeded.")

        return False

    # =====================================================
    # Clear OTP
    # =====================================================

    def clear(self):

        self.__otp = None
        self.__email = None
        self.__expiry_time = None
        self.__attempts = 0

    # =====================================================
    # Email Verification
    # =====================================================

    def verify_email(self, email):

        self.__email = email

        otp = self.generate_otp()

        try:
            send_email_otp(email, otp)

        except Exception as e:
            ui.error(f"Unable to send OTP.\n{e}")
            return False

        ui.success("OTP has been sent to your Email successfully.")
        ui.info(f"Email: {email}")
        ui.info(f"OTP expires in {self.OTP_VALIDITY_MINUTES} minutes.")

        while True:

            if self.is_expired():
                ui.error("OTP has expired.")
                self.clear()
                return False

            ui.menu(
                "EMAIL VERIFICATION",
                [
                    ("1", "Enter OTP", "🔢"),
                    ("2", "Resend OTP", "🔁"),
                    ("3", "Cancel", "🚫"),
                ],
                icon="📧",
            )

            choice = ui.prompt("Enter Choice").strip()

            if choice == "1":

                entered = ui.prompt("Enter OTP").strip()

                if self.verify_otp(entered):
                    ui.success("Email Verified Successfully.")
                    self.clear()
                    return True

                if self.__attempts >= self.MAX_ATTEMPTS:
                    self.clear()
                    return False

            elif choice == "2":

                otp = self.generate_otp()


                try:
                    send_email_otp(email, otp)
                    ui.success("A new OTP has been sent.")

                except Exception as e:
                    ui.error(f"Unable to resend OTP.\n{e}")
                    return False

            elif choice == "3":

                ui.warning("Verification Cancelled.")
                self.clear()
                return False

            else:

                ui.warning("Invalid Choice.")
