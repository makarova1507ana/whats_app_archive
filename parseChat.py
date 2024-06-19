import re
import json
import zipfile
import os
# Регулярные выражения для разбора шаблонов сообщений и файлов
message_pattern = r'^(\d{2}\.\d{2}.\d{4}, \d{2}:\d{2}) - ([^:]+): (.*)$'
file_pattern = r'^(\d{2}\.\d{2}.\d{4}, \d{2}:\d{2}) - ([^:]+): ‎([^()]+)\.jpg \(файл добавлен\)$'

ALLOWED_EXTENSIONS = {'zip'}


UPLOAD_FOLDER = 'uploads'


# Функция для проверки, имеет ли файл разрешенное расширение
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Функция для сохранения разобранных сообщений в файл JSON
def save_messages(folder, messages):
    with open(os.path.join(folder, 'messages.json'), 'w', encoding='utf-8') as json_file:
        json.dump(messages, json_file, ensure_ascii=False, indent=4)

# Функция для извлечения сообщений из zip-архива и их разбора
def extract_messages_from_archive(archive_path, extract_folder):
    extracted_messages = []

    # Извлечение zip-архива
    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

        # Обход извлеченных файлов и разбор каждого файла .txt
        for root, _, files in os.walk(extract_folder):
            for file in files:
                if file.endswith('.txt'):
                    try:
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            for line in lines:
                                line = line.strip()
                                if line:
                                    message_match = re.match(message_pattern, line)
                                    file_match = re.match(file_pattern, line)
                                    if message_match:
                                        timestamp = message_match.group(1)
                                        sender = message_match.group(2)
                                        content = message_match.group(3)
                                        extracted_messages.append({
                                            'id': len(extracted_messages) + 1,
                                            'timestamp': timestamp,
                                            'sender': sender,
                                            'content': content,
                                            'deleted': False
                                        })
                                    elif file_match:
                                        timestamp = file_match.group(1)
                                        sender = file_match.group(2)
                                        file_name = file_match.group(3)
                                        extracted_messages.append({
                                            'id': len(extracted_messages) + 1,
                                            'timestamp': timestamp,
                                            'sender': sender,
                                            'content': file_name,
                                            'deleted': False
                                        })
                    except FileNotFoundError as e:
                        print(f"Файл не найден: {e}")
                    except Exception as e:
                        print(f"Произошла ошибка при обработке файла {file}: {e}")

    return extracted_messages

# Функция для загрузки сообщений из файла JSON
def load_messages(folder):
    messages_file = os.path.join(folder, 'messages.json')
    if os.path.exists(messages_file):
        try:
            with open(messages_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                if isinstance(messages, list):
                    for message in messages:
                        if not isinstance(message, dict) or not all(
                                key in message for key in ['id', 'timestamp', 'sender', 'content', 'deleted']):
                            raise ValueError('Неверный формат сообщения в JSON-файле.')
                else:
                    raise ValueError('Файл сообщений не является списком.')
                return messages
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Ошибка загрузки сообщений: {e}")
    return []
