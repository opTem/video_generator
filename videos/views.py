import base64
import time
import os
import json
import random
from io import BytesIO

import numpy as np
import requests

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_201_CREATED, \
    HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip, \
    concatenate_audioclips, VideoClip
from openai import OpenAI
from .youtube_upload import youtube_authenticate, upload_video


from django.core.files.base import ContentFile
from .models import Video
import moviepy.config as mpy_config

from .selenium_upload import upload_video_to_tiktok

mpy_config.FFMPEG_BINARY = "/usr/bin/ffmpeg"





# Загружаем переменные из .env
load_dotenv()

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Eleven Labs API
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Google Cloud Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Suno API
SUNO_COOKIE = os.getenv("SUNO_COOKIE")
SUNO_API_KEY = os.getenv("SUNO_API_KEY")
SUNO_API_URL = os.getenv("SUNO_API_URL")
CHECK_STATUS_URL = os.getenv("CHECK_STATUS_URL")

class GenerateTextAPIView(APIView):
    def post(self, request):
        theme = request.data.get('theme', 'наука')

        prompt = f"""
                Придумай интересный научный факт, длина которого не менее 5000 знаков (включая пробелы) по теме {theme}. 
                Разбей его на 5 смысловые частей так, чтобы каждая часть содержала примерно 600 знаков и была понятна отдельно. 
                Используй подробные объяснения, примеры и интересные сравнения, чтобы сделать текст увлекательным.

                Для каждой части напиши отдельный промт для генерации изображения в DALL·E.

                Также предложи описание для музыки, которая хорошо подходит к этому факту.


                ⚡️ Формат ответа (отвечай ТОЛЬКО JSON, без пояснений и лишних слов):
                {{
                    "text": "Полный научный факт (5500 знаков, 5 части)",
                    "frames": [
                        {{"text": "Первая часть (примерно 1000 знаков)", "image_prompt": "Описание первой картинки"}} ,
                        {{"text": "Вторая часть (примерно 1000 знаков)", "image_prompt": "Описание второй картинки"}} ,
                        {{"text": "Третья часть (примерно 1000 знаков)", "image_prompt": "Описание третьей картинки"}}
                        {{"text": "Четвертая часть (примерно 1000 знаков)", "image_prompt": "Описание четвертой картинки"}}
                        {{"text": "Пятая часть (примерно 1000 знаков)", "image_prompt": "Описание пятой картинки"}}
                    ],
                    "music_prompt": "Описание музыки",
                    "tiktok_description": "Текст для TikTok с хештегами",
                }}
                Отвечай ТОЛЬКО JSON, без лишних слов.
                """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}],
        )
        print(response.choices[0].message.content)
        gpt_data = json.loads(response.choices[0].message.content)

        video = Video.objects.create(
            theme=theme,
            text=gpt_data["text"],
            frame_1_text=gpt_data["frames"][0]["text"],
            frame_2_text=gpt_data["frames"][1]["text"],
            frame_3_text=gpt_data["frames"][2]["text"],
            frame_4_text=gpt_data["frames"][3]["text"],
            frame_5_text=gpt_data["frames"][4]["text"],
            frame_1_prompt=gpt_data["frames"][0]["image_prompt"],
            frame_2_prompt=gpt_data["frames"][1]["image_prompt"],
            frame_3_prompt=gpt_data["frames"][2]["image_prompt"],
            frame_4_prompt=gpt_data["frames"][3]["image_prompt"],
            frame_5_prompt=gpt_data["frames"][4]["image_prompt"],
            music_prompt=gpt_data["music_prompt"],
            tiktok_description=gpt_data["tiktok_description"]
        )

        return Response({
            "text": gpt_data["text"],
            "id": video.id,
            "frames": gpt_data["frames"],
            "music_prompt": gpt_data["music_prompt"],
            "tiktok_description": gpt_data["tiktok_description"]
        }, status=status.HTTP_201_CREATED)


