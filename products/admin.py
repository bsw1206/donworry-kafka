from django.contrib import admin
from .models import FinancialCompany, Product, ProductOption

admin.site.register(FinancialCompany)
admin.site.register(Product)
admin.site.register(ProductOption)