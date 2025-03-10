# Generated by Django 5.1.6 on 2025-02-28 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0004_remove_video_audio_file_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='audio_file',
            field=models.FileField(blank=True, null=True, upload_to='audio/'),
        ),
        migrations.AddField(
            model_name='video',
            name='background_image_1',
            field=models.ImageField(blank=True, null=True, upload_to='backgrounds/'),
        ),
        migrations.AddField(
            model_name='video',
            name='background_image_2',
            field=models.ImageField(blank=True, null=True, upload_to='backgrounds/'),
        ),
        migrations.AddField(
            model_name='video',
            name='background_image_3',
            field=models.ImageField(blank=True, null=True, upload_to='backgrounds/'),
        ),
        migrations.AddField(
            model_name='video',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='final_video',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
        migrations.AddField(
            model_name='video',
            name='frame_1_prompt',
            field=models.TextField(default='Нет данных'),
        ),
        migrations.AddField(
            model_name='video',
            name='frame_1_text',
            field=models.TextField(default='Нет данных'),
        ),
        migrations.AddField(
            model_name='video',
            name='frame_2_prompt',
            field=models.TextField(default='Нет данных'),
        ),
        migrations.AddField(
            model_name='video',
            name='frame_2_text',
            field=models.TextField(default='Нет данных'),
        ),
        migrations.AddField(
            model_name='video',
            name='frame_3_prompt',
            field=models.TextField(default='Нет данных'),
        ),
        migrations.AddField(
            model_name='video',
            name='frame_3_text',
            field=models.TextField(default='Нет данных'),
        ),
        migrations.AddField(
            model_name='video',
            name='music_file',
            field=models.FileField(blank=True, null=True, upload_to='music/'),
        ),
        migrations.AddField(
            model_name='video',
            name='text',
            field=models.TextField(default='Нет данных'),
        ),
        migrations.AddField(
            model_name='video',
            name='theme',
            field=models.CharField(default='Нет данных', max_length=255),
        ),
    ]
