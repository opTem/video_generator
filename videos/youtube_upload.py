# videos/youtube_upload.py
import os
import re
import json

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "token.json"

def youtube_authenticate():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080)
    youtube = build("youtube", "v3", credentials=credentials)
    return youtube

# def youtube_authenticate():
#     creds = None
#
#     # Загружаем сохранённый токен
#     if os.path.exists(TOKEN_FILE):
#         with open(TOKEN_FILE, "r") as token_file:
#             creds = Credentials.from_authorized_user_info(json.load(token_file), SCOPES)
#
#     # Если токена нет или он просрочен — авторизуемся заново
#     if not creds or not creds.valid:
#         flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
#         creds = flow.run_local_server(port=8080)
#
#         # Сохраняем новый токен в файл
#         with open(TOKEN_FILE, "w") as token_file:
#             token_file.write(creds.to_json())
#
#     return build("youtube", "v3", credentials=creds)
# def extract_hashtags(text):
#     """ Извлекает хештеги из текста """
#     return re.findall(r"#\w+", text)
def upload_video(youtube, video_path, title, description):
    print("Исходное описание:", description)  # Отладка

    # Оставляем описание нетронутым (включая хештеги)
    clean_description = description.strip()

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": clean_description,  # Описание без изменений
                "categoryId": "22"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload(video_path)
    )
    response = request.execute()
    return response
