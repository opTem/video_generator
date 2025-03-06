import pickle
import time
import re
import os

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

COOKIES_FILE = "cookies.pkl"


def load_cookies(driver, file_path):
    """Загружаем сохраненные куки"""
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("✅ Куки загружены!")

def upload_video_to_tiktok(video_path, title, description):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://www.tiktok.com/tiktokstudio/upload?from=webapp&lang=ru-RU")
        time.sleep(5)

        # Загружаем куки
        load_cookies(driver, COOKIES_FILE)
        driver.refresh()
        time.sleep(5)

        if "login" in driver.current_url:
            print("❌ Ошибка: требуется повторный вход в TikTok!")
            return "Ошибка авторизации"

        print("✅ Успешная авторизация!")

        # Загружаем видео
        try:
            upload_input = driver.find_element(By.XPATH, '//input[@type="file" and @accept="video/*"]')
            upload_input.send_keys(video_path)
            print("📤 Видео загружается...")
        except NoSuchElementException:
            print("❌ Ошибка: не найдено поле загрузки видео!")
            return "Ошибка загрузки видео"

        time.sleep(10)  # Даем время для загрузки

        # Заполняем описание
        try:

            description_box = driver.find_element(By.XPATH, '//div[@contenteditable="true" and @role="textbox"]')
            description_box.click()
            time.sleep(2)

            sanitized_description = sanitize_text(description)
            print(f"🔍 Оригинальный текст: {description}")
            print(f"✅ Очищенный текст: {sanitized_description}")

            driver.execute_script("arguments[0].innerText = '';", description_box)
            time.sleep(2)
            # description_box.send_keys(Keys.CONTROL + "a")
            # time.sleep(1)
            # description_box.send_keys(Keys.DELETE)
            # time.sleep(1)
            description_box.send_keys(sanitized_description)
            print("📝 Описание введено")
        except NoSuchElementException:
            print("❌ Ошибка: поле описания не найдено!")
            return "Ошибка ввода описания"

        # Прокручиваем страницу вниз перед раскрытием настроек
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)

        # Разворачиваем настройки
        try:
            show_more_button = driver.find_element(By.XPATH, '//div[@data-e2e="advanced_settings_container"]//span[contains(text(), "Show more")]')
            show_more_button.click()
            time.sleep(2)
        except NoSuchElementException:
            print("⚠ Настройки уже развернуты или кнопка не найдена")

        # Активируем нужный чекбокс
        try:
            ai_content_switch = driver.find_element(By.XPATH,
                                                    '//div[@data-e2e="aigc_container"]//div[contains(@class, "Switch__root") and @data-layout="switch-root"]')
            driver.execute_script("arguments[0].scrollIntoView();", ai_content_switch)
            time.sleep(1)
            ai_content_switch.click()
            print("✅ Чекбокс 'AI-generated content' активирован!")
            time.sleep(2)

            # Проверяем, появилось ли всплывающее окно с кнопкой "Turn on"
            try:
                turn_on_button = driver.find_element(By.XPATH, '//button[contains(@class, "Button__root") and contains(., "Turn on")]')
                turn_on_button.click()
                print("✅ Активировали чекбокс через всплывающее окно!")
            except NoSuchElementException:
                print("⚠ Кнопка подтверждения не появилась, возможно, чекбокс уже был активирован.")

        except NoSuchElementException:
            print("❌ Ошибка: не найден нужный чекбокс!")
            return "Ошибка активации чекбокса"

        time.sleep(3)

        # Ожидание перед публикацией
        input("⏳ Проверь все поля и нажми Enter, чтобы опубликовать...")

        # Нажимаем кнопку публикации
        try:
            publish_button = driver.find_element(By.XPATH, '//button[@data-e2e="post_video_button"]')
            driver.execute_script("arguments[0].scrollIntoView();", publish_button)
            time.sleep(1)
            publish_button.click()
            print("🚀 Видео загружено на TikTok!")
        except NoSuchElementException:
            print("❌ Ошибка: кнопка публикации не найдена!")
            return "Ошибка публикации видео"

        time.sleep(10)

    finally:
        driver.quit()

    return "✅ Видео загружено успешно!"


def sanitize_text(text, max_length=600):
    """
    Удаляет все неподдерживаемые символы (не входящие в Basic Multilingual Plane).
    Обрезает текст до max_length символов, если TikTok ограничивает длину описания.
    """
    if not isinstance(text, str):
        return text  # Если передан не текст, просто вернуть его

    cleaned_text = re.sub(r'[^\u0000-\uFFFF]', '', text)  # Удаляем всё, что выше U+FFFF (BMP)

    return cleaned_text[:max_length]  # Ограничиваем длину (если надо)
