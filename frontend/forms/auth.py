# accounts/forms.py
import re

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["phone"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        # Remove any spaces or dashes
        phone = phone.replace(" ", "").replace("-", "")

        # Bangladeshi phone number regex: starts with 01 and 11 digits total
        if not re.fullmatch(r"01\d{9}", phone):
            raise ValidationError(
                "Enter a valid Bangladeshi phone number (e.g., 017XXXXXXXX)."
            )

        # Optional: check if phone already exists
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("This phone number is already registered.")

        return phone

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email_or_phone = forms.CharField(label="Email or Phone")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
