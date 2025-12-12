import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

User = get_user_model()


class UserCreationForm(BaseUserCreationForm):
    """Form for creating new users in admin"""

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Groups",
        help_text="Select groups for this user",
    )

    class Meta:
        model = User
        fields = (
            "email",
            "phone",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
        )
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "vTextField", "placeholder": "user@example.com"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "vTextField", "placeholder": "+8801712345678"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make password fields required
        self.fields["password1"].required = True
        self.fields["password2"].required = True

        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if hasattr(field, "widget") and hasattr(field.widget, "attrs"):
                field.widget.attrs.update({"class": "form-control"})

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")

        # At least one of email or phone must be provided
        if not email and not phone:
            raise ValidationError(
                {
                    "email": "Either email or phone must be provided.",
                    "phone": "Either email or phone must be provided.",
                }
            )

        # Validate phone format if provided
        if phone:
            # Remove all non-digit characters
            phone_digits = re.sub(r"\D", "", phone)
            if len(phone_digits) < 10:
                raise ValidationError(
                    {"phone": "Phone number must be at least 10 digits."}
                )
            cleaned_data["phone"] = phone_digits

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()
            # Save groups (many-to-many)
            self.save_m2m()

        return user


class UserChangeForm(BaseUserChangeForm):
    """Form for updating existing users in admin"""

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Groups",
    )

    password = forms.CharField(
        label="Password",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Leave blank to keep current password",
            }
        ),
        help_text="Raw passwords are not stored, so there is no way to see \
            this user's password.",
    )

    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add help text for social fields
        self.fields["facebook_id"].help_text = "Facebook User ID (from social login)"
        self.fields["google_id"].help_text = "Google User ID (from social login)"
        self.fields["github_id"].help_text = "GitHub User ID (from social login)"

        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if hasattr(field, "widget") and hasattr(field.widget, "attrs"):
                if "class" not in field.widget.attrs:
                    field.widget.attrs["class"] = "form-control"

        # Make certain fields readonly for non-superusers
        if not self.instance.is_superuser:
            self.fields["is_superuser"].disabled = True
            self.fields["is_superuser"].help_text = "Only superusers can change this"

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            # Remove all non-digit characters
            phone_digits = re.sub(r"\D", "", phone)
            if len(phone_digits) < 10:
                raise ValidationError("Phone number must be at least 10 digits.")
            return phone_digits
        return phone

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            # Check if email is unique (excluding current user)
            qs = User.objects.filter(email=email)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")

        # Ensure at least one identifier exists
        if not email and not phone:
            if self.instance.email or self.instance.phone:
                # Keep existing if both cleared
                if self.instance.email:
                    cleaned_data["email"] = self.instance.email
                if self.instance.phone:
                    cleaned_data["phone"] = self.instance.phone
            else:
                raise ValidationError(
                    {
                        "email": "Either email or phone must be provided.",
                        "phone": "Either email or phone must be provided.",
                    }
                )

        return cleaned_data


# Additional forms for frontend
class EmailPhoneAuthenticationForm(forms.Form):
    """Form for email/phone authentication"""

    identifier = forms.CharField(
        label="Email or Phone",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter email or phone number",
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter password"}
        )
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def clean_identifier(self):
        identifier = self.cleaned_data.get("identifier")

        # Normalize phone numbers
        if identifier and "@" not in identifier:
            # Remove all non-digit characters for phone
            identifier = re.sub(r"\D", "", identifier)

        return identifier


class UserRegistrationForm(forms.ModelForm):
    """Form for user registration on frontend"""

    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ("email", "phone", "first_name", "last_name")
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")

        if not email and not phone:
            raise ValidationError("Please provide either email or phone number.")

        return cleaned_data

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user


class ProfileUpdateForm(forms.ModelForm):
    """Form for users to update their profile"""

    class Meta:
        model = User
        fields = ("email", "phone", "first_name", "last_name", "bio", "profile_picture")
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Tell us about yourself...",
                }
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            phone_digits = re.sub(r"\D", "", phone)
            if len(phone_digits) < 10:
                raise ValidationError("Phone number must be at least 10 digits.")
            return phone_digits
        return phone


class PasswordChangeCustomForm(forms.Form):
    """Form for changing password"""

    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise ValidationError("Your current password was entered incorrectly.")
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn't match.")

        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data["new_password1"])
        if commit:
            self.user.save()
        return self.user


# Admin-specific forms
class BulkUserImportForm(forms.Form):
    """Form for bulk importing users in admin"""

    csv_file = forms.FileField(
        label="CSV File",
        help_text="Upload CSV file with columns: email,phone,first_name,\
            last_name,groups",
    )
    send_welcome_email = forms.BooleanField(
        required=False, initial=True, label="Send welcome email to new users"
    )

    class Meta:
        fields = ("csv_file", "send_welcome_email")


class GroupAssignmentForm(forms.Form):
    """Form for assigning users to groups in bulk"""

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-control", "size": "10"}),
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple, required=True
    )
    action = forms.ChoiceField(
        choices=[
            ("add", "Add to selected groups"),
            ("remove", "Remove from selected groups"),
            ("replace", "Replace all groups with selected"),
        ],
        initial="add",
        widget=forms.RadioSelect,
    )
