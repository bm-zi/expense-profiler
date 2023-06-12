from django.urls import path
from django.urls.conf import include
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="income"),
    path('add-income', views.add_income, name="add-income"),
    path('preferences/', include('userpreferences.urls')),
    path('edit-income/<int:id>', views.income_edit, name="edit-income"),
    path('delete-income/<int:id>', views.income_delete, name="delete-income"),
    path('search-income', csrf_exempt(views.search_income),
         name="search-income"),
    path('income-summary', views.income_source_summary, name="income-summary"),
    path('income-stats', views.stats_view, name="income-stats"),
    path('export-csv', views.export_csv, name="export-csv"),
    path('export-excel', views.export_excel, name="export-excel"),
]
