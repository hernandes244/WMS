from django.urls import path
from .api import login, me, scan, addresses, transfer

urlpatterns = [
    path('login/', login, name='api_login'),
    path('me/', me, name='api_me'),
    path('scan/', scan, name='api_scan'),
    path('addresses/', addresses, name='api_addresses'),
    path('transfer/', transfer, name='api_transfer'),
]
