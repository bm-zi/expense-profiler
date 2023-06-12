from django.urls import path
from django.urls.conf import include
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="dashboard"),
    path('search-expenses', csrf_exempt(views.search_expenses),
         name="search-expenses"),
    # path('stats', views.stats, name="dashboard-stats"),
]
