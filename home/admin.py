from django.contrib import admin
from .models import Customer,Product,Order,OrderProduct,ProductCategory
from import_export.admin import ImportExportModelAdmin

# Register your models here.
# admin.site.register(Customer)
# admin.site.register(Product)
# admin.site.register(Order)
# admin.site.register(OrderProduct)
# admin.site.register(ProductCategory)
@admin.register(Customer,Product,Order,OrderProduct,ProductCategory)
class ViewAdmin(ImportExportModelAdmin):
    pass