from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from src.apps.profiles.models import Profile, LegalCard

User = get_user_model()


@receiver(post_save, sender=Profile)
def create_legal_card_signal(
    sender, instance: Profile, created: bool, **kwargs
) -> None:
    legal_card = LegalCard.objects.filter(profile=instance).first()
    if instance.is_legal and legal_card is None:
        LegalCard.objects.create(profile=instance)
