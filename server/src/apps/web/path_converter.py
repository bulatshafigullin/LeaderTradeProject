import re
from django.http import Http404
from django.shortcuts import get_object_or_404
from src.other.enums import TireSeason, ProductType
from catalog.models import Brand
from products.models import (
    Product
)
from web.util import fmt_float
from cache_memoize import cache_memoize


class RimRadiusConverter:
    regex = "r([0-9]+)"
    filter_name = "size"

    def to_python(self, value):
        return int(value.replace("r", ""))

    def to_url(self, value):
        return "r" + str(value)

    def humanize(self, value):
        return "R" + str(value)

    def to_bc(self, args):
        """
        Display value in breadcrumbs
        """
        res = "Диски"
        if args.get("brands"):
            res = "Диски " + fmt_active_params(Rim, {"brands": args.get("brands")})
        elif args.get("type"):
            if args.get("type") in [RimType.alloy, RimType.flow_forming]:
                res = "Литые диски"
            elif args.get("type") in [RimType.forged]:
                res = "Кованые диски"

        return res + " R" + str(args["size"])


# @cache_memoize(60)
def get_brand_slugs():
    res = {}
    brands = Brand.objects.exclude(slug=None)
    rim_brands = set(
        Product.objects.filter(type=ProductType.RIMS).exclude(brand_id=None)
        .values("brand_id")
        .order_by()
        .distinct()
        .values_list("brand_id", flat=True)
    )
    tire_brands = set(
        Product.objects.filter(type=ProductType.TIRES).exclude(brand_id=None)
        .values("brand_id")
        .order_by()
        .distinct()
        .values_list("brand_id", flat=True)
    )
    for brand in brands:
        brand.url = None
        if brand.pk in rim_brands:
            brand.url = "diski"
        elif brand.pk in tire_brands:
            brand.url = "shiny"
        res[brand.slug] = brand
    return res


@cache_memoize(60)
def get_brand_ids():
    return {brand.id: brand.slug for brand in Brand.objects.all()}


class BrandConverter:
    regex = "([\w\-\d]+)"
    filter_name = "brands"

    def to_python(self, value):
        slugs = value.split("-or-")
        brands = get_brand_slugs()
        res = [brands.get(s) for s in slugs]
        if not res or None in res:
            raise ValueError(f"No such brand {res}")
        return [b.pk for b in res]

    def to_url(self, value):
        if isinstance(value, Brand):
            return value.slug
        brands = get_brand_ids()
        brand_slugs = [brands.get(int(v)) for v in value]
        if None in brand_slugs:
            raise Http404
        return "-or-".join(brand_slugs)

    def humanize(self, value):
        brands = Brand.objects.filter(id__in=value).values("name")
        return " ".join([b["name"] for b in brands])

    def to_bc(self, args):
        return "Диски " + fmt_active_params(Rim, {"brands": args["brands"]})


class RimTypeConverter:
    regex = "litye|forged|forged-maket|flow-forming"
    filter_name = "type"

    def to_python(self, value):
        if value == "forged":
            return value
        elif value == "litye":
            return RimType.alloy
        elif value == "forged-maket":
            return "maket"
        elif value == "flow-forming":
            return "flow_forming"

    def to_url(self, value):
        if value == "forged":
            return "forged"
        elif value == "alloy":
            return "litye"
        elif value == "maket":
            return "forged-maket"
        elif value == "flow_forming":
            return "flow-forming"

    def humanize(self, value):
        return RIM_TYPES_PLURAL.get(value)

    def to_bc(self, args):
        res = self.humanize(args["type"])
        brands = args.get("brands")
        if brands:
            return res + " " + fmt_active_params(Rim, {"brands": brands})
        return res


class RimPcdConverter:
    regex = "[0-9]+x[0-9]+\-*[0-9]+"
    filter_name = "unite_pcd"

    def to_python(self, value):
        return value.replace("-", ".")

    def to_url(self, value):
        return value.replace(".", "-")

    def humanize(self, value):
        return str(value)

    def to_bc(self, args):
        res = "Диски "
        if sz := args.get("size"):
            res += f"R{sz} "
        return res + args["unite_pcd"]


class RimWidth2Converter:
    regex = "raznoshirokie|ne-raznoshirokie"
    filter_name = "width2"

    def to_python(self, value):
        if value == "raznoshirokie":
            return "yes"
        if value == "ne-raznoshirokie":
            return "no"

    def to_url(self, value):
        if value == "yes":
            return "raznoshirokie"
        if value == "no":
            return "ne-raznoshirokie"

    def humanize(self, value):
        if value == "yes":
            return "Разноширокие"
        if value == "no":
            return "Не разноширокие"


