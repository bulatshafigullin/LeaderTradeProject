from django.urls import path, include, register_converter
from src.apps.web import views as v

from web import path_converter

register_converter(path_converter.RimPathConverter, "rim_pathfilter")
register_converter(path_converter.TirePathConverter, "tire_pathfilter")

urlpatterns = [
    path("", v.home),
    path("sale/", v.catalog, {"slug": "sale", "title": "Распродажа"}),
    path("diski/", v.catalog, {"slug": "rims", "title": "Диски"}),
    path("diski/<rim_pathfilter:pathfilter>/", v.catalog, {"slug": "rims", "title": "Диски"}),
    path("shiny/", v.catalog, {"slug": "tires", "title": "Шины"}),
    path("shiny/<tire_pathfilter:pathfilter>/", v.catalog, {"slug": "tires", "title": "Шины"}),
    path("kolesa-v-sbore/", v.catalog, {"slug": "em", "title": "Колеса в сборе"}),
    path("aksessuary/", v.catalog, {"slug": "aksessuary", "title": "Аксессуары"}),
    
    path("product/<slug:slug>/", v.product),
    path("search/", v.search),
    path("about/", v.about),
    path("news/", v.news),
    path("news/<slug:slug>", v.news_item),
    path("promo/", v.promo),
    path("calculator/", v.calculator),
    path("portfolio/", v.portfolio),
    path("portfolio/<slug:slug>/", v.portfolio_item),
    path("policy/", v.policy),
    path("reviews/", v.reviews),
    path("sitemap/", v.sitemap),
    path("partnership/", v.partnership),
    path("shinomontazh/", v.shinka),
    path("payment-delivery/", v.delivery),
    path("return/", v.return_view),
    path("contacts/", v.contacts),
    path("cart/", v.cart),
    path("checkout/", v.checkout),
    path("favorites/", v.favorites),
    path("rassrochka/", v.credit),
    path("froala_editor/", include("froala_editor.urls")),
    path("js/spark/promo/<int:id>/", v.promo_spark),
    path("js/spark/review/<int:id>/", v.review_spark),
]
