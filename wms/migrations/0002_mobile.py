from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[('wms','0001_initial')]
    operations=[
        migrations.CreateModel(name='ProductBarcode',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('code',models.CharField(max_length=80,unique=True)),('kind',models.CharField(default='EAN/QR',max_length=30)),('active',models.BooleanField(default=True)),('product',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='barcodes',to='wms.product'))]),
        migrations.CreateModel(name='Imei',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('number',models.CharField(max_length=15,unique=True)),('status',models.CharField(choices=[('AVAILABLE','Disponível'),('RESERVED','Reservado'),('PICKED','Separado'),('SHIPPED','Expedido'),('BLOCKED','Bloqueado')],default='AVAILABLE',max_length=20)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('address',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,to='wms.address')),('product',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='imeis',to='wms.product')),('receipt',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,to='wms.receipt'))]),
    ]
