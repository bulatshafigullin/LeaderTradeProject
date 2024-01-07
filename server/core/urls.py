from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from django.conf import settings
from django.conf.urls.static import static

from core.settings import API_URL
import src.apps.web.urls

schema_view = get_schema_view(
    openapi.Info(
        title="LeaderTrade API",
        default_version="v1",
        description="Distribution Message API",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="fu7ur3gh057@gmail.com"),
        license=openapi.License(name="Your License"),
    ),
    # url="https://лидертрейд116.рф/",
    public=True,
)

urlpatterns = [
    # Healthcheck
    path(
        f"{API_URL}/health/",
        lambda request: HttpResponse("OK", content_type="text/plain"),
    ),
    # path(f"{API_URL}/auth/", include("src.apps.users.api.urls")),
    # path(f"{API_URL}/products/", include("products.api.urls")),
    # path(f"{API_URL}/profiles/", include("src.apps.profiles.api.urls")),
    # path(f"{API_URL}/locations/", include("locations.api.urls")),
    # path(f"{API_URL}/catalog/", include("catalog.api.urls")),
    # path(f"{API_URL}/interface/", include("src.apps.interface.api.urls")),
    # path(f"{API_URL}/orders/", include("src.apps.orders.api.urls")),
    # path(f"{API_URL}/actions/", include("src.apps.actions.api.urls")),
    # path(f"{API_URL}/news/", include("src.apps.news.api.urls")),
    # Admin
    path("admin/", admin.site.urls),
    # Wagtail
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("pages/", include(wagtail_urls)),
    # Swagger
    path(
        "swagger<str:format>",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path('', include(src.apps.web.urls))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "LeaderTrade"
admin.site.site_title = "LeaderTrade Admin Portal"
admin.site.index_title = "Welcome to the LeaderTrade Portal"
