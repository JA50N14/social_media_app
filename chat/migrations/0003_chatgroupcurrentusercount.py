# Generated by Django 5.1.2 on 2025-01-03 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_chatviewed'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatGroupCurrentUserCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_group', models.CharField(max_length=150)),
                ('connected_user_count', models.IntegerField(default=1)),
            ],
            options={
                'ordering': ['-connected_user_count'],
            },
        ),
    ]
