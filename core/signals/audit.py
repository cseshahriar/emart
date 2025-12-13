# core/signals/audit.py
from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.middleware.current_user import get_current_user
from core.models.base import BaseModel


@receiver(pre_save)
def set_audit_fields(sender, instance, **kwargs):
    if not issubclass(sender, BaseModel):
        return

    user = get_current_user()
    if user and user.is_authenticated:
        if not instance.pk:
            instance.created_by = user
        instance.updated_by = user
