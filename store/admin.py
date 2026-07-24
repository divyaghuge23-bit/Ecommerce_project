from django.contrib import admin
from .models import Product, Category


# ✅ Category Admin
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


# ✅ Product Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'price', 'category','description')


# ✅ Register models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)