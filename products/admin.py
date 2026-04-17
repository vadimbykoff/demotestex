from django.contrib import admin
from products.models import Category, Product, Manufacturer, Supplier, Unit


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    ...

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ...

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    ...
