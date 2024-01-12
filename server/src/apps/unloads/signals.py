from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from unloads.models import UnloadScheduler
from src.other.enums import TaskStatus