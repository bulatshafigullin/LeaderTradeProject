from typing import Any

from bulk_update.helper import bulk_update
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import Q, F
from products.models import Product, Category

from core.settings import CHUNK_STEP
from catalog.models import Brand
from src.api.requests.fortochki_requests import (
    refresh_wsdl_file,
    find_rim_list,
    convert_code_list,
    get_rim_goods_info,
    find_tire_list,
    get_tire_goods_info,
)
from src.api.requests.starco_requests import (
    get_starco_rims,
    get_starco_stock,
    get_starco_prices,
    get_starco_tyres,
)
from src.apps.catalog.models import Brand
from src.apps.unloads.models import UnloadScheduler
from src.apps.unloads.utils import (
    update_fortochki_price_info,
    update_fortochki_rim_info,
    update_fortochki_tire_info,
    prepare_fortochki_rim,
    chunks,
    prepare_fortochki_tire, prepare_starco_tire, prepare_starco_rim,
)
from src.other.enums import ProductType, UnloadServiceType
from src.utils.slug_utils import slugify

logger = get_task_logger(__name__)


# 4TOCHKI TASKS
# BEAT
@shared_task(name="unload_fortochki_beat")
def unload_fortochki_beat() -> None:
    refresh_wsdl_file()
    logger.info("Unloading fortochki data...")
    scheduler = UnloadScheduler.objects.filter(
        service=UnloadServiceType.fortochki
    ).first()
    if scheduler.rim_unload:
        fortochki_unload_rims_task.delay()
    if scheduler.tire_unload:
        fortochki_unload_tires_task.delay()
    return None


def get_fortochki_filter(product_list: list[Any]) -> Q:
    filter_query = Q()
    for data in product_list:
        slug = slugify(data.name)
        data.slug = slug
        if data.code:
            filter_query |= Q(ext_data__code=data.code)
        else:
            filter_query |= Q(slug=slug)
    return filter_query


def get_starco_filter(product_list: list[Any]) -> Q:
    filter_query = Q()
    for data in product_list:
        slug = slugify(data.full_name)
        data.slug = slug
        if data.product_no:
            filter_query |= Q(ext_data__product_no=data.product_no)
        else:
            filter_query |= Q(slug=slug)
    return filter_query


@shared_task(name="fortochki_unload_rims_task")
def fortochki_unload_rims_task() -> None:
    code_list = []
    rim_list = find_rim_list()
    logger.info(f"founded disk list: {len(rim_list)}")
    rim_products = (
        Product.objects.all()
        .annotate(code=F("ext_data__code"))
        .filter(type=ProductType.RIMS, unload_service=UnloadServiceType.fortochki)
    )
    category = Category.objects.filter(title=ProductType.RIMS).first()
    # create or update rim
    for rims_chunk in chunks(rim_list, CHUNK_STEP):
        filter_query = get_fortochki_filter(product_list=rims_chunk)

        founded_rim = {
            it.code or it.slug: it
            for it in rim_products.filter(filter_query).annotate(
                code=F("ext_data__code")
            )
        }
        create_lst = []
        update_lst = []
        for rim_data in rims_chunk:
            product = founded_rim.get(rim_data.code or rim_data.slug)
            if product:
                product = update_fortochki_price_info(rim_data, product)
                update_lst.append(product)
            else:
                create_lst.append(rim_data)

        if update_lst:
            bulk_update(update_lst, update_fields=["rest", "price", "ext_data"])

        if create_lst:
            products = [prepare_fortochki_rim(it, category) for it in create_lst]
            products = Product.objects.bulk_create(products)
            for chunk in chunks(products, 200):
                task_data = [
                    p.ext_data["code"] for p in chunk if p.ext_data.get("code", None)
                ]
                fortochki_get_rim_info_task.delay(task_data)
    return None


