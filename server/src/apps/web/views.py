import json
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Min, Max, F, Count
from catalog.models import Brand
from src.other.enums import RimType
from products.models import Product, ProductType
from web.filters import RimFilter
from web.util import combined_qdict, in_spark, make_similar_url, digits


PAGE_SIZE = 20


def home(r):
    recommend = Product.objects.filter(
        rest__gt=0, created_at__gte=datetime.now() - timedelta(days=20)
    )[:12]
    popular_tires = Product.objects.filter(rest__gt=0, type=ProductType.TIRES).order_by(
        "-views"
    )[:12]
    popular_rims = Product.objects.filter(rest__gt=0, type=ProductType.RIMS).order_by(
        "-views"
    )[:12]
    most_buyed = Product.objects.filter(rest__gt=0).order_by("-buyed")[:12]
    return render(r, "index.html", locals())


def catalog(r, slug=None, pathfilter={}, title=None):
    products = Product.objects.exclude(rest__lt=1).order_by("pk")
    try:
        ptype = ProductType[slug.upper()]
    except KeyError:
        ptype = None
    if ptype:
        products = products.filter(type=ptype)
    else:
        if slug == "sale":
            products = products.filter(current_price__lt=F("price"))
        else:
            products = Product.objects.none()
    decl_product_types = {}
    if slug == "rims":
        decl_product_types = {
            t.name.lower(): {
                "title": t.label,
                "slug": t.name.lower(),
                "count": products.filter(rim_type=t).count(),
            }
            for t in RimType
        }
    decl_filter_of_types = {}
    if slug == "rims":
        decl_filter_of_types = {
            "size": {
                "title": "Диаметр (D)",
                "type": "single",
                "vals": [
                    {"title": "R" + str(b["size"]), "id": b["size"]}
                    for b in products.values("size")
                    .exclude(size=None)
                    .order_by()
                    .distinct()
                ],
            },
            "unite_pcd": {
                "title": "Разболтовка",
                "type": "single",
                "vals": [
                    {"title": str(b["unite_pcd"]), "id": b["unite_pcd"]}
                    for b in products.values("unite_pcd").order_by().distinct()
                ],
            },
            "et": {
                "title": "Вылет (ET)",
                "type": "single",
                "vals": [
                    {"title": str(b["et"]), "id": b["et"]}
                    for b in products.values("et").order_by().distinct()
                ],
            },
        }

    path_dict = {}
    if pathfilter:
        for conv, v in pathfilter.items():
            path_dict[conv.filter_name] = v

    qd = combined_qdict(r, path_dict)
    filterset = RimFilter(qd, request=r, queryset=products)
    if filterset.form.is_valid():
        products = filterset.qs

    price_agg = products.aggregate(min_price=Min("price"), max_price=Max("price"))
    brands_in_products = {
        q["brand_id"]: q["c"]
        for q in products.values("brand_id").order_by().annotate(c=Count("pk"))
    }
    decl_filter_common = {
        "price": {
            "title": "Цена",
            "type": "range",
            "vals": [
                int(price_agg["min_price"] or 0),
                int(price_agg["max_price"] or 0) + 1,
            ],
        },
        "brands": {
            "title": "Производитель",
            "type": "checkbox",
            "vals": [
                {"title": b.title, "id": b.pk, "count": brands_in_products[b.pk]}
                for b in Brand.objects.filter(pk__in=brands_in_products.keys()).order_by('title')
            ],
        },
    }

    pages = Paginator(products, PAGE_SIZE)
    page = pages.get_page(int(r.GET.get("page", 1)))
    if ts := in_spark(r):
        return render(r, "spark/catalog.html", locals())
    return render(r, "catalog.html", locals())


def search(r):
    return render(r, "search.html", locals())


def promo(r):
    return render(r, "promo.html", locals())


def about(r):
    return render(r, "about.html", locals())


def news(r):
    from news.models import Post

    posts = Post.objects.filter(live=True).order_by("-date")
    pages = Paginator(posts, PAGE_SIZE)
    page = pages.get_page(int(r.GET.get("page", 1)))
    return render(r, "news.html", locals())


def news_item(r, slug):
    from news.models import Post

    post = Post.objects.get(slug=slug, live=True)
    post_products = [pp.product for pp in post.products.all()]
    other_posts = (
        Post.objects.exclude(slug=slug).filter(live=True).order_by("-date")[:4]
    )
    return render(r, "news-item.html", locals())


