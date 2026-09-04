from django.urls import path
from .views import dashboard,mobile,stock,receipts,orders,pickings,movements
urlpatterns=[path('',dashboard,name='dashboard'),path('mobile/',mobile,name='mobile'),path('estoque/',stock,name='stock'),path('entradas/',receipts,name='receipts'),path('pedidos/',orders,name='orders'),path('separacoes/',pickings,name='pickings'),path('movimentacoes/',movements,name='movements')]
