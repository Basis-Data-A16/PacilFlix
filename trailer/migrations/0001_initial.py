# Generated by Django 5.0.4 on 2024-05-02 13:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Film',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('synopsis', models.TextField()),
                ('trailer_url', models.URLField()),
                ('release_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('synopsis', models.TextField()),
                ('trailer_url', models.URLField()),
                ('release_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Trailer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ranking', models.IntegerField()),
                ('title', models.CharField(max_length=100)),
                ('synopsis', models.TextField()),
                ('trailer_url', models.URLField()),
                ('release_date', models.DateField()),
                ('total_views_last_7_days', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('subtitle', models.CharField(max_length=100)),
                ('synopsis', models.TextField()),
                ('duration', models.DurationField()),
                ('release_date', models.DateField()),
                ('video_url', models.URLField()),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='episodes', to='trailer.series')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('trailer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='trailer.trailer')),
            ],
        ),
    ]