class DiaConverter:
    regex = "dia([0-9]+\-*[0-9]*)"
    filter_name = "dia"

    def to_python(self, value):
        return float(value.replace("-", ".").replace("dia", ""))

    def to_url(self, value):
        return "dia" + str(value).replace(".", "-")

    def humanize(self, value):
        return "DIA " + str(value)


class RimWidthConverter:
    regex = "[0-9]+\-*[0-9]*j$"
    filter_name = "width"

    def to_python(self, value):
        return value.replace("j", "").replace("-", ".")

    def to_url(self, value):
        return str(value).replace(".", "-") + "j"

    def humanize(self, value):
        return fmt_float(value) + "j"


class RimWidthMaxConverter:
    regex = "[0-9]+\-*[0-9]*jmax$"
    filter_name = "wheels_width_max"

    def to_python(self, value):
        return value.replace("jmax", "").replace("-", ".")

    def to_url(self, value):
        return str(value).replace(".", "-") + "jmax"

    def humanize(self, value):
        return "Макс. ширина " + str(value)


class EtConverter:
    regex = "et\-?[0-9]+"
    filter_name = "et_length__lte"

    def to_python(self, value):
        return value.replace("et", "")

    def to_url(self, value):
        return f"et{value}"

    def humanize(self, value):
        return "Вылет " + str(value)


class EtMaxConverter:
    regex = "et\-max\-?[0-9]+"
    filter_name = "wheels_et_max"

    def to_python(self, value):
        return value.replace("et-max", "")

    def to_url(self, value):
        return f"et-max{value}"

    def humanize(self, value):
        return "Макс вылет " + str(value)


class VatConverter:
    regex = "has_vat"
    filter_name = "has_vat"
    staff_only = True

    def to_python(self, value):
        if value == "has_vat":
            return True
        return False

    def to_url(self, value):
        if value is True:
            return "has_vat"

    def humanize(self, value):
        if value is True:
            return "Только с НДС"


class ImportRuleConverter:
    regex = "imported-from-?[0-9]+"
    filter_name = "imported_from"

    def to_python(self, value):
        return value.replace("imported-from-", "")

    def to_url(self, value):
        return f"imported-from-{value}"

    def humanize(self, value):
        return f"Загружено из {value}"


class EfMaxConverter:
    regex = "ef\-max\-?[0-9]+"
    filter_name = "ef_max"
    staff_only = True

    def to_python(self, value):
        return value.replace("ef-max", "")

    def to_url(self, value):
        return f"ef-max{value}"

    def humanize(self, value):
        return "Эффективность " + str(value)


class EfMinConverter:
    regex = "ef\-min\-?[0-9]+"
    filter_name = "ef_min"
    staff_only = True

    def to_python(self, value):
        return value.replace("ef-min", "")

    def to_url(self, value):
        return f"ef-min{value}"

    def humanize(self, value):
        return "Эффективность " + str(value)


class TireWidthConverter:
    regex = "(\d+)w"
    filter_name = "width"

    def to_python(self, value):
        return value.replace("w", "")

    def to_url(self, value):
        return str(value) + "w"

    def humanize(self, value):
        return "Ширина " + str(value)


class ProfileConverver:
    regex = "profile(\d*)"
    filter_name = "height"

    def to_python(self, value):
        return value.replace("profile", "")

    def to_url(self, value):
        return "profile" + str(value)

    def humanize(self, value):
        return "Профиль " + str(value)


class TireSizeConverver:
    regex = "tyres-r(\d*)"
    filter_name = "diameter"

    def to_python(self, value):
        return value.replace("tyres-r", "")

    def to_url(self, value):
        return f"tyres-r{value}"

    def humanize(self, value):
        return "R" + str(value)


class TireSpikeConverver:
    regex = "shipovannye|neshipovannye"
    filter_name = "spikes"

    def to_python(self, value):
        return value == "shipovannye"

    def to_url(self, value):
        return "shipovannye" if value else "neshipovannye"

    def humanize(self, value):
        if value is True:
            return "шипованые"
        if value is False:
            return "нешипованые"


TireSeasonFromUrls = {
    "zimnie": TireSeason.winter,
    "letnie": TireSeason.summer,
    "vsesezonnye": TireSeason.universal,
}

TireSeasonToUrls = {value: key for key, value in TireSeasonFromUrls.items()}


class TireSeasonConverver:
    regex = "|".join(TireSeasonFromUrls.keys())
    filter_name = "seasonality"

    def to_python(self, value):
        return TireSeasonFromUrls[value]

    def to_url(self, value):
        return TireSeasonToUrls[value]

    def humanize(self, value):
        return SEASONS[value]


