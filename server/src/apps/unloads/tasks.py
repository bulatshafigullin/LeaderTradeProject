from bulk_update.helper import bulk_update
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import Q, F

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
from products.models import Product, Category
from src.apps.unloads.models import UnloadScheduler
from src.apps.unloads.utils import (
    update_fortochki_price_info,
    create_fortochki_rim,
    update_fortochki_rim_info,
    create_fortochki_tire,
    update_fortochki_tire_info,
    starco_create_rim,
    starco_create_tire,
    prepare_fortochki_rim,
    chunks,
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


@shared_task(name="fortochki_unload_rims_task")
def fortochki_unload_rims_task() -> None:
    code_list = []
    rim_list = find_rim_list()
    logger.info(f"founded disk list: {len(rim_list)}")
    rim_products = (
        Product.objects.all()
        .annotate(code=F("ext_data__code"))
        .filter(type=ProductType.RIMS)
    )
    category = Category.objects.filter(title=ProductType.RIMS).first()
    # create or update rim
    for rims_chunk in chunks(rim_list, CHUNK_STEP):
        filter_query = Q()
        for rim_data in rims_chunk:
            slug = slugify(rim_data.name)
            rim_data.slug = slug
            if rim_data.code:
                filter_query |= Q(ext_data__code=rim_data.code)
            else:
                filter_query |= Q(slug=slug)

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
                fortochki_get_rim_info_task.delay(
                    [p.ext_data["code"] for p in products if p.ext_data.get("code")]
                )
    return None


@shared_task(name="fortochki_get_rim_info_task")
def fortochki_get_rim_info_task(code_list: list) -> None:
    logger.info(f"start get rim goods info...")
    converted_code_list = convert_code_list(code_list=code_list)
    info_list = {
        it.code: it for it in get_rim_goods_info(code_list=converted_code_list)
    }
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


@shared_task(name="fortochki_unload_tires_task")
def fortochki_unload_tires_task() -> None:
    code_list = []
    tire_list = find_tire_list()
    logger.info(f"founded tire list: {len(tire_list)}")
    tire_products = (
        Product.objects.all()
        .annotate(code=F("ext_data__code"))
        .filter(type=ProductType.TIRES)
    )
    # create or update tire
    for tire_data in tire_list:
        slug = slugify(tire_data.name)
        filter_query = Q(code=tire_data.code) | Q(slug=slug)
        founded_tire = tire_products.filter(filter_query).first()
        if founded_tire is not None:
            update_fortochki_price_info(data=tire_data, product=founded_tire)
        else:
            try:
                code = create_fortochki_tire(data=tire_data)
                code_list.append(code)
            except Exception as ex:
                logger.info(ex)
    chunked_list = [
        code_list[i : i + CHUNK_STEP] for i in range(0, len(code_list), CHUNK_STEP)
    ]
    logger.info(f"chunked list size {len(chunked_list)}")
    any([fortochki_get_tire_info_task.delay(i) for i in chunked_list])
    return None


@shared_task(name="fortochki_get_tire_info_task")
def fortochki_get_tire_info_task(code_list: list) -> None:
    logger.info(f"start get tire goods info...")
    converted_code_list = convert_code_list(code_list=code_list)
    info_list = get_tire_goods_info(code_list=converted_code_list)
    logger.info(info_list)
    for info in info_list:
        update_fortochki_tire_info(data=info)
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
    tire_list = get_starco_tyres()
    for tire_data in tire_list:
        slug = slugify(tire_data.full_name)
        filter_query = Q(type=ProductType.TIRES) & (
            Q(ext_data__product_no=tire_data.product_no) | Q(slug=slug)
        )
        if Product.objects.filter(filter_query).exists():
            continue
        else:
            starco_create_tire(data=tire_data)


# @shared_task(name="starco_get_rim_task")
def starco_get_rim_task() -> None:
    rim_list = get_starco_rims()
    for rim_data in rim_list:
        slug = slugify(rim_data.full_name)
        filter_query = Q(type=ProductType.RIMS) & (
            Q(ext_data__product_no=rim_data.product_no) | Q(slug=slug)
        )
        if Product.objects.filter(filter_query).exists():
            continue
        else:
            starco_create_rim(data=rim_data)
    starco_get_stock_task.delay()
    return None


# BEAT
@shared_task(name="starco_get_stock_beat")
def starco_get_stock_task() -> None:
    stock_list = get_starco_stock()
    logger.info("finished getting starco stock ...")
    chunked_stock_list = [
        stock_list[i : i + CHUNK_STEP] for i in range(0, len(stock_list), CHUNK_STEP)
    ]
    for chunk_stocks in chunked_stock_list:
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
    logger.info("finished getting starco price list ...")
    chunked_price_list = [
        price_list[i : i + CHUNK_STEP] for i in range(0, len(price_list), CHUNK_STEP)
    ]
    for chunk_prices in chunked_price_list:
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
