# Generated by Django 2.2.6 on 2019-10-23 12:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Privilege',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('privilege_name', models.CharField(max_length=50)),
                ('privilege_ID', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Trigger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trigger_name', models.CharField(max_length=50)),
                ('trigger_data', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_nom', models.CharField(max_length=50)),
                ('contact_prenom', models.CharField(max_length=50)),
                ('contact_privilege', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Batz_API.Privilege')),
            ],
        ),
    ]
