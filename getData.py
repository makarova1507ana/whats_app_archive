import os
import re
import shutil
import zipfile
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from models import  *
# Регулярные выражения для разбора шаблонов сообщений и файлов
message_pattern = r'^(\d{2}\.\d{2}.\d{4}, \d{2}:\d{2}) - ([^:]+): (.*)$'
file_pattern = r'^(\d{2}\.\d{2}.\d{4}, \d{2}:\d{2}) - ([^:]+): ‎([^()]+\.(jpg)|(gif)|(png)|(webp)) \(файл добавлен\)$'

ALLOWED_EXTENSIONS = {'zip'}
def extract_senders(file_path):
    """
    Извлекает уникальных отправителей из текстового файла сообщений.

    Аргументы:
    file_path (str): Путь к текстовому файлу.

    Возвращает:
    set: Множество уникальных отправителей.
    """
    senders = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line:
                message_match = re.match(message_pattern, line)
                if message_match:
                    sender = message_match.group(2)
                    senders.add(sender)
                else:
                    file_match = re.match(file_pattern, line)
                    if file_match:
                        sender = file_match.group(2)
                        senders.add(sender)
    return senders

def create_or_update_chat(session, senders):
    """
    Создает новый чат или обновляет существующий на основе списка отправителей.

    Аргументы:
    session (sqlalchemy.orm.session.Session): Сессия SQLAlchemy для работы с базой данных.
    senders (set): Множество отправителей для создания/обновления чата.

    Возвращает:
    Chat: Объект чата (новый или существующий).
    """
    chat_name = ', '.join(sorted(senders))
    try:
        existing_chat = session.query(Chat).filter_by(name=chat_name).one()
        return existing_chat
    except NoResultFound:
        new_chat = Chat(name=chat_name)
        session.add(new_chat)
        session.commit()
        return new_chat

# Функция для проверки, имеет ли файл разрешенное расширение
def allowed_file(filename):
    """
    Проверяет, имеет ли файл разрешенное расширение.

    Аргументы:
    filename (str): Имя файла для проверки.

    Возвращает:
    bool: True, если расширение файла допустимо, иначе False.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import uuid

def generate_unique_filename(filename):
    base, ext = os.path.splitext(filename)
    unique_id = uuid.uuid4().hex[:6]  # Генерируем случайный уникальный идентификатор
    return f"{base}_{unique_id}{ext}"

# Функция для извлечения сообщений из архива и сохранения в базу данных
def extract_messages_from_archive(archive_path):
    """
    Извлекает сообщения и медиафайлы из ZIP-архива и сохраняет их в базу данных.

    Аргументы:
    archive_path (str): Путь к ZIP-архиву.

    Возвращает:
    list: Список извлеченных сообщений и медиафайлов (объекты SQLAlchemy).
    """
    extracted_messages = []
    extracted_media = []

    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        extract_folder = os.path.join(app.config['UPLOAD_FOLDER'], "temp_extract")
        zip_ref.extractall(extract_folder)

        session = db.session()

        for root, _, files in os.walk(extract_folder):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name.endswith('.txt'):
                    try:
                        senders = extract_senders(file_path)  # Извлечение уникальных отправителей
                        chat = create_or_update_chat(session, senders)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            for line in lines:
                                line = line.strip()
                                if line:
                                    message_match = re.match(message_pattern, line)
                                    file_match = re.match(file_pattern, line)
                                    if file_match:
                                        timestamp = file_match.group(1)
                                        sender = file_match.group(2)
                                        file_name = file_match.group(3)
                                        existing_message = session.query(Media).filter_by(
                                            chat_id=chat.id,
                                            timestamp=timestamp,
                                            sender=sender,
                                            filename=file_name
                                        ).first()
                                        if not existing_message:
                                            new_media = Media(
                                                timestamp=timestamp,
                                                sender=sender,
                                                filename=file_name,
                                                chat_id=chat.id
                                            )
                                            extracted_media.append(new_media)
                                    elif message_match:
                                        timestamp = message_match.group(1)
                                        sender = message_match.group(2)
                                        content = message_match.group(3)
                                        existing_message = session.query(Message).filter_by(
                                            chat_id=chat.id,
                                            timestamp=timestamp,
                                            sender=sender,
                                            content=content
                                        ).first()
                                        if not existing_message:
                                            new_message = Message(
                                                timestamp=timestamp,
                                                sender=sender,
                                                content=content,
                                                chat_id=chat.id
                                            )
                                            extracted_messages.append(new_message)

                    except FileNotFoundError as e:
                        print(f"Файл не найден: {e}")
                    except Exception as e:
                        print(f"Произошла ошибка при обработке файла {file_name}: {e}")
                else:
                    # Сохранение медиафайлов
                    media_name = secure_filename(file_name)
                    media_path = os.path.join(app.config['UPLOAD_FOLDER'], "media", media_name)
                    if not os.path.exists(media_path):
                        os.rename(file_path, media_path)
                    else:
                        unique_media_name = generate_unique_filename(media_name)
                        unique_media_path = os.path.join(app.config['UPLOAD_FOLDER'], "media", unique_media_name)
                        os.rename(file_path, unique_media_path)

        try:
            session.add_all(extracted_messages)
            session.add_all(extracted_media)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            print(f"Произошла ошибка при сохранении сообщений: {e}")
        finally:
            session.close()

        # Удаление временной папки после обработки
        shutil.rmtree(extract_folder)

    return extracted_messages
