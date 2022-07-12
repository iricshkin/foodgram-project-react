# Generated by Django 2.2.19 on 2022-07-12 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20220712_2113'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Subscribe',
            new_name='Subscription',
        ),
        migrations.AddField(
            model_name='user',
            name='is_subcribed',
            field=models.BooleanField(default=False, help_text='Отметьте для подписки на автора', verbose_name='Подписка на данного автора'),
        ),
    ]
