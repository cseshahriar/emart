# users/backends.py
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class EmailOrPhoneBackend(BaseBackend):
    """
    Authenticate using email or phone number.
    """

    def authenticate(
        self, request, email_or_phone=None, password=None, **kwargs
    ):
        user = None
        if email_or_phone is None or password is None:
            return None

        # Check email
        if "@" in email_or_phone:
            try:
                user = User.objects.get(email=email_or_phone)
            except User.DoesNotExist:
                return None
        else:
            # Check phone
            try:
                user = User.objects.get(phone=email_or_phone)
            except User.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def user_can_authenticate(self, user):
        return getattr(user, "is_active", False)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
