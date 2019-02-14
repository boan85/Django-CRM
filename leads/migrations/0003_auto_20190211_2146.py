# Generated by Django 2.0.11 on 2019-02-11 16:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0002_lead_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lead',
            name='account',
        ),
        migrations.RemoveField(
            model_name='lead',
            name='description',
        ),
        migrations.RemoveField(
            model_name='lead',
            name='title',
        ),
        migrations.AddField(
            model_name='lead',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Leads', to='contacts.Contact'),
        ),
        migrations.AddField(
            model_name='lead',
            name='memo',
            field=models.TextField(blank=True, null=True, verbose_name='Memo'),
        ),
    ]
