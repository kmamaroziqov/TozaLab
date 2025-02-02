from django.urls import path
from .views import get_services

urlpatterns = [
    path('services/', get_services, name='get_services'),
]