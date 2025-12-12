import re

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class EmailPhoneBackend(ModelBackend):
    """
    Authenticate using either email or phone number
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        # Check if input is email or phone
        if "@" in username:
            # Email authentication
            kwargs = {"email": username}
        else:
            # Phone authentication (remove non-digits)
            phone = re.sub(r"\D", "", username)
            kwargs = {"phone": phone}

        try:
            user = UserModel.objects.get(**kwargs)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce timing difference
            UserModel().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