class GenerateMusicAPIView(APIView):
    def post(self, request):
        print("📥 Получен запрос на генерацию музыки")
        video_id = request.data.get("video_id")

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            print("❌ Видео не найдено")
            return Response({"error": "Видео не найдено"}, status=HTTP_404_NOT_FOUND)

        if not video.music_prompt:
            print("❌ Нет промта для музыки")
            return Response({"error": "Нет промта для музыки"}, status=HTTP_400_BAD_REQUEST)

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": video.music_prompt,
            "style": "Orchestral",
            "title": f"Generated Music for Video {video.id}",
            "customMode": True,
            "instrumental": True,
            "model": "V4",
            "callBackUrl": "https://your-backend.com/api/music_callback/"
        }

        # Отправляем запрос на генерацию
        response = requests.post(SUNO_API_URL, json=payload, headers=headers)

        print(f"📡 Статус ответа: {response.status_code}")
        result = response.json()
        print(f"📡 Полный ответ от API: {result}")

        if response.status_code != 200 or result.get("code") != 200:
            print(f"❌ Ошибка API: {response.text}")
            return Response({"error": "Ошибка генерации музыки"}, status=HTTP_500_INTERNAL_SERVER_ERROR)

        task_id = result["data"]["taskId"]
        print(f"✅ Музыка генерируется, taskId: {task_id}")

        # Мониторинг статуса генерации (максимум 5 минут = 30 запросов с интервалом 10 сек)
        music_url = None
        for _ in range(30):
            time.sleep(10)  # Ждем 10 секунд перед повторным запросом

            check_response = requests.get(CHECK_STATUS_URL, headers=headers, params={"taskId": task_id})
            try:
                status_result = check_response.json()
            except Exception as e:
                print("Ошибка при декодировании JSON:", e)
                print("Ответ:", check_response.text)
                return Response({"error": "Ошибка при получении статуса"}, status=HTTP_500_INTERNAL_SERVER_ERROR)

            print(f"📡 Статус ответа: {check_response.status_code}")
            print(f"📡 Ответ от API: {status_result}")

            if check_response.status_code == 200 and status_result.get("msg") == "success":
                task_info = status_result.get("data", {})
                status = task_info.get("status")
                print(f"Текущий статус задачи: {status}")

                if status == "SUCCESS":
                    suno_data = task_info.get("response", {}).get("sunoData", [])

                    if suno_data:
                        first_track = suno_data[0]
                        music_url = first_track.get("audioUrl")
                        if music_url:
                            print(f"🎵 Музыка готова! Скачивай отсюда: {music_url}")
                            break
                        else:
                            print("⚠️ Генерация завершена, но URL аудио не найден.")
                    else:
                        print("⚠️ Не найдены данные о сгенерированной музыке.")
            else:
                print("⏳ Генерация ещё не завершена, ждем 10 секунд...")

        if not music_url:
            print("❌ Музыка не была сгенерирована за 5 минут")
            return Response({"error": "Музыка не была сгенерирована за 5 минут"}, status=HTTP_500_INTERNAL_SERVER_ERROR)

        # Скачиваем музыку
        music_path = f"music_{video.id}.mp3"
        print("📥 Скачиваем сгенерированную музыку...")
        music_response = requests.get(music_url)

        if music_response.status_code == 200:
            with open(music_path, "wb") as f:
                f.write(music_response.content)
            print("✅ Музыка загружена и сохранена локально")
        else:
            print("❌ Ошибка загрузки музыки")
            return Response({"error": "Ошибка загрузки музыки"}, status=HTTP_500_INTERNAL_SERVER_ERROR)

        # Сохраняем музыку в Django
        with open(music_path, "rb") as music_file:
            video.music_file.save(f"music_{video.id}.mp3", ContentFile(music_file.read()))
        print("✅ Музыка сохранена в модели Video")

        os.remove(music_path)  # Удаляем временный файл
        print("🗑 Временный файл удален")

        return Response({
            "message": "Музыка сгенерирована!",
            "music_url": video.music_file.url
        }, status=HTTP_201_CREATED)