TirePathParams = {
    BrandConverter.filter_name: BrandConverter(),
    TireWidthConverter.filter_name: TireWidthConverter(),
    ProfileConverver.filter_name: ProfileConverver(),
    TireSizeConverver.filter_name: TireSizeConverver(),
    TireSpikeConverver.filter_name: TireSpikeConverver(),
    TireSeasonConverver.filter_name: TireSeasonConverver(),
    VatConverter.filter_name: VatConverter(),
    EfMinConverter.filter_name: EfMinConverter(),
    EfMaxConverter.filter_name: EfMaxConverter(),
    ImportRuleConverter.filter_name: ImportRuleConverter(),
}

RimPathParams = {
    BrandConverter.filter_name: BrandConverter(),
    RimTypeConverter.filter_name: RimTypeConverter(),
    RimRadiusConverter.filter_name: RimRadiusConverter(),
    RimPcdConverter.filter_name: RimPcdConverter(),
    DiaConverter.filter_name: DiaConverter(),
    RimWidthConverter.filter_name: RimWidthConverter(),
    EtConverter.filter_name: EtConverter(),
    RimWidth2Converter.filter_name: RimWidth2Converter(),
    RimWidthMaxConverter.filter_name: RimWidthMaxConverter(),
    EtMaxConverter.filter_name: EtMaxConverter(),
    VatConverter.filter_name: VatConverter(),
    EfMinConverter.filter_name: EfMinConverter(),
    EfMaxConverter.filter_name: EfMaxConverter(),
    ImportRuleConverter.filter_name: ImportRuleConverter(),
}

SIMILARITY_PARAMS = {
    ProductType.RIMS: [
        RimRadiusConverter(),
        RimPcdConverter(),
        DiaConverter(),
        RimWidthConverter(),
        EtConverter(),
    ],
    ProductType.TIRES: [
        TireWidthConverter(),
        ProfileConverver(),
        TireSizeConverver(),
        TireSpikeConverver(),
        TireSeasonConverver(),
    ]
}

class PathConverter:
    regex = "([\w\-\d\/]+)"

    def to_python(self, value):
        path_filters = {}
        parts = value.split("/")
        conv_idx = -1
        for part in parts:
            for idx, conv in enumerate(self.path_params.values()):
                if conv in path_filters or idx <= conv_idx:
                    continue
                m = re.match(conv.regex, part)
                if not m:
                    continue
                try:
                    v = conv.to_python(part)
                    path_filters[conv] = v
                    conv_idx = idx
                    break
                except ValueError:
                    continue

        if len(parts) != len(path_filters):
            raise ValueError
        return path_filters

    def to_url(self, value):
        return ""


class TirePathConverter(PathConverter):
    path_params = TirePathParams
    filter_name = "tire_pathfilter"


class RimPathConverter(PathConverter):
    path_params = RimPathParams
    filter_name = "rim_pathfilter"


def fmt_active_params(model, params):
    alist = []
    fields = {f.name: f.verbose_name for f in model._meta.fields}

    if model == Tire and params.get("seasonality"):
        season = TirePathParams["seasonality"].humanize(params.get("seasonality"))
        alist.append(season)
        params.pop("seasonality", None)

    if brand_id := params.get("brands"):
        if isinstance(brand_id, list):
            brands = Brand.objects.filter(id__in=brand_id).values_list("name", flat=True)
            alist.append(", ".join(brands))
        else:
            brand = get_object_or_404(Brand, id=brand_id)
            alist.append(brand.name)

    tire_fields = ["spikes", "diameter", "width", "height"]
    if model == Tire:
        if params.get("width") and params.get("height"):
            alist.append(str(params["width"]) + "/" + str(params["height"]))
            del fields["width"]
            del fields["height"]
            tire_fields.remove("width")
            tire_fields.remove("height")

        for field in tire_fields:
            if params.get(field) is not None:
                alist.append(TirePathParams[field].humanize(params.get(field)))
                try:
                    fields.pop(field)
                except Exception as e:
                    pass

    if model == Rim:
        params.pop("type", None)
        for field in ["size", "unite_pcd", "dia", "width", "et_length__lte"]:
            if params.get(field):
                alist.append(RimPathParams[field].humanize(params.get(field)))
                try:
                    fields.pop(field)
                except Exception as e:
                    pass
        if wide := params.get("width2"):
            alist.append("Разноширокие")
            fields.pop("width2")
    for name, val in params.items():
        title = fields.get(name)
        if title and val:
            alist.append(title + " " + str(val))
    s = " ".join(alist)
    return s
