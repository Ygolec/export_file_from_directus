import requests
import re
import urllib.parse

# Данные для аутентификации
login_url = "http://localhost/auth/login"
user_email = ""  # Замените на ваш email
user_password = ""  # Замените на ваш пароль

# Список идентификаторов файлов
file_ids = [
    "dfeb4cf4-708b-46e3-9eca-8bc526517685",


]

# Основная часть URL для скачивания файлов
base_url = "http://localhost/assets/{}?download"

# Создаем сессию
session = requests.Session()

# Подробные заголовки для имитации браузера
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Данные для авторизации
login_data = {
    "email": user_email,
    "password": user_password,
    "mode": "session"  # Используем 'session' для получения сессионных куки
}

# Авторизация
response = session.post(login_url, json=login_data, headers=headers)

# Проверка успешности авторизации
if response.status_code == 200:
    print("Успешная авторизация. Используем сессионные куки для последующих запросов.")
else:
    print(f"Ошибка при авторизации. Статус: {response.status_code}")
    exit()


# Функция для извлечения и очистки имени файла
def get_clean_filename(content_disposition, fallback_name="file.bin"):
    import re
    import urllib.parse

    filename = None

    # Пытаемся найти параметр filename* (RFC 5987)
    filename_star_match = re.search(r'filename\*\s*=\s*(?:([\w-]+)\'[\w-]*\')?([^;\r\n]+)', content_disposition, flags=re.IGNORECASE)
    if filename_star_match:
        encoding = filename_star_match.group(1) or 'utf-8'
        encoded_filename = filename_star_match.group(2)
        # Декодируем имя файла
        try:
            filename = urllib.parse.unquote(encoded_filename, encoding=encoding)
        except LookupError:
            # Если кодировка неизвестна, используем utf-8
            filename = urllib.parse.unquote(encoded_filename, encoding='utf-8')
    else:
        # Пытаемся найти параметр filename
        filename_match = re.search(r'filename\s*=\s*"?(?P<filename>[^";\r\n]+)"?', content_disposition, flags=re.IGNORECASE)
        if filename_match:
            filename = filename_match.group('filename')
            # Попытка декодирования, если имя файла закодировано
            try:
                filename = urllib.parse.unquote(filename)
            except Exception:
                pass

    if filename:
        # Очищаем имя файла от недопустимых символов
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return filename
    else:
        return fallback_name




# Функция для скачивания файла с сохранением оригинального имени
def download_file(file_id):
    url = base_url.format(file_id)
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        # Получение и очистка имени файла
        content_disposition = response.headers.get("Content-Disposition", "")
        print(f"Content-Disposition для {file_id}: {content_disposition}")
        filename = get_clean_filename(content_disposition, fallback_name=f"{file_id}.bin")

        # Сохранение файла с исходным именем
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Файл {filename} успешно загружен.")
    else:
        print(f"Не удалось скачать файл {file_id}. Статус: {response.status_code}")





# Цикл для скачивания всех файлов из списка
for file_id in file_ids:
    try:
        download_file(file_id)
    except Exception as e:
        print(f"Ошибка при скачивании файла {file_id}: {e}")

