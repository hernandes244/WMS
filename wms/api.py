from decimal import Decimal, InvalidOperation
from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Product, ProductBarcode, Address, Stock, Movement


def product_payload(product):
    return {
        'id': product.id,
        'code': product.code,
        'description': product.description,
        'unit': product.unit,
        'imei_control': product.imei_control,
        'barcodes': list(product.barcodes.filter(active=True).values_list('code', flat=True)),
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = str(request.data.get('username', '')).strip()
    password = str(request.data.get('password', ''))
    user = authenticate(username=username, password=password)
    if not user or not user.is_active:
        return Response({'ok': False, 'error': 'Usuário ou senha inválidos.'}, status=401)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'ok': True, 'token': token.key, 'user': user.username})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({'ok': True, 'user': request.user.username})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def scan(request):
    code = str(request.query_params.get('code', '')).strip()
    if not code:
        return Response({'ok': False, 'error': 'Informe um código.'}, status=400)
    barcode = ProductBarcode.objects.select_related('product').filter(code=code, active=True, product__active=True).first()
    product = barcode.product if barcode else Product.objects.filter(code=code, active=True).first()
    if not product:
        return Response({'ok': False, 'found': False, 'error': 'Código não cadastrado no WMS.'}, status=404)
    stocks = Stock.objects.filter(product=product).select_related('address','lot').order_by('address__code')
    return Response({'ok': True, 'found': True, 'product': product_payload(product), 'stock': [
        {'address': s.address.code, 'quantity': str(s.quantity), 'reserved': str(s.reserved), 'blocked': str(s.blocked), 'available': str(s.available), 'lot': s.lot.code if s.lot else None}
        for s in stocks
    ]})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def addresses(request):
    return Response({'ok': True, 'addresses': list(Address.objects.filter(active=True).order_by('code').values('id','code'))})

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def transfer(request):
    try:
        product_id = int(request.data.get('product_id'))
        source_id = int(request.data.get('source_id'))
        destination_id = int(request.data.get('destination_id'))
        quantity = Decimal(str(request.data.get('quantity')))
    except (TypeError, ValueError, InvalidOperation):
        return Response({'ok': False, 'error': 'Dados de transferência inválidos.'}, status=400)
    if quantity <= 0:
        return Response({'ok': False, 'error': 'A quantidade deve ser maior que zero.'}, status=400)
    if source_id == destination_id:
        return Response({'ok': False, 'error': 'Origem e destino devem ser diferentes.'}, status=400)
    with transaction.atomic():
        source = Stock.objects.select_for_update().filter(product_id=product_id, address_id=source_id).first()
        if not source or source.available < quantity:
            return Response({'ok': False, 'error': 'Estoque disponível insuficiente na origem.'}, status=409)
        destination, _ = Stock.objects.select_for_update().get_or_create(product_id=product_id, address_id=destination_id, lot=source.lot, defaults={'quantity': 0})
        source.quantity -= quantity
        destination.quantity += quantity
        source.save(update_fields=['quantity'])
        destination.save(update_fields=['quantity'])
        Movement.objects.create(product_id=product_id, source_id=source_id, destination_id=destination_id, quantity=quantity, movement_type='TRANSFER', reference='MOBILE', user=request.user)
    return Response({'ok': True, 'message': 'Transferência realizada com sucesso.'})
