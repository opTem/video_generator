import os

from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
import requests

load_dotenv()

API_URL = os.getenv("API_URL")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context):
    await update.message.reply_text(
        "Привет! Я бот для генерации видео. Используй /help для списка команд."
    )

async def generate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    theme = " ".join(context.args) if context.args else "наука"
    response = requests.post(f"{API_URL}/generate-text/", json={"theme": theme})
    if response.status_code == 201:
        data = response.json()
        await update.message.reply_text(f"Текст создан! ID: {data['id']} \n\n{data['text']}")
    else:
        await update.message.reply_text(f"Ошибка: {response.text}")


async def generate_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Ошибка: укажите ID видео. Пример: /generate_audio 123")
        return

    video_id = context.args[0]
    response = requests.post(f"{API_URL}/generate-audio/", json={"video_id": video_id})

    if response.status_code == 201:
        data = response.json()
        audio_url = data.get("audio_url")
        print(f"Ссылка на аудио: {audio_url}")

        if audio_url.startswith("http"):  # Убеждаемся, что URL полный
            # Скачиваем аудиофайл
            audio_file = requests.get(audio_url).content
            with open("temp_audio.mp3", "wb") as file:
                file.write(audio_file)

            # Отправляем аудио в Telegram
            await update.message.reply_audio(audio=open("temp_audio.mp3", "rb"), caption="🎙 Готовая озвучка!")

            # Удаляем временный файл
            os.remove("temp_audio.mp3")
        else:
            await update.message.reply_text("Ошибка: получен некорректный URL для аудиофайла.")
    else:
        await update.message.reply_text(f"Ошибка: {response.text}")

async def generate_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_id = context.args[0]
    response = requests.post(f"{API_URL}/generate-image/", json={"video_id": video_id})
    if response.status_code == 201:
        await update.message.reply_text("Изображения успешно созданы!")
    else:
        await update.message.reply_text(f"Ошибка: {response.text}")

async def generate_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_id = context.args[0]
    response = requests.post(f"{API_URL}/generate-video/", json={"video_id": video_id})
    if response.status_code == 201:
        video_url = response.json()["video_url"]
        await update.message.reply_text(f"Видео готово: {video_url}")
    else:
        await update.message.reply_text(f"Ошибка: {response.text}")

async def generate_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос на генерацию музыки для видео"""
    if not context.args:
        await update.message.reply_text("Укажи ID видео для музыки!")
        return

    video_id = context.args[0]

    response = requests.post(f"{API_URL}/generate_music/", json={"video_id": video_id})

    if response.status_code == 201:
        music_url = response.json().get("music_url", "URL не найден")
        await update.message.reply_text(f"Музыка создана! 🎵\n{music_url}")
    else:
        await update.message.reply_text(f"Ошибка генерации музыки: {response.text}")

async def publish_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_id = context.args[0]
    print(API_URL)
    response = requests.get(f"{API_URL}/videos/{video_id}/")

    if response.status_code == 200:
        video_url = response.json()["final_video_url"]

        # Скачиваем видео на сервер и отправляем файлом
        video_file = requests.get(video_url).content
        with open("temp_video.mp4", "wb") as file:
            file.write(video_file)

        await update.message.reply_video(video=open("temp_video.mp4", "rb"))
        os.remove("temp_video.mp4")
    else:
        await update.message.reply_text(f"Ошибка: {response.text}")



async def publish_youtube(update, context):
    if not context.args:
        await update.message.reply_text("Укажи ID видео для публикации!")
        return

    video_id = context.args[0]

    response = requests.post(
        "http://127.0.0.1:8000/api/publish-youtube/",
        json={"video_id": video_id}
    )

    if response.status_code == 201:
        await update.message.reply_text("✅ Видео опубликовано на YouTube!")
    else:
        await update.message.reply_text(f"Ошибка публикации: {response.text}")

async def publish_tiktok(update, context):
    if not context.args:
        await update.message.reply_text("Укажи ID видео для публикации!")
        return

    video_id = context.args[0]

    response = requests.post(
        "http://127.0.0.1:8000/api/publish-tiktok/",
        json={"video_id": video_id}
    )

    if response.status_code == 200:
        await update.message.reply_text("✅ Видео опубликовано на TikTok!")
    else:
        await update.message.reply_text(f"Ошибка публикации: {response.text}")

async def help_command(update: Update, context):
    help_text = """
    📌 Доступные команды:

    🔹 /generate_text - Создать текст
    🔹 /generate_audio - Сгенерировать озвучку
    🔹 /generate_image - Сгенерировать изображения
    🔹 /generate_music - Создать музыку
    🔹 /generate_video - Собрать видео
    🔹 /publish - Опубликовать видео
    🔹 /publish_youtube - Загрузить на YouTube
    🔹 /publish_tiktok - Загрузить в TikTok
    """
    await update.message.reply_text(help_text)
application = ApplicationBuilder().token(TOKEN).build()

# Команды
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("generate_text", generate_text))
application.add_handler(CommandHandler("generate_audio", generate_audio))
application.add_handler(CommandHandler("generate_image", generate_images))
application.add_handler(CommandHandler("generate_video", generate_video))
application.add_handler(CommandHandler("generate_music", generate_music))
application.add_handler(CommandHandler("publish", publish_video))
application.add_handler(CommandHandler("publish_youtube", publish_youtube))
application.add_handler(CommandHandler("publish_tiktok", publish_tiktok))

# Добавляем меню команд в Telegram
async def set_bot_commands():
    commands = [
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Список команд"),
        BotCommand("generate_text", "Создать текст"),
        BotCommand("generate_audio", "Создать озвучку"),
        BotCommand("generate_image", "Создать изображения"),
        BotCommand("generate_video", "Собрать видео"),
        BotCommand("generate_music", "Создать музыку"),
        BotCommand("publish", "Опубликовать видео"),
        BotCommand("publish_youtube", "Загрузить на YouTube"),
        BotCommand("publish_tiktok", "Загрузить в TikTok"),
    ]
    bot = application.bot
    await bot.set_my_commands(commands)

if __name__ == "__main__":
    application.run_polling()
    application.loop.run_until_complete(set_bot_commands())

