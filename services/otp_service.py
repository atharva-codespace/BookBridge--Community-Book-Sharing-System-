"""
services/otp_service.py

Handles Email OTP generation, sending,
verification, expiry timer and resend OTP.
"""

import random
from datetime import datetime, timedelta

from utils.email_sender import send_email_otp


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
            print("\nOTP has expired.")
            return False

        self.__attempts += 1

        if entered_otp == self.__otp:
            return True

        remaining = self.MAX_ATTEMPTS - self.__attempts

        if remaining > 0:
            print(f"\nIncorrect OTP.")
            print(f"Attempts Remaining : {remaining}")
        else:
            print("\nMaximum attempts exceeded.")

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
            print(f"\nUnable to send OTP.\n{e}")
            return False

        print("\nOTP has been sent to your Email successfully.")
        print(f"Email : {email}")
        print(f"OTP expires in {self.OTP_VALIDITY_MINUTES} minutes.")

        while True:

            if self.is_expired():
                print("\nOTP has expired.")
                self.clear()
                return False

            print("\n========== EMAIL VERIFICATION ==========")
            print("1. Enter OTP")
            print("2. Resend OTP")
            print("3. Cancel")

            choice = input("Enter Choice : ").strip()

            if choice == "1":

                entered = input("Enter OTP : ").strip()

                if self.verify_otp(entered):
                    print("\nEmail Verified Successfully.\n")
                    self.clear()
                    return True

                if self.__attempts >= self.MAX_ATTEMPTS:
                    self.clear()
                    return False

            elif choice == "2":

                otp = self.generate_otp()


                try:
                    send_email_otp(email, otp)
                    print("\nA new OTP has been sent.")

                except Exception as e:
                    print(f"\nUnable to resend OTP.\n{e}")
                    return False

            elif choice == "3":

                print("\nVerification Cancelled.")
                self.clear()
                return False

            else:

                print("\nInvalid Choice.")