# Generated by Django 2.1.5 on 2019-02-04 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(max_length=100, unique=True)),
                ('image', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('manufacturer', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('stock', models.PositiveIntegerField()),
            ],
        ),
    ]
