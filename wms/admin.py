from django.contrib import admin
from .models import *
admin.site.register([Product,Address,Lot,Stock,Receipt,ReceiptItem,Order,OrderItem,Picking,PickingItem,Movement])
