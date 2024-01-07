from datetime import date, datetime
from markupsafe import Markup
import jinja2
from django.templatetags.static import static
from django.urls import reverse
from django.db.models import Sum
from django.template.defaultfilters import date as date_filter, stringformat, linebreaks
from django.contrib.humanize.templatetags.humanize import naturaltime, intcomma
from django.templatetags.tz import localtime
from django.utils import timezone
from cache_memoize import cache_memoize
from products.models import Product
from .jinja_ext import CacheExtension

from jinja2 import Environment


def phone_format(val):
    try:
        val = str(val)
        return f"{val[0]} ({val[1:4]}) {val[4:7]}-{val[7:]}"
    except:
        return str(val)


@jinja2.pass_context
def get_unicorn(ctx, component_name, request=None, **kwargs):
    return Markup(UnicornNode(component_name, kwargs).render(ctx))


def endswith(st, v):
    if st and st.endswith(v):
        return True


@jinja2.pass_context
def get_most_viewed_products(ctx):
    return Product.objects.all().order_by("-views")[:10]


@jinja2.pass_context
def get_recent_promo(ctx):
    from promo.models import Promo
    return Promo.objects.order_by("-start")[:6]


def remp(s):
    return s.replace("<p>", "").replace("</p>", "")


def remq(s):
    return s.replace('"', "")


@cache_memoize(60 * 60)
def all_time_total():
    return Donat.objects.exclude(paid_at=None).aggregate(s=Sum("amount"))["s"] or 0


@cache_memoize(60 * 60)
def this_year_total():
    this_year = get_this_year()
    return (
        Donat.objects.filter(
            paid_at__range=[date(this_year, 1, 1), date(this_year + 1, 1, 1)]
        ).aggregate(s=Sum("amount"))["s"]
        or 0
    )


@cache_memoize(60)
def get_shop():
    from locations.models import Shop

    try:
        obj = Shop.objects.first()
        return obj
    except:
        return Shop()


import re

pre = re.compile(r"<.*?>")


def remtags(s):
    return pre.sub("", s)


@jinja2.pass_context
def spark(ctx, name):
    from web.ts_urls import send_msg
    from django.utils.safestring import mark_safe

    return mark_safe(send_msg(ctx["request"], name))


def environment(**options):
    env = Environment(**options)
    env.add_extension(CacheExtension)
    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "now": timezone.now,
            "today": date.today,
            "str": str,
            "spark": spark,
            "get_most_viewed_products": get_most_viewed_products,
            "get_recent_promo": get_recent_promo,
            "get_shop": get_shop
        }
    )
    env.filters.update(
        {
            "date": date_filter,
            "stringformat": stringformat,
            "linebreaks": linebreaks,
            "endswith": endswith,
            "asphone": phone_format,
            "localtime": localtime,
            "naturaltime": naturaltime,
            "intcomma": intcomma,
            "remp": remp,
            "remtags": remtags,
            "remq": remq,
        }
    )
    return env