@shared_task(name="fortochki_unload_tire_task")
def fortochki_unload_tire_task():
    code_list = []
    tire_list = find_tire_list()
    logger.info(f"founded tire list: {len(tire_list)}")
    tire_products = (
        Product.objects.all()
        .annotate(code=F("ext_data__code"))
        .filter(type=ProductType.TIRES, unload_service=UnloadServiceType.fortochki)
    )
    category = Category.objects.filter(title=ProductType.TIRES).first()
    # create or update tire
    for tires_chunk in chunks(tire_products, CHUNK_STEP):
        filter_query = get_fortochki_filter(product_list=tires_chunk)
        founded_tire = {
            it.code or it.slug: it
            for it in tire_products.filter(filter_query).annotate(
                code=F("ext_data__code")
            )
        }
        create_lst = []
        update_lst = []
        for tire_data in tires_chunk:
            product = founded_tire.get(tire_data.code or tire_data.slug)
            if product:
                product = update_fortochki_price_info(tire_data, product)
                update_lst.append(product)
                update_lst.append(product)
            else:
                create_lst.append(tire_data)
        # updating products
        if update_lst:
            bulk_update(update_lst, update_fields=["rest", "price", "ext_data"])
        # creating products
        if create_lst:
            products = [prepare_fortochki_tire(it, category) for it in create_lst]
            products = Product.objects.bulk_create(products)
            for chunk in chunks(products, 200):
                print(chunk)
                task_data = [
                    p.ext_data["code"] for p in chunk if p.ext_data.get("code", None)
                ]
                fortochki_get_tire_info_task.delay(task_data)
    return None


@shared_task(name="fortochki_get_rim_info_task")
def fortochki_get_rim_info_task(code_list: list) -> None:
    logger.info(f"start get rim goods info..., code_list: {len(code_list)}")
    converted_code_list = convert_code_list(code_list=code_list)
    info_list = {
        it.code: it for it in get_rim_goods_info(code_list=converted_code_list)
    }
    print(f"INFO LIST")
    products = Product.objects.annotate(code=F("ext_data__code")).filter(
        type=ProductType.RIMS, ext_data__code__in=info_list.keys()
    )
    brands = {brand.title: brand for brand in Brand.objects.all()}
    for p in products:
        info = info_list[p.code]
        brand_name = info.brand.upper()
        brand = brands.get(brand_name)
        if not brand:
            brand = Brand.objects.create(title=brand_name)
            brands[brand_name] = brand
        p.brand = brand
        update_fortochki_rim_info(data=info, rim=p)
    bulk_update(
        products,
        update_fields=[
            "dia",
            "et",
            "pcd",
            "unite_pcd",
            "bolts",
            "bolts2",
            "width",
            "brand",
        ],
    )
    return None


@shared_task(name="fortochki_get_tire_info_task")
def fortochki_get_tire_info_task(code_list: list) -> None:
    logger.info(f"start get rim goods info..., code_list: {len(code_list)}")
    converted_code_list = convert_code_list(code_list=code_list)
    info_list = {
        it.code: it for it in get_tire_goods_info(code_list=converted_code_list)
    }
    print(f"INFO LIST")
    products = Product.objects.annotate(code=F("ext_data__code")).filter(
        type=ProductType.TIRES, ext_data__code__in=info_list.keys()
    )
    brands = {brand.title: brand for brand in Brand.objects.all()}
    for p in products:
        info = info_list[p.code]
        brand_name = info.brand.upper()
        brand = brands.get(brand_name)
        if not brand:
            brand = Brand.objects.create(title=brand_name)
            brands[brand_name] = brand
        p.brand = brand
        update_fortochki_tire_info(data=info, tire=p)
    bulk_update(
        products,
        update_fields=[
            "width",
            "width2",
            "season",
            "height",
            "load_index",
            "speed_index",
            "brand",
        ],
    )
    return None


# STARCO TASKS
# BEAT
@shared_task(name="unload_starco_beat")
def unload_starco_beat() -> None:
    logger.info("Unloading starco data...")
    scheduler = UnloadScheduler.objects.filter(service=UnloadServiceType.starco).first()
    if scheduler.rim_unload:
        starco_get_rim_task()
    if scheduler.tire_unload:
        starco_get_tire_task()
    starco_get_stock_task.delay()
    return None


# @shared_task(name="starco_get_tire_task")
def starco_get_tire_task() -> None:
    brands = {brand.title: brand for brand in Brand.objects.all()}
    tire_list = get_starco_tyres()
    tire_products = (
        Product.objects.all()
        .annotate(product_no=F("ext_data__product_no"))
        .filter(type=ProductType.TIRES, unload_service=UnloadServiceType.starco)
    )
    product_list = {
        it.product_no: it for it in tire_products
    }
    category = Category.objects.filter(title=ProductType.TIRES).first()
    for tire_chunk in chunks(tire_list, CHUNK_STEP):
        filter_query = get_starco_filter(product_list=tire_chunk)
        founded_tire = {
            it.product_no or it.slug: it
            for it in tire_products.filter(filter_query).annotate(
                product_no=F("ext_data__product_no")
            )
        }
        create_lst = []
        for tire_data in tire_chunk:
            product = founded_tire.get(tire_data.product_no or tire_data.slug)
            # create brand if not exists
            if tire_data.Brand or tire_data.Brand != "":
                brand_name = tire_data.Brand.upper()
                brand = brands.get(brand_name)
                if not brand:
                    brand = Brand.objects.create(title=brand_name)
                    brands[brand_name] = brand
            if not product:
                create_lst.append(tire_data)
        if create_lst:
            products = [prepare_starco_tire(it, brands, category) for it in create_lst]
            res = [i for i in products if i is not None]
            Product.objects.bulk_create(res)
        return None