def promo(r):
    from promo.models import Promo

    items = Promo.objects.order_by("-start")[:15]
    return render(r, "promo.html", locals())


def promo_spark(r, id):
    from promo.models import Promo

    promo = Promo.objects.get(id=id)
    return render(r, "spark/promo_modal.html", locals())


def review_spark(r, id):
    from promo.models import Review

    review = Review.objects.get(id=id)
    return render(r, "spark/review_modal.html", locals())


def credit(r):
    return render(r, "credit.html", locals())


def calculator(r):
    return render(r, "calc.html", locals())


def portfolio(r):
    from promo.models import Portfolio

    items = Portfolio.objects.all()
    pages = Paginator(items, PAGE_SIZE)
    page = pages.get_page(int(r.GET.get("page", 1)))
    return render(r, "portfolio.html", locals())


def portfolio_item(r, slug):
    from promo.models import Portfolio

    item = get_object_or_404(Portfolio, slug=slug)
    products = [pp.product for pp in item.products.all()]
    other_items = Portfolio.objects.exclude(slug=slug)[:6]
    return render(r, "portfolio-item.html", locals())


def policy(r):
    return render(r, "politics.html", locals())


def reviews(r):
    from promo.models import Review

    items = Review.objects.exclude(published_at=None).order_by("-published_at")
    pages = Paginator(items, PAGE_SIZE)
    page = pages.get_page(int(r.GET.get("page", 1)))
    return render(r, "reviews.html", locals())


def sitemap(r):
    return render(r, "sitemap.html", locals())


def delivery(r):
    return render(r, "delivery.html", locals())


def return_view(r):
    return render(r, "return-2.html", locals())


def partnership(r):
    return render(r, "sotr.html", locals())


def shinka(r):
    return render(r, "sotr2.html", locals())


def contacts(r):
    from locations.models import Shop
    from src.other.enums import DayOfWeek

    shops = Shop.objects.all()
    return render(r, "contacts.html", locals())


def cart(r):
    if in_spark(r):
        if r.GET.get('cartData'):
            data = json.loads(r.GET.get('cartData'))
            len_data = len(data)
            data = {int(d): data[d] for d in data}

        if r.GET.get('action') == 'add':
            product = Product.objects.get(pk=r.GET.get('id'))
            if data[product.pk] < product.rest:
                data[product.pk] += 1
        if r.GET.get('action') == 'remove':
            id = int(r.GET.get('id'))
            if data[id] > 0:
                data[id] -= 1

        data_json = json.dumps(data)
        products = Product.objects.filter(pk__in=data.keys())
        can_proceed = True
        similar_urls = {}
        total = 0
        for p in products:
            total += (p.current_price or p.price) * data[p.pk]
            if p.rest < data[p.pk]:
                similar_urls[p.pk] = make_similar_url(p)
                can_proceed = False
        if total == 0:
            can_proceed = False
        return render(r, "spark/cart_products.html", locals())
    if r.method == "POST":

        return redirect('/checkout/')
    return render(r, "cart1.html", locals())


def checkout(r):
    return render(r, "cart2.html", locals())


def favorites(r):
    return render(r, "favorites.html", locals())


def brands(r):
    rim_brand_ids = Product.objects.filter(rest__gt=0, type=ProductType.RIMS).values('brand_id').order_by('brand_id').distinct()
    rim_brands = Brand.objects.filter(pk__in=rim_brand_ids)
    return render(r, 'brands.html', locals())


def product(r, slug):
    item = get_object_or_404(Product, slug=slug)
    return render(r, "product.html", locals())

def login_spark(r):
    from users.models import User
    from users.tasks import broadcast_sms_task
    if r.method == 'POST':
        user = User.objects.get_or_create(phone_number=digits(r.POST['phone']))
        verification = user.verification
        verification.generate_token()
        task_data = {
            "phone_number": user.phone_number,
            "verify_code": verification.token,
        }
        broadcast_sms_task.delay(task_data)
        return render(r, 'spark/sms_modal.html', locals())
    return render(r, 'spark/login_modal.html', locals())


def check_sms_code(r):
    from urllib.parse import urlparse
    from django.http import HttpResponse
    if r.method == "POST":
        if urlparse(r.headers.get('referer')).path == 'cart':
            return HttpResponse("<div><script>window.location = '/checkout/'</script></div>")
    elif r.method == 'GET':
        return render(r, 'spark/sms_modal.html', locals())