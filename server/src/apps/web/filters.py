import django_filters

from cache_memoize import cache_memoize
from django.db import models
from django.db.models import Q
from django.db.models import Q, Value as V
from src.other.enums import RimType
from django.db.models.functions import Concat, Cast, Floor, Coalesce
from django.db.models import FloatField
from catalog.models import Brand
from products.models import Product


from django.forms.fields import MultipleChoiceField, IntegerField


class MultipleValueField(MultipleChoiceField):
    def __init__(self, *args, field_class, **kwargs):
        self.inner_field = field_class()
        super().__init__(*args, **kwargs)

    def valid_value(self, value):
        return self.inner_field.validate(value)

    def clean(self, values):
        return values and [self.inner_field.clean(value) for value in values]


class MultipleValueFilter(django_filters.Filter):
    field_class = MultipleValueField
    required = False

    def __init__(self, *args, field_class, **kwargs):
        kwargs.setdefault("lookup_expr", "in")
        super().__init__(*args, field_class=field_class, **kwargs)


def tire_brand_filter(queryset, name, value):
    return queryset.filter(brand__slug__in=value)


def imported_from_filter(queryset, _, value):
    return queryset.filter(imported_from__contains=[value])


class TireFilter(django_filters.FilterSet):
    brands = MultipleValueFilter(field_class=IntegerField, required=False, field_name="brand")

    class Meta:
        model = Product
        fields = {
            "spikes": ["exact"],
            "width": ["exact"],
            "height": ["exact"],
            "diameter": ["exact"],
            "load_index": ["exact"],
            "speed_index": ["exact"],
            "runflat": ["exact"],
        }


def pcd_filter(queryset, name, value):
    bolts, pcd = value.split("x")
    return queryset.filter(Q(bolts=bolts, pcd=pcd) | Q(bolts2=bolts, pcd2=pcd))


def width_filter(queryset, name, value):
    return queryset.filter(Q(width__gte=value) | Q(width2__gte=value))


def width2_filter(queryset, name, value):
    if value == "yes":
        return queryset.filter(width2__gte=1)
    if value == "no":
        return queryset.filter(width2=0)
    return queryset


def rim_type_filter(queryset, name, value):
    return queryset.filter(rim_type=RimType[value.upper()])


@cache_memoize(3 * 60)
def rule_ids_with_vat_available():
    return list(
        ImportProductsRule.objects.filter(active=True, is_vat_available=True).values_list(
            "id", flat=True
        )
    )


class RimFilter(django_filters.FilterSet):
    size = django_filters.NumberFilter(field_name="size")
    dia = django_filters.NumberFilter(lookup_expr="gte")
    dia_min = django_filters.NumberFilter(field_name="dia", lookup_expr="gte")
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    width2 = django_filters.CharFilter(field_name="width2", method=width2_filter)
    width = django_filters.NumberFilter(field_name="width", method=width_filter)
    wheels_width_max = django_filters.NumberFilter(lookup_expr="lte", field_name="width")
    wheels_et_max = django_filters.NumberFilter(lookup_expr="lte", field_name="et_length")
    et_length__lte = django_filters.NumberFilter(lookup_expr="gte", field_name="et_length")
    unite_pcd = django_filters.CharFilter(field_name="unite_pcd", method=pcd_filter)
    brands = MultipleValueFilter(field_class=IntegerField, required=False, field_name="brand")
    rim_type = django_filters.CharFilter(field_name="type", method=rim_type_filter)


    class Meta:
        model = Product
        fields = {
            "size": ["exact"],
            "width": ["gte", "lte"],
            "pcd": ["exact"],
            "bolts": ["exact"],
            "unite_pcd": ["exact"],
        }


class AccessoryFilter(django_filters.FilterSet):
    brand = django_filters.NumberFilter(field_name="brand_id")
    imported_from = django_filters.NumberFilter(method=imported_from_filter)

    class Meta:
        model = Product
        fields = {"brand": ["exact"]}


@cache_memoize(60)
def collect_pcd_options(qs, size=None):
    pcd1 = (
        qs.exclude(Q(bolts=0) | Q(pcd=0))
        .values("bolts", "pcd")
        .order_by("bolts", "pcd")
        .distinct()
        .annotate(
            x=Concat(
                Cast("bolts", output_field=models.CharField()),
                V("x"),
                Cast("pcd", output_field=models.CharField()),
            )
        )
        .values_list("x", flat=True)
    )
    pcd2 = (
        qs.exclude(Q(bolts2=0) | Q(pcd2=0))
        .values("bolts2", "pcd2")
        .order_by("bolts2", "pcd2")
        .distinct()
        .annotate(
            x=Concat(
                Cast("bolts2", output_field=models.CharField()),
                V("x"),
                Cast("pcd2", output_field=models.CharField()),
            )
        )
        .values_list("x", flat=True)
    )
    data = sorted(set(pcd1).union(set(pcd2)), key=lambda x: tuple(map(float, x.split("x"))))
    return data
