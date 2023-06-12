from django.contrib import admin
from .models import Income, Source

# Register your models here.


class IncomeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'date', 'description', 'source')
    search_fields = ('amount', 'date', 'description', 'source')
    list_per_page = 10


admin.site.register(Income, IncomeAdmin)
admin.site.register(Source)
