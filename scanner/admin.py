from django.contrib import admin
from scanner.models import Receipt, Shopping, Item
# Register your models here.

admin.site.register(Item)
admin.site.register(Shopping)
admin.site.register(Receipt)
