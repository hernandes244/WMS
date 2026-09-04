from django.contrib import admin
from .models import *
admin.site.register([Product,ProductBarcode,Address,Lot,Stock,Imei,Receipt,ReceiptItem,Order,OrderItem,Picking,PickingItem,Movement])
