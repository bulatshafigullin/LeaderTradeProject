from users.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        # The magic line
        if User.objects.count() == 0:
            User.objects.create_admin(phone_number="+79221110500", password="12345")
            print("Admin created")
