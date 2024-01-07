from django.db import models
from django.utils.translation import gettext_lazy as _

from src.apps.base.models import PKIDMixin, TimeStampedMixin


class Brand(PKIDMixin, TimeStampedMixin):
    title = models.CharField(max_length=100, verbose_name=_("Название"))
    slug = models.SlugField(max_length=150, null=True, blank=True)
    description = models.TextField(blank=True, verbose_name=_("Описание"))

    class Meta:
        verbose_name = _("Брэнд товара")
        verbose_name_plural = _("Брэнды Товаров")

    def __str__(self) -> str:
        return f"{self.title}"


class Make(PKIDMixin):
    title = models.CharField(max_length=100, verbose_name=_("Название"))

    class Meta:
        verbose_name = _("Марка")
        verbose_name_plural = _("Марки")

    def __str__(self) -> str:
        return f"{self.title}"


class Model(PKIDMixin):
    make = models.ForeignKey(
        to=Make,
        related_name="models",
        on_delete=models.CASCADE,
        verbose_name=_("Марка"),
    )
    title = models.CharField(max_length=100, verbose_name=_("Название"))
    year = models.IntegerField(blank=True, null=True, verbose_name=_("Год"))

    class Meta:
        verbose_name = _("Модель")
        verbose_name_plural = _("Модели")

    def __str__(self) -> str:
        return f"{self.title}"
