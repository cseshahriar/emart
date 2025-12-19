import re

from allauth.account.adapter import DefaultAccountAdapter
from django.core.exceptions import ValidationError


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.phone = form.cleaned_data.get("phone")
        if commit:
            user.save()
        return user

    def clean_username(self, username, shallow=False):
        return None  # disable username

    def clean_email(self, email):
        return None  # disable email requirement

    def clean_phone_number(self, phone):
        """
        Validate BD phone number:
        - Must be 11 digits
        - Can start with +8801 or 01
        """
        if not phone:
            raise ValidationError("Phone number is required")

        # Normalize +880
        if phone.startswith("0"):
            phone = "+880" + phone[1:]

        pattern = r"^\+8801\d{9}$"
        if not re.match(pattern, phone):
            raise ValidationError("Enter a valid Bangladeshi phone number")
        return phone
