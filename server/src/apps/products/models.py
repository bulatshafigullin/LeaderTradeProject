from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_enum_choices.fields import EnumChoiceField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from src.apps.base.models import PKIDMixin, TimeStampedMixin
from catalog.models import Brand
from src.apps.profiles.models import Profile
from src.other.enums import ProductType, RimType, UnloadServiceType
from src.utils.slug_utils import slugify


# Tree model
class Category(PKIDMixin, MPTTModel):
    title = models.CharField(max_length=255, verbose_name=_("Название"))
    slug = models.SlugField(
        max_length=250, null=True, blank=True, unique=True, verbose_name=_("URL путь")
    )
    parent = TreeForeignKey(
        to="self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Родитель"),
    )

    class MPTTMeta:
        order_insertion_by = ["title"]

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")

    def save(self, *args, **kwargs) -> None:
        # if not self.pk:
        self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title}"


class Product(PKIDMixin, TimeStampedMixin):
    category = models.ForeignKey(
        to=Category,
        related_name="products",
        on_delete=models.CASCADE,
        verbose_name=_("Категория"),
    )
    title = models.CharField(max_length=255, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    slug = models.SlugField(
        max_length=250,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        verbose_name=_("URL путь"),
    )
    # tire
    season = models.CharField("Сезонность", max_length=255, blank=True)
    spikes = models.BooleanField("Шипы", default=False)
    height = models.IntegerField("Высота", blank=True, null=True, default=0)
    diameter = models.IntegerField("Диаметр (размер)", blank=True, null=True, default=0)
    suv = models.BooleanField(default=False)
    load_index = models.CharField(
        "Индекс нагрузки", max_length=255, blank=True, null=True, default="-"
    )
    speed_index = models.CharField(
        "Индекс скорости", max_length=255, blank=True, null=True, default="-"
    )
    runflat = models.BooleanField("Run Flat", default=False)
    # rim
    type = EnumChoiceField(
        ProductType, default=ProductType.RIMS, verbose_name=_("Тип товара")
    )
    rim_type = models.CharField(
        choices=RimType.choices, default=RimType.ALLOY, 
        max_length=1,
        null=True, blank=True, verbose_name=_("Тип дисков")
    )
    color = models.CharField(
        max_length=100, verbose_name=_("Цвет"), blank=True, null=True
    )
    size = models.SmallIntegerField(
        verbose_name=_("Диаметр (размер)"), blank=True, null=True
    )
    et = models.IntegerField(verbose_name=_("Вылет ET"), blank=True, null=True)
    width = models.FloatField(
        verbose_name=_("Ширина обода"), blank=False, null=True, default=0
    )
    width2 = models.FloatField(
        verbose_name=_("Ширина обода 2"), blank=False, null=True, default=0
    )
    et2 = models.IntegerField(
        verbose_name=_("Вылет ET 2"), blank=False, null=False, default=0
    )
    dia = models.FloatField(
        verbose_name=_("Диаметр центр. отверстия, DIA"),
        blank=True,
        null=True,
        default=0,
    )
    pcd = models.FloatField(
        verbose_name=_("Сверловка, PCD"), blank=True, null=True, default=0
    )
    bolts = models.SmallIntegerField(
        verbose_name=_("Количество болтов"), blank=True, null=True, default=0
    )
    pcd2 = models.FloatField(
        verbose_name=_("Сверловка, PCD 2"), blank=True, null=True, default=0
    )
    bolts2 = models.SmallIntegerField(
        verbose_name=_("Количество болтов 2"), blank=True, null=True, default=0
    )
    unite_pcd = models.CharField(
        verbose_name=_("Сверловка, PCD"), max_length=255, blank=True, null=True
    )
    # general
    model = models.CharField(
        verbose_name=_("Модель"), max_length=255, blank=True, null=True
    )
    brand = models.ForeignKey(
        to=Brand,
        verbose_name="Производитель",
        related_name="products",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    current_price = models.DecimalField(
        max_digits=12,
        decimal_places=5,
        verbose_name=_("Текущая Стоимость"),
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=5,
        verbose_name=_("Стоимость"),
        null=True,
        blank=True,
    )
    discount = models.DecimalField(
        max_digits=12,
        decimal_places=5,
        verbose_name=_("Скидка"),
        blank=True,
        default=0,
    )
    bar_code = models.IntegerField(
        verbose_name=_("Код(Артикул)"), blank=True, null=True
    )
    views = models.IntegerField(default=0, verbose_name=_("Просмотры"))
    buyed = models.IntegerField(default=0, verbose_name=_("Покупки"))
    image = models.ImageField(
        upload_to="products/", blank=True, null=True, verbose_name=_("Изображение"),
        max_length=255
    )
    rest = models.IntegerField(default=0, verbose_name=_("Остаток"))
    ext_data = models.JSONField(
        blank=True, null=True, verbose_name=_("Дополнительная информация")
    )
    unload_service = EnumChoiceField(UnloadServiceType, null=True, blank=True)

    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")

    def add_view(self) -> None:
        self.views += 1
        self.save(update_fields=['views'])

    def add_to_json(self, key: str, value: Any) -> None:
        pass

    def save(self, *args, **kwargs) -> None:
        if not self.pk_id:
            self.image.upload_to = f"products/{self.pk_id}/"
            # update slug
            self.slug = slugify(self.title)
        # update current_price
        if self.price is not None:
            self.current_price = float(self.price) - float(self.discount)
        super(Product, self).save(*args, **kwargs)

    @property
    def external_id(self) -> str | None:
        ext_id = self.ext_data.get("code", None)
        if ext_id is None:
            return self.ext_data.get("product_no", None)

    def __str__(self) -> str:
        return f"{self.title}"


class ProductImage(PKIDMixin):
    product = models.ForeignKey(
        Product,
        related_name="album",
        on_delete=models.CASCADE,
        verbose_name=_("Товар"),
    )
    image = models.ImageField(
        upload_to="products/", blank=True, null=True, verbose_name=_("Изображение")
    )

    def save(self, *args, **kwargs) -> None:
        self.image.upload_to = f"products/{self.product.pk_id}/"
        super(ProductImage, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Изображение Товара")
        verbose_name_plural = _("Изображения Товара")
