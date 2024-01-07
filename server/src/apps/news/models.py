from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import StreamField
from products.models import Product
from wagtail.images.blocks import ImageChooserBlock
from django import forms
from wagtail.models import Page, Orderable
from modelcluster.fields import ParentalKey

from django.utils.translation import gettext_lazy as _

from src.apps.base.models import TimeStampedMixin, PKIDMixin
from src.utils.slug_utils import slugify


class Post(TimeStampedMixin, Page):
    pic = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Обложка"),
        related_name="+",
    )
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title", label="Заголовок")),
            ("paragraph", blocks.RichTextBlock(label="Текст")),
            ("image", ImageChooserBlock(label="Изображение")),
            (
                "gallery",
                blocks.ListBlock(ImageChooserBlock(label="Фото"), label="Галерея фото"),
            ),
        ],
        use_json_field=True,
        verbose_name=_("Контент"),
    )
    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("pic"),
        FieldPanel("body"),
        InlinePanel('products', heading="Товары в новости", label="Товар"),
    ]
    date = models.DateTimeField("Дата новости")

    class Meta:
        verbose_name = _("Публикация")
        verbose_name_plural = _("Публикации")

    def save(self, *args, **kwargs) -> None:
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.id)


class PostProduct(Orderable):
    page = ParentalKey(Post, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name='ИД Товара')

    panels = [
        FieldPanel('product', widget=forms.TextInput()),
    ]