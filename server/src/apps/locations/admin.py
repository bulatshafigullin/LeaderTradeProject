from django.contrib import admin

from locations.models import City, Address, Shop, Worktime


class WorktimeInline(admin.StackedInline):
    model = Worktime
    extra = 1


class CityAdmin(admin.ModelAdmin):
    list_display = ["pk_id", "title", "created_at"]
    list_display_links = ["pk_id", "title"]
    search_fields = ["title"]


class AddressAdmin(admin.ModelAdmin):
    list_display = ["pk_id", "city", "street", "house", "apartment"]
    list_display_links = ["pk_id", "city", "street"]
    search_fields = ["street"]
    raw_id_fields = ("city",)


class ShopAdmin(admin.ModelAdmin):
    list_display = ["pk_id", "address", "email"]
    list_display_links = ["pk_id", "address"]
    raw_id_fields = ("address",)
    inlines = [
        WorktimeInline,
    ]


admin.site.register(City, CityAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Shop, ShopAdmin)
