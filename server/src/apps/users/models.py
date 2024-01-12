from datetime import timedelta, datetime

from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from src.apps.base.models import TimeStampedMixin, PKIDMixin, Settings
from users.managers import UserManager
from src.utils.sms_utils import generate_verification_code


class User(AbstractBaseUser, PermissionsMixin, TimeStampedMixin):
    id = models.BigAutoField(primary_key=True, editable=False, verbose_name=_("ID"))
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        unique=True,
        verbose_name=_("Номер телефона"),
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = UserManager()
    USERNAME_FIELD = "phone_number"

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self) -> str:
        return f"{self.phone_number}"


class Verification(PKIDMixin, TimeStampedMixin):
    user = models.OneToOneField(
        verbose_name=_("Пользователь"),
        to=User,
        related_name="verification",
        on_delete=models.CASCADE,
    )
    token = models.IntegerField(verbose_name=_("Токен"), null=True, blank=True)
    expire_date = models.DateTimeField(
        verbose_name=_("Дата истечения"), null=True, blank=True
    )
    attempt_count = models.IntegerField(default=0, verbose_name=_("Количество попыток"))

    class Meta:
        verbose_name = _("Верификация")
        verbose_name_plural = _("Верификации")

    def _is_expired(self) -> bool:
        if self.expire_date is None:
            return False
        current_datetime = timezone.localtime(timezone.now())
        end_time = timezone.localtime(self.expire_date)
        return end_time <= current_datetime

    def _create_expire_date(self) -> datetime:
        current_datetime = timezone.localtime(timezone.now())
        settings = Settings.objects.first()
        period_time = settings.verify_token_generation_period
        return current_datetime + timedelta(minutes=period_time)

    def generate_token(self) -> int:
        settings = Settings.objects.first()
        if self.attempt_count > settings.verify_token_max_count:
            raise Exception("Limit Exception")
        # if token is just created or expired
        if self.token is None or self._is_expired():
            new_expire_date = self._create_expire_date()
            self.expire_date = new_expire_date
            self.attempt_count = 1
            self.token = generate_verification_code()
        self.save()
        return self.token
