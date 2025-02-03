from django.urls import path
from .views import ServiceList, ServiceDetail
from .views import UserRegister, UserProfile
from .views import BookingList, BookingDetail

urlpatterns = [
    path('services/', ServiceList.as_view(), name='service_list'),
    path('services/<int:id>/', ServiceDetail.as_view(), name='service_detail'),
    path('register/', UserRegister.as_view(), name='user_register'),
    path('profile/', UserProfile.as_view(), name='user_profile'),
    path('bookings/', BookingList.as_view(), name='booking_list'),
    path('bookings/<int:id>/', BookingDetail.as_view(), name='booking_detail'),
]