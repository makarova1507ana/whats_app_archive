

import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

from parseChat import *

app = Flask(__name__)
app.secret_key = 'ваш_секретный_ключ'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER






# Маршрут главной страницы приложения
@app.route('/', methods=['GET', 'POST'])
def index():
    folders = list_chat_folders()

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не выбран')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Файл не выбран')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            extract_folder = os.path.join(app.config['UPLOAD_FOLDER'], os.path.splitext(filename)[0])

            if not os.path.exists(extract_folder):
                os.makedirs(extract_folder)

            existing_messages = load_messages(extract_folder)

            new_messages = extract_messages_from_archive(filepath, extract_folder)

            combined_messages = []
            existing_contents = {msg['content']: msg for msg in existing_messages}

            for msg in new_messages:
                if msg['content'] in existing_contents:
                    existing_msg = existing_contents[msg['content']]
                    msg['deleted'] = existing_msg['deleted']
                combined_messages.append(msg)

            save_messages(extract_folder, combined_messages)

            flash('Файл успешно загружен и обработан')
            return redirect(url_for('index'))

    return render_template('index.html', folders=folders)

# Маршрут просмотра сообщений в чате
@app.route('/chat/<folder>', methods=['GET', 'POST'])
def view_chat(folder):
    messages = load_messages(os.path.join(app.config['UPLOAD_FOLDER'], folder))

    if request.method == 'POST':
        message_id = request.form.get('message_id')
        if message_id:
            for message in messages:
                if message['id'] == int(message_id):
                    message['deleted'] = True
            save_messages(os.path.join(app.config['UPLOAD_FOLDER'], folder), messages)
            flash(f'Сообщение {message_id} удалено')
            return redirect(url_for('view_chat', folder=folder))

    filtered_messages = [msg for msg in messages if not msg['deleted']]

    return render_template('chat.html', current_folder=folder, messages=filtered_messages)

# Функция для получения списка папок чатов
def list_chat_folders():
    folders = []
    for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
        for dir in dirs:
            if os.path.exists(os.path.join(root, dir, 'messages.json')):
                folders.append(dir)
    return folders

# Маршрут для обслуживания загруженных файлов
@app.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], folder), filename)

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
