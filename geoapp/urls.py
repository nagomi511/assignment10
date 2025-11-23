from django.urls import path
from . import views

urlpatterns = [
    path('', views.continent_weather_view, name='continent_form'),
    path('history/', views.history_view, name='history'),
]
