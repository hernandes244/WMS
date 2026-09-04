from django.urls import path
from .api import login,me,scan,addresses,receipts,receive,transfer,inventory,orders,create_picking,pickings,pick,validate_imei

urlpatterns=[
    path('login/',login,name='api_login'),
    path('me/',me,name='api_me'),
    path('scan/',scan,name='api_scan'),
    path('addresses/',addresses,name='api_addresses'),
    path('receipts/',receipts,name='api_receipts'),
    path('receive/',receive,name='api_receive'),
    path('transfer/',transfer,name='api_transfer'),
    path('inventory/',inventory,name='api_inventory'),
    path('orders/',orders,name='api_orders'),
    path('picking/create/',create_picking,name='api_picking_create'),
    path('pickings/',pickings,name='api_pickings'),
    path('picking/pick/',pick,name='api_pick'),
    path('imei/validate/',validate_imei,name='api_imei_validate'),
]
