from django.db import models

class Product(models.Model):
    code=models.CharField(max_length=80,unique=True)
    description=models.CharField(max_length=255)
    unit=models.CharField(max_length=10,default='UN')
    min_stock=models.DecimalField(max_digits=14,decimal_places=3,default=0)
    imei_control=models.BooleanField(default=False)
    active=models.BooleanField(default=True)
    def __str__(self): return f'{self.code} - {self.description}'

class ProductBarcode(models.Model):
    product=models.ForeignKey(Product,related_name='barcodes',on_delete=models.CASCADE)
    code=models.CharField(max_length=80,unique=True)
    kind=models.CharField(max_length=30,default='EAN/QR')
    active=models.BooleanField(default=True)
    class Meta:
        ordering=['code']
    def __str__(self): return f'{self.code} -> {self.product.code}'

class Address(models.Model):
    code=models.CharField(max_length=40,unique=True)
    aisle=models.CharField(max_length=20,blank=True)
    level=models.PositiveIntegerField(default=1)
    capacity=models.DecimalField(max_digits=14,decimal_places=3,default=0)
    active=models.BooleanField(default=True)
    def __str__(self): return self.code

class Lot(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    code=models.CharField(max_length=80)
    expiry=models.DateField(null=True,blank=True)
    class Meta: unique_together=('product','code')

class Stock(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    address=models.ForeignKey(Address,on_delete=models.CASCADE)
    lot=models.ForeignKey(Lot,null=True,blank=True,on_delete=models.PROTECT)
    quantity=models.DecimalField(max_digits=14,decimal_places=3,default=0)
    reserved=models.DecimalField(max_digits=14,decimal_places=3,default=0)
    blocked=models.DecimalField(max_digits=14,decimal_places=3,default=0)
    class Meta: unique_together=('product','address','lot')
    @property
    def available(self): return self.quantity-self.reserved-self.blocked

class Receipt(models.Model):
    STATUS=[('OPEN','Aberta'),('CHECKING','Conferindo'),('DONE','Finalizada'),('DIVERGENCE','Divergência')]
    number=models.CharField(max_length=40,unique=True)
    invoice=models.CharField(max_length=50,blank=True)
    supplier=models.CharField(max_length=255)
    received_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,choices=STATUS,default='OPEN')

class ReceiptItem(models.Model):
    receipt=models.ForeignKey(Receipt,related_name='items',on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.PROTECT)
    expected=models.DecimalField(max_digits=14,decimal_places=3)
    received=models.DecimalField(max_digits=14,decimal_places=3,default=0)
    lot_code=models.CharField(max_length=80,blank=True)
    expiry=models.DateField(null=True,blank=True)

class Order(models.Model):
    STATUS=[('RECEIVED','Recebido'),('RELEASED','Liberado'),('PICKING','Em separação'),('PICKED','Separado'),('SHIPPED','Expedido'),('CANCELLED','Cancelado')]
    number=models.CharField(max_length=50,unique=True)
    customer=models.CharField(max_length=255,blank=True)
    priority=models.PositiveIntegerField(default=5)
    status=models.CharField(max_length=20,choices=STATUS,default='RECEIVED')
    created_at=models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order=models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.PROTECT)
    quantity=models.DecimalField(max_digits=14,decimal_places=3)
    picked=models.DecimalField(max_digits=14,decimal_places=3,default=0)

class Picking(models.Model):
    STATUS=[('OPEN','Aberta'),('RELEASED','Liberada'),('RUNNING','Em execução'),('DONE','Concluída')]
    number=models.CharField(max_length=40,unique=True)
    status=models.CharField(max_length=20,choices=STATUS,default='OPEN')
    created_at=models.DateTimeField(auto_now_add=True)

class PickingItem(models.Model):
    picking=models.ForeignKey(Picking,related_name='items',on_delete=models.CASCADE)
    order_item=models.ForeignKey(OrderItem,on_delete=models.PROTECT)
    address=models.ForeignKey(Address,on_delete=models.PROTECT)
    quantity=models.DecimalField(max_digits=14,decimal_places=3)
    picked=models.DecimalField(max_digits=14,decimal_places=3,default=0)

class Movement(models.Model):
    TYPE=[('TRANSFER','Transferência'),('IN','Entrada'),('OUT','Saída'),('ADJUST','Ajuste'),('BLOCK','Bloqueio'),('UNBLOCK','Desbloqueio')]
    product=models.ForeignKey(Product,on_delete=models.PROTECT)
    source=models.ForeignKey(Address,null=True,blank=True,related_name='movement_source',on_delete=models.PROTECT)
    destination=models.ForeignKey(Address,null=True,blank=True,related_name='movement_destination',on_delete=models.PROTECT)
    quantity=models.DecimalField(max_digits=14,decimal_places=3)
    movement_type=models.CharField(max_length=20,choices=TYPE)
    reference=models.CharField(max_length=80,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey('auth.User',null=True,blank=True,on_delete=models.SET_NULL)
