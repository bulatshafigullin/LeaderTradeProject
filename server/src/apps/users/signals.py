from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from src.apps.profiles.models import Profile
from users.models import Verification

User = get_user_model()


@receiver(post_save, sender=User)
def create_verification_signal(sender, instance: User, created: bool, **kwargs) -> None:
    if created:
        verification = Verification.objects.create(user=instance)
        verification.generate_token()
