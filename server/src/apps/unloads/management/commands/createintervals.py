from django.core.management import BaseCommand
from django_celery_beat.models import IntervalSchedule


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        # The magic line
        IntervalSchedule.objects.get_or_create(every=1, period="minutes")
        IntervalSchedule.objects.get_or_create(every=5, period="minutes")
        IntervalSchedule.objects.get_or_create(every=30, period="minutes")
        IntervalSchedule.objects.get_or_create(every=1, period="hours")
        IntervalSchedule.objects.get_or_create(every=5, period="hours")
        IntervalSchedule.objects.get_or_create(every=12, period="hours")
        IntervalSchedule.objects.get_or_create(every=1, period="days")
        print("Time intervals created")
