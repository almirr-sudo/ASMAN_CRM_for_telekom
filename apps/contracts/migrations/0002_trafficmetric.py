from django.db import migrations, models
import decimal


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrafficMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('calls', models.PositiveIntegerField(default=0)),
                ('sms', models.PositiveIntegerField(default=0)),
                ('data_mb', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=12)),
                ('topups', models.PositiveIntegerField(default=0)),
                ('charges', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=12)),
                ('source', models.CharField(choices=[('emulator', 'Эмулятор'), ('import', 'Импорт')], default='emulator', max_length=20)),
            ],
            options={
                'verbose_name': 'Метрика трафика',
                'verbose_name_plural': 'Метрики трафика',
                'ordering': ['-timestamp'],
            },
        ),
    ]
