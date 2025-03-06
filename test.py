import requests
import time

API_KEY = "92db75d68a47d2f7647de9d2817adcba"
TASK_ID = "2615daa4076829d75e1e6ab09b7b2770"
RECORD_INFO_URL = "https://apibox.erweima.ai/api/v1/generate/record-info"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

params = {
    "taskId": TASK_ID
}

while True:
    response = requests.get(RECORD_INFO_URL, headers=headers, params=params)
    try:
        data = response.json()
    except Exception as e:
        print("Ошибка при декодировании JSON:", e)
        print("Ответ:", response.text)
        break

    print(f"📡 Статус ответа: {response.status_code}")
    print(f"📡 Ответ от API: {data}")

    # Используем ключ "msg", а не "message"
    if response.status_code == 200 and data.get("msg") == "success":
        task_info = data.get("data", {})
        status = task_info.get("status")
        print(f"Текущий статус задачи: {status}")

        # Проверяем, что статус равен "SUCCESS"
        if status == "SUCCESS":
            # Аудиоданные находятся в task_info["response"]["sunoData"]
            suno_data = task_info.get("response", {}).get("sunoData", [])
            if suno_data:
                # Выбираем первый вариант (можно обработать оба, если нужно)
                first_track = suno_data[0]
                audio_url = first_track.get("audioUrl")
                if audio_url:
                    print(f"🎵 Музыка готова! Скачивай отсюда: {audio_url}")
                    break
                else:
                    print("⚠️ Генерация завершена, но URL аудио не найден.")
            else:
                print("⚠️ Не найдены данные о сгенерированной музыке.")
        else:
            print("⏳ Генерация ещё не завершена, ждем 5 секунд...")
    else:
        print("⚠️ Ошибка запроса или неверный ответ от API.")

    time.sleep(5)
