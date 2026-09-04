from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('wms', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='ProductBarcode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=80, unique=True)),
                ('kind', models.CharField(default='EAN/QR', max_length=30)),
                ('active', models.BooleanField(default=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='barcodes', to='wms.product')),
            ],
            options={'ordering': ['code']},
        ),
    ]