class GenerateAudioAPIView(APIView):
    def post(self, request, *args, **kwargs):
        video_id = request.data.get("video_id")
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Видео не найдено"}, status=404)

        # Выбираем текст для озвучки
        # input_text = video.ssml_text if video.ssml_text else video.text
        input_text = video.text

        # Выбираем модель (tts-1 или tts-1-hd)
        model = "tts-1-hd"  # Можно заменить на "tts-1-hd" для более качественной озвучки

        # Запрос к OpenAI TTS
        response = client.audio.speech.create(
            model=model,
            voice="shimmer",  # Или попробуй "fable" Другие варианты: "echo", "fable", "onyx", "nova", "shimmer"
            input=input_text,
            speed=1.5
        )

        # Читаем бинарные данные аудио
        audio_bytes = response.read()

        # Сохраняем аудио в Django
        audio_file = ContentFile(audio_bytes, name=f"audio_{video.id}.mp3")
        video.audio_file.save(audio_file.name, audio_file)

        # Полный URL файла
        audio_full_url = request.build_absolute_uri(video.audio_file.url)
        print(audio_full_url)

        return Response({"message": "Озвучка создана!", "audio_url": audio_full_url}, status=201)


class GenerateImagesAPIView(APIView):
    def post(self, request):
        video_id = request.data.get("video_id")
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Видео не найдено"}, status=404)

        image_prompts = [
            video.frame_1_prompt,
            video.frame_2_prompt,
            video.frame_3_prompt,
            video.frame_4_prompt,
            video.frame_5_prompt
        ]

        image_urls = []
        for i, prompt in enumerate(image_prompts):
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                response_format="b64_json"
            )

            image_data = base64.b64decode(response.data[0].b64_json)
            image_file = ContentFile(image_data, name=f"background_{video.id}_{i + 1}.png")

            field_name = f"background_image_{i + 1}"
            getattr(video, field_name).save(image_file.name, image_file)
            image_urls.append(getattr(video, field_name).url)

        video.save()

        return Response({"message": "Фоны сгенерированы!", "image_urls": image_urls}, status=201)



