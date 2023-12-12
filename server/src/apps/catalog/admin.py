from django.contrib import admin

from src.apps.catalog.models import Make, Model, Brand


class MakeAdmin(admin.ModelAdmin):
    list_display = ["pk_id", "title"]
    list_display_links = ["pk_id"]
    search_fields = ["title"]


class ModelAdmin(admin.ModelAdmin):
    list_display = ["pk_id", "make", "title"]
    list_display_links = ["pk_id", "make"]
    search_fields = ["make", "title"]


class BrandAdmin(admin.ModelAdmin):
    list_display = ["pk_id", "title"]
    list_display_links = ["pk_id", "title"]
    search_fields = ["title"]


admin.site.register(Make, MakeAdmin)
admin.site.register(Model, ModelAdmin)
admin.site.register(Brand, BrandAdmin)