# @shared_task(name="starco_get_rim_task")
def starco_get_rim_task() -> None:
    brands = {brand.title: brand for brand in Brand.objects.all()}
    rim_list = get_starco_rims()
    rim_products = (
        Product.objects.all()
        .filter(type=ProductType.RIMS, unload_service=UnloadServiceType.starco)
        .annotate(product_no=F("ext_data__product_no"))
    )
    product_list = {
        it.product_no: it for it in rim_products
    }
    category = Category.objects.filter(title=ProductType.RIMS).first()
    for rim_chunk in chunks(rim_list, CHUNK_STEP):
        filter_query = get_starco_filter(product_list=rim_chunk)
        founded_tire = {
            it.product_no or it.slug: it
            for it in rim_products.filter(filter_query).annotate(
                product_no=F("ext_data__product_no")
            )
        }
        create_lst = []
        for rim_data in rim_chunk:
            product = founded_tire.get(rim_data.product_no or rim_data.slug)
            # create brand if not exists
            if rim_data.Brand or rim_data.Brand != "":
                brand_name = rim_data.Brand.upper()
                brand = brands.get(brand_name)
                if not brand:
                    brand = Brand.objects.create(title=brand_name)
                    brands[brand_name] = brand
            if not product:
                create_lst.append(rim_data)
        if create_lst:
            products = [prepare_starco_rim(it, brands, category) for it in create_lst]
            products = Product.objects.bulk_create(products)
    return None


# BEAT
@shared_task(name="starco_get_stock_beat")
def starco_get_stock_task() -> None:
    stock_list = get_starco_stock()
    logger.info("finished getting starco stock ...")
    product_no_list = [pr.product_no for pr in stock_list]
    products = (
        Product.objects.all().annotate(product_no=F("ext_data__product_no"))
        .filter(
            unload_service=UnloadServiceType.starco,
            product_no__in=product_no_list
        )
    )
    for chunk_stocks in chunks(stock_list, 200):
        product_no_list = [pr.product_no for pr in chunk_stocks]
        products = (
            Product.objects.filter(unload_service=UnloadServiceType.starco)
            .annotate(product_no=F("ext_data__product_no"))
            .filter(product_no__in=product_no_list)
        )
        updated_products: list[Product] = []
        for stock in chunk_stocks:
            for product in products:
                if product.product_no == stock.product_no:
                    current_rest_count = (
                        stock.BEL_STOCK
                        + stock.CEL_STOCK
                        + stock.EKT_STOCK
                        + stock.KAZ_STOCK
                        + stock.MOS_STOCK
                        + stock.UKR_STOCK
                    )
                    product.rest = current_rest_count
                    updated_products.append(product)
                    break
        bulk_update(updated_products, update_fields=["rest"])
    starco_get_price_list_task.delay()
    return None


@shared_task(name="starco_get_price_list_task")
def starco_get_price_list_task() -> None:
    price_list = get_starco_prices()
    logger.info("finished getting starco price list from API...")
    product_no_list = [pr.product_no for pr in price_list]
    products = (
        Product.objects.annotate(product_no=F("ext_data__product_no"))
        .filter(
            unload_service=UnloadServiceType.starco,
            product_no__in=product_no_list
        )
    )
    for chunk_prices in chunks(price_list, 200):
        product_no_list = [pr.product_no for pr in chunk_prices]
        products = (
            Product.objects.filter(unload_service=UnloadServiceType.starco)
            .annotate(product_no=F("ext_data__product_no"))
            .filter(product_no__in=product_no_list)
        )
        updated_products: list[Product] = []
        for price in chunk_prices:
            for product in products:
                if product.product_no == price.product_no:
                    product.price = price.price
                    updated_products.append(product)
                    break
        bulk_update(updated_products, update_fields=["price"])
    return None