class GenerateFinalVideoAPIView(APIView):
    def post(self, request):
        video_id = request.data.get("video_id")

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Видео не найдено"}, status=404)

        background_images = [
            video.background_image_1,
            video.background_image_2,
            video.background_image_3,
            video.background_image_4,
            video.background_image_5
        ]

        if len(background_images) < 5 or not video.audio_file:
            return Response({"error": "Не хватает изображений или голосового аудио"}, status=400)

        voice_audio = AudioFileClip(video.audio_file.path)
        audio_duration = voice_audio.duration

        image_duration = audio_duration / len(background_images)
        image_clips = [
            ImageClip(img.path).with_duration(image_duration) for img in background_images
        ]

        intro_clip = ImageClip(background_images[0].path).with_duration(1)
        all_clips = [intro_clip] + image_clips

        background_clip = concatenate_videoclips(all_clips, method="compose").with_audio(voice_audio)

        # Whisper API для распознавания речи и создания субтитров
        with open(video.audio_file.path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )

        words_with_timings = transcript.words
        subtitles_offset = 1  # Двигаем текст немного вперед
        txt_clips = []

        for word in words_with_timings:
            start_time = max(0, word.start + subtitles_offset)  # Избегаем отрицательных значений
            word_duration = max(0.2, word.end - word.start)  # Минимальная длительность
            position = ('center', 'center')  # Размещаем субтитры внизу экрана

            txt_clips.append(generate_subtitle_text(
                word.word, start_time, word_duration, position,
                font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            ))

        # Добавляем субтитры в финальный видеоклип
        final_clip = CompositeVideoClip([background_clip] + txt_clips)

        output_filename = f"final_{video.id}.mp4"
        output_path = os.path.join("media/videos/", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        final_clip.write_videofile(
            output_path,
            fps=60,
            codec='libx264',
            audio_codec="aac",
            ffmpeg_params=['-preset', 'slow', '-crf', '18', '-b:v', '10M', '-pix_fmt', 'yuv720p'],
            threads=6
        )

        video.final_video = output_path
        video.save()

        return Response(
            {
                "message": "Видео собрано автоматически!",
                "video_url": video.final_video.url
            },
            status=201
        )


def gradual_fade_mask(width, height, duration):
    def make_frame(t):
        alpha = np.clip(t / duration, 0, 1)  # Значения от 0 до 1
        mask = np.ones((height, width, 1), dtype=np.float32) * alpha  # 3D маска с альфа-каналом
        return mask

    return VideoClip(make_frame, duration=duration).to_mask()


def generate_subtitle_text(word, start_time, duration, position, font_path, font_size=50):
    """
    Создаёт обычный белый текст без караоке-эффекта.
    """

    txt_white = TextClip(
        text=word,
        font=font_path,
        font_size=font_size,
        color="white",
        stroke_color="black",
        stroke_width=3
    ).with_start(start_time).with_duration(duration).with_position(position)

    return txt_white


def group_words(words_with_timings, group_size=3):
    grouped = []
    for i in range(0, len(words_with_timings), group_size):
        chunk = words_with_timings[i:i+group_size]
        text = " ".join([w.word for w in chunk])
        start = chunk[0].start
        end = chunk[-1].end
        grouped.append({"text": text, "start": start, "end": end})
    return grouped


class PublishToYoutubeAPIView(APIView):
    def post(self, request):
        video_id = request.data.get("video_id")

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Видео не найдено"}, status=404)

        youtube = youtube_authenticate()

        video_path = video.final_video.path.replace('/media/media/', '/media/')
        # video_path = video.final_video.path
        title = f"Научное видео на тему {video.theme}"
        description = video.tiktok_description
        # tags = [video.theme, "наука", "shorts"]

        response = upload_video(youtube, video_path, title, description)

        return Response({
            "message": "Видео собрано автоматически с караоке-эффектом!",
            "video_url": video.final_video.url.replace('/media/', '')
        }, status=201)


class PublishToTikTokAPIView(APIView):
    def post(self, request):
        video_id = request.data.get("video_id")

        if not video_id:
            return Response({"error": "video_id не передан"}, status=400)

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Видео не найдено"}, status=404)

        video_path = video.final_video.path.replace('/media/media/', '/media/')  # Путь к видео
        title = f"Научное видео на тему {video.theme}"  # Название видео
        description = video.tiktok_description  # Описание видео
        tags = [video.theme, "наука", "shorts"]  # Теги для видео

        try:
            print(f"Запуск upload_video_to_tiktok с параметрами:\nvideo_path={video_path}\ntitle={title}\ndescription={description}")
            result = upload_video_to_tiktok(video_path, title, description)
            return Response({"message": result}, status=200)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Ошибка в upload_video_to_tiktok:\n{error_details}")
            return Response({"error": str(e), "trace": error_details}, status=500)





class GetFinalVideoAPIView(APIView):
    def get(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)

        if video.final_video:
            # Убираем лишнее "media/media/" из пути
            video_url = request.build_absolute_uri(video.final_video.url.replace('/media/media/', '/media/'))
            return JsonResponse({"final_video_url": video_url}, status=200)
        else:
            return JsonResponse({"error": "Финальное видео не найдено."}, status=404)


class MusicCallbackAPIView(APIView):
    def post(self, request):
        print("📥 Получен callback от Suno API")
        data = request.data
        print(f"📡 Данные callback: {data}")

        music_url = data.get("music_url")
        video_id = data.get("video_id")

        if not music_url or not video_id:
            print("❌ Некорректный callback-ответ")
            return Response({"error": "Некорректный callback"}, status=400)

        try:
            video = Video.objects.get(id=video_id)
            video.music_file.save(f"music_{video.id}.mp3", ContentFile(requests.get(music_url).content))
            video.save()
            print("✅ Музыка сохранена в модели Video")
        except Video.DoesNotExist:
            print("❌ Видео не найдено")
            return Response({"error": "Видео не найдено"}, status=404)

        return Response({"message": "Музыка успешно сохранена"}, status=200)




