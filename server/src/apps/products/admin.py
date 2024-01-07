from django.contrib import admin

from products.models import (
    Category,
    Product,
    ProductImage,
)


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["pk_id", "title", "parent", "slug"]
    list_display_links = ["pk_id", "title", "slug"]
    prepopulated_fields = {'slug': ('title',), }


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "pk_id",
        "title",
        "category",
        "slug",
        "price",
        "discount",
        "rest",
        "created_at",
    ]
    list_display_links = [
        "pk_id",
        "category",
        "price",
        "discount",
    ]
    list_filter = ["category"]
    search_fields = ["title"]
    inlines = [
        ProductImageInline,
    ]
    raw_id_fields = ("category",)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
