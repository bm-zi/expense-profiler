from django.contrib import admin
from .models import Expense, Category

# Register your models here.


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'date', 'description', 'category')
    search_fields = ('amount', 'date', 'description', 'category')
    list_per_page = 10


admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)
