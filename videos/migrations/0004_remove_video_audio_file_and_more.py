# Generated by Django 5.1.6 on 2025-02-28 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0003_alter_video_theme'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='audio_file',
        ),
        migrations.RemoveField(
            model_name='video',
            name='background_image_1',
        ),
        migrations.RemoveField(
            model_name='video',
            name='background_image_2',
        ),
        migrations.RemoveField(
            model_name='video',
            name='background_image_3',
        ),
        migrations.RemoveField(
            model_name='video',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='video',
            name='final_video',
        ),
        migrations.RemoveField(
            model_name='video',
            name='text',
        ),
        migrations.RemoveField(
            model_name='video',
            name='theme',
        ),
        migrations.RemoveField(
            model_name='video',
            name='voice',
        ),
    ]
