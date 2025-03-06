## **AI Video Generator Bot**
🎥 **AI Video Generator Bot** – Telegram-бот и Django-сервис для автоматической генерации научных видео. Использует OpenAI, DALL·E, ElevenLabs, Suno API и MoviePy для создания контента.

---

### **📌 Возможности**
- 🔹 Генерация текста с интересными фактами с помощью OpenAI GPT-4o  
- 🎙 Генерация озвучки с ElevenLabs и OpenAI  
- 🖼 Создание изображений с DALL·E  
- 🎵 Генерация музыки через Suno API  
- 🎞 Автоматическая сборка видео (MoviePy)  
- 📤 Публикация видео в YouTube и TikTok  

---

### **🚀 Установка и настройка**
#### **1️⃣ Клонирование репозитория**
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

#### **2️⃣ Установка зависимостей**
Создаём виртуальное окружение и устанавливаем зависимости:
```bash
python3 -m venv venv
source venv/bin/activate  # Для Linux/macOS
venv\Scripts\activate  # Для Windows

pip install -r requirements.txt
```

#### **3️⃣ Настройка переменных окружения**
Создай файл `.env` в корне проекта и добавь в него API-ключи:

```plaintext
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Eleven Labs API
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Google Cloud Credentials (файл JSON)
GOOGLE_APPLICATION_CREDENTIALS=service-account-file.json

# Suno API
SUNO_API_KEY=your_suno_api_key
SUNO_COOKIE=your_suno_cookie
SUNO_API_URL=https://apibox.erweima.ai/api/v1/generate
CHECK_STATUS_URL=https://apibox.erweima.ai/api/v1/generate/record-info

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# API URL
API_URL=http://127.0.0.1:8000/api
```

Не забудь добавить `.env` в `.gitignore`, чтобы не загрузить ключи в репозиторий.

#### **4️⃣ Запуск Django-сервера**
Выполни миграции и запусти сервер:
```bash
python manage.py migrate
python manage.py runserver
```

#### **5️⃣ Запуск Telegram-бота**
```bash
python bot.py
```

---

### **📜 Доступные команды в боте**
| Команда             | Описание                                    |
|---------------------|--------------------------------------------|
| `/start`           | Начало работы с ботом                      |
| `/help`            | Список команд                              |
| `/generate_text`   | Генерация текста                          |
| `/generate_audio`  | Создание озвучки                          |
| `/generate_image`  | Генерация изображений                     |
| `/generate_video`  | Сборка финального видео                    |
| `/generate_music`  | Создание музыки                           |
| `/publish`         | Получение финального видео                 |
| `/publish_youtube` | Публикация видео на YouTube               |
| `/publish_tiktok`  | Публикация видео в TikTok                 |

---

### **🛠 Основные технологии**
- **Backend:** Django, DRF  
- **AI & ML:** OpenAI API (GPT-4o, DALL·E, Whisper), ElevenLabs  
- **Видео:** MoviePy, ffmpeg  
- **Базы данных:** PostgreSQL / SQLite  
- **Автоматизация публикаций:** Selenium, YouTube API, TikTok Web  

---

### **📌 To-Do**
✅ Генерация текста  
✅ Создание озвучки и фоновой музыки  
✅ Генерация изображений  
✅ Сборка видео с субтитрами  
✅ Публикация на YouTube  
🔜 Интеграция с Shorts
🔜 Оптимизация видео для TikTok  

---



