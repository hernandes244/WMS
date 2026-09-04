from decimal import Decimal, InvalidOperation
from datetime import date
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import F
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Product, ProductBarcode, Address, Stock, Movement, Receipt, ReceiptItem, Lot, Order, Picking, PickingItem, Imei

def product_payload(product):
    return {'id':product.id,'code':product.code,'description':product.description,'unit':product.unit,'imei_control':product.imei_control,'barcodes':list(product.barcodes.filter(active=True).values_list('code',flat=True))}

def parse_qty(value):
    q=Decimal(str(value))
    if q<=0: raise InvalidOperation
    return q

def luhn(value):
    if len(value)!=15 or not value.isdigit(): return False
    total=0
    for i,d in enumerate(value):
        n=int(d)
        if i%2==0:
            n*=2
            if n>9: n-=9
        total+=n
    return total%10==0

def stock_payload(s):
    return {'id':s.id,'address_id':s.address_id,'address':s.address.code,'quantity':str(s.quantity),'reserved':str(s.reserved),'blocked':str(s.blocked),'available':str(s.available),'lot':s.lot.code if s.lot else None}

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username=str(request.data.get('username','')).strip(); password=str(request.data.get('password',''))
    user=authenticate(username=username,password=password)
    if not user or not user.is_active: return Response({'ok':False,'error':'Usuário ou senha inválidos.'},status=401)
    token,_=Token.objects.get_or_create(user=user)
    return Response({'ok':True,'token':token.key,'user':user.username})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def me(request): return Response({'ok':True,'user':request.user.username})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def scan(request):
    code=str(request.query_params.get('code','')).strip()
    if not code: return Response({'ok':False,'error':'Informe um código.'},status=400)
    barcode=ProductBarcode.objects.select_related('product').filter(code=code,active=True,product__active=True).first()
    product=barcode.product if barcode else Product.objects.filter(code=code,active=True).first()
    if not product: return Response({'ok':False,'found':False,'error':'Código não cadastrado no WMS.'},status=404)
    stocks=Stock.objects.filter(product=product).select_related('address','lot').order_by('address__code')
    return Response({'ok':True,'found':True,'product':product_payload(product),'stock':[stock_payload(s) for s in stocks]})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def addresses(request):
    return Response({'ok':True,'addresses':list(Address.objects.filter(active=True).order_by('code').values('id','code'))})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def receipts(request):
    data=[]
    for r in Receipt.objects.filter(status__in=['OPEN','CHECKING','DIVERGENCE']).order_by('-received_at')[:100]:
        data.append({'id':r.id,'number':r.number,'invoice':r.invoice,'supplier':r.supplier,'status':r.status,'items':[{'id':i.id,'product':product_payload(i.product),'expected':str(i.expected),'received':str(i.received),'lot_code':i.lot_code,'expiry':i.expiry.isoformat() if i.expiry else None} for i in r.items.select_related('product')]})
    return Response({'ok':True,'receipts':data})

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def receive(request):
    try:
        receipt=Receipt.objects.get(pk=int(request.data.get('receipt_id'))); product=Product.objects.get(pk=int(request.data.get('product_id')),active=True); address=Address.objects.get(pk=int(request.data.get('address_id')),active=True); quantity=parse_qty(request.data.get('quantity'))
    except (Receipt.DoesNotExist,Product.DoesNotExist,Address.DoesNotExist,TypeError,ValueError,InvalidOperation): return Response({'ok':False,'error':'Dados de recebimento inválidos.'},status=400)
    lot_code=str(request.data.get('lot_code','')).strip(); expiry_raw=str(request.data.get('expiry','')).strip(); expiry=None
    if expiry_raw:
        try: expiry=date.fromisoformat(expiry_raw)
        except ValueError: return Response({'ok':False,'error':'Validade inválida. Use AAAA-MM-DD.'},status=400)
    imeis=[str(x).strip() for x in request.data.get('imeis',[]) if str(x).strip()]
    if product.imei_control:
        if quantity != int(quantity) or len(imeis)!=int(quantity) or len(set(imeis))!=len(imeis): return Response({'ok':False,'error':'Produto com controle de IMEI exige um IMEI único para cada unidade recebida.'},status=400)
        if any(not luhn(x) for x in imeis): return Response({'ok':False,'error':'Existe IMEI inválido. Deve ter 15 dígitos e passar no Luhn.'},status=400)
        if Imei.objects.filter(number__in=imeis).exists(): return Response({'ok':False,'error':'Um ou mais IMEIs já estão cadastrados.'},status=409)
    with transaction.atomic():
        lot=None
        if lot_code:
            lot,_=Lot.objects.get_or_create(product=product,code=lot_code,defaults={'expiry':expiry})
            if expiry and lot.expiry!=expiry: lot.expiry=expiry; lot.save(update_fields=['expiry'])
        stock,_=Stock.objects.select_for_update().get_or_create(product=product,address=address,lot=lot,defaults={'quantity':0})
        stock.quantity+=quantity; stock.save(update_fields=['quantity'])
        item=receipt.items.filter(product=product).order_by('id').first()
        if item: item.received+=quantity; item.save(update_fields=['received'])
        Movement.objects.create(product=product,destination=address,quantity=quantity,movement_type='IN',reference=f'RECEIPT:{receipt.number}',user=request.user)
        for n in imeis: Imei.objects.create(product=product,number=n,address=address,receipt=receipt)
    return Response({'ok':True,'message':'Recebimento confirmado e estoque atualizado.'})

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def transfer(request):
    try: product_id=int(request.data.get('product_id')); source_id=int(request.data.get('source_id')); destination_id=int(request.data.get('destination_id')); quantity=parse_qty(request.data.get('quantity'))
    except (TypeError,ValueError,InvalidOperation): return Response({'ok':False,'error':'Dados de transferência inválidos.'},status=400)
    if source_id==destination_id: return Response({'ok':False,'error':'Origem e destino devem ser diferentes.'},status=400)
    lot_id=request.data.get('lot_id')
    with transaction.atomic():
        qs=Stock.objects.select_for_update().filter(product_id=product_id,address_id=source_id)
        if lot_id: qs=qs.filter(lot_id=lot_id)
        source=qs.order_by('lot__expiry','id').first()
        if not source or source.available<quantity: return Response({'ok':False,'error':'Estoque disponível insuficiente na origem.'},status=409)
        destination,_=Stock.objects.select_for_update().get_or_create(product_id=product_id,address_id=destination_id,lot=source.lot,defaults={'quantity':0})
        source.quantity-=quantity; destination.quantity+=quantity; source.save(update_fields=['quantity']); destination.save(update_fields=['quantity'])
        Movement.objects.create(product_id=product_id,source_id=source_id,destination_id=destination_id,quantity=quantity,movement_type='TRANSFER',reference='MOBILE',user=request.user)
        if product_id and int(quantity)==quantity:
            ids=list(Imei.objects.filter(product_id=product_id,address_id=source_id,status='AVAILABLE').values_list('id',flat=True)[:int(quantity)])
            if ids: Imei.objects.filter(id__in=ids).update(address_id=destination_id)
    return Response({'ok':True,'message':'Transferência realizada com sucesso.'})

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def inventory(request):
    try:
        product=Product.objects.get(pk=int(request.data.get('product_id')),active=True); address=Address.objects.get(pk=int(request.data.get('address_id')),active=True); counted=parse_qty(request.data.get('counted_quantity'))
    except (Product.DoesNotExist,Address.DoesNotExist,TypeError,ValueError,InvalidOperation): return Response({'ok':False,'error':'Dados de inventário inválidos.'},status=400)
    lot_code=str(request.data.get('lot_code','')).strip(); lot=None
    if lot_code: lot=Lot.objects.filter(product=product,code=lot_code).first() or Lot.objects.create(product=product,code=lot_code)
    with transaction.atomic():
        stock,_=Stock.objects.select_for_update().get_or_create(product=product,address=address,lot=lot,defaults={'quantity':0})
        old=stock.quantity; delta=counted-old; stock.quantity=counted; stock.save(update_fields=['quantity'])
        if delta: Movement.objects.create(product=product,source=address,destination=address,quantity=abs(delta),movement_type='ADJUST',reference=f'INVENTORY old={old} new={counted}',user=request.user)
    return Response({'ok':True,'message':f'Inventário confirmado. Saldo ajustado de {old} para {counted}.','difference':str(delta)})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def orders(request):
    data=[]
    for o in Order.objects.filter(status__in=['RECEIVED','RELEASED','PICKING']).order_by('priority','created_at')[:100]:
        data.append({'id':o.id,'number':o.number,'customer':o.customer,'priority':o.priority,'status':o.status,'items':[{'id':i.id,'product':product_payload(i.product),'quantity':str(i.quantity),'picked':str(i.picked)} for i in o.items.select_related('product')]})
    return Response({'ok':True,'orders':data})

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_picking(request):
    order_ids=request.data.get('order_ids') or []
    if not order_ids: return Response({'ok':False,'error':'Selecione pelo menos um pedido.'},status=400)
    try: ids=[int(x) for x in order_ids]; orders_q=list(Order.objects.filter(id__in=ids,status__in=['RECEIVED','RELEASED']).prefetch_related('items__product'))
    except (TypeError,ValueError): return Response({'ok':False,'error':'Pedidos inválidos.'},status=400)
    if not orders_q: return Response({'ok':False,'error':'Nenhum pedido elegível.'},status=400)
    with transaction.atomic():
        p=Picking.objects.create(number=f'P{date.today().strftime("%Y%m%d")}-{Picking.objects.count()+1:05d}',status='RELEASED')
        for o in orders_q:
            o.status='PICKING'; o.save(update_fields=['status'])
            for oi in o.items.all():
                remaining=oi.quantity-oi.picked
                if remaining<=0: continue
                stocks=Stock.objects.filter(product=oi.product).select_related('address').order_by('address__code','lot__expiry')
                for s in stocks:
                    take=min(remaining,s.available)
                    if take>0:
                        PickingItem.objects.create(picking=p,order_item=oi,address=s.address,quantity=take); s.reserved+=take; s.save(update_fields=['reserved']); remaining-=take
                    if remaining<=0: break
        if not p.items.exists(): p.delete(); return Response({'ok':False,'error':'Não há estoque disponível para os pedidos selecionados.'},status=409)
    return Response({'ok':True,'message':f'Separação {p.number} gerada.','picking_id':p.id,'number':p.number})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def pickings(request):
    data=[]
    for p in Picking.objects.filter(status__in=['RELEASED','RUNNING']).order_by('created_at')[:50]:
        data.append({'id':p.id,'number':p.number,'status':p.status,'items':[{'id':i.id,'order':i.order_item.order.number,'product':product_payload(i.order_item.product),'address_id':i.address_id,'address':i.address.code,'quantity':str(i.quantity),'picked':str(i.picked)} for i in p.items.select_related('order_item__order','order_item__product','address')]})
    return Response({'ok':True,'pickings':data})

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def pick(request):
    try: item=PickingItem.objects.select_related('order_item__product','order_item__order','address').get(pk=int(request.data.get('picking_item_id'))); quantity=parse_qty(request.data.get('quantity'))
    except (PickingItem.DoesNotExist,TypeError,ValueError,InvalidOperation): return Response({'ok':False,'error':'Item de separação inválido.'},status=400)
    scanned_code=str(request.data.get('code','')).strip(); scanned_address=str(request.data.get('address','')).strip(); product=item.order_item.product
    barcode=ProductBarcode.objects.filter(code=scanned_code,active=True,product=product).exists() or scanned_code==product.code
    if not barcode: return Response({'ok':False,'error':'PRODUTO ERRADO. A leitura não corresponde ao item da separação.'},status=409)
    if scanned_address and scanned_address!=item.address.code: return Response({'ok':False,'error':'ENDEREÇO ERRADO. Vá para o endereço indicado.'},status=409)
    if item.picked+quantity>item.quantity: return Response({'ok':False,'error':'Quantidade maior que a solicitada.'},status=409)
    with transaction.atomic():
        s=Stock.objects.select_for_update().filter(product=product,address=item.address).order_by('lot__expiry','id').first()
        if not s or s.available<quantity: return Response({'ok':False,'error':'Estoque insuficiente no endereço.'},status=409)
        s.quantity-=quantity; s.reserved-=min(s.reserved,quantity); s.save(update_fields=['quantity','reserved'])
        item.picked+=quantity; item.save(update_fields=['picked'])
        oi=item.order_item; oi.picked+=quantity; oi.save(update_fields=['picked'])
        Movement.objects.create(product=product,source=item.address,quantity=quantity,movement_type='OUT',reference=f'PICKING:{item.picking.number}',user=request.user)
        item.picking.status='RUNNING'; item.picking.save(update_fields=['status'])
        if not item.picking.items.filter(picked__lt=F('quantity')).exists(): item.picking.status='DONE'; item.picking.save(update_fields=['status'])
        if not oi.order.items.filter(picked__lt=F('quantity')).exists(): oi.order.status='PICKED'; oi.order.save(update_fields=['status'])
    return Response({'ok':True,'message':'Produto conferido e separado corretamente.'})

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def validate_imei(request):
    number=''.join(ch for ch in str(request.data.get('imei','')).strip() if ch.isdigit()); product_id=request.data.get('product_id')
    if not luhn(number): return Response({'ok':False,'valid':False,'error':'IMEI inválido: são necessários 15 dígitos e dígito verificador Luhn correto.'},status=400)
    obj=Imei.objects.select_related('product','address').filter(number=number).first()
    if not obj: return Response({'ok':False,'valid':False,'registered':False,'error':'IMEI válido, porém não cadastrado no WMS.'},status=404)
    if product_id and obj.product_id!=int(product_id): return Response({'ok':False,'valid':False,'error':'IMEI pertence a outro produto.'},status=409)
    if obj.status in ['BLOCKED','SHIPPED']: return Response({'ok':False,'valid':False,'error':f'IMEI não pode ser utilizado. Status: {obj.status}.'},status=409)
    return Response({'ok':True,'valid':True,'registered':True,'imei':number,'product':product_payload(obj.product),'status':obj.status,'address':obj.address.code if obj.address else None})
