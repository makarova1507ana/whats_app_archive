from getData  import  *

ALLOWED_EXTENSIONS = {'zip'}
UPLOAD_FOLDER = 'uploads'







# Создание контекста приложения и базы данных
with app.app_context():
    db.create_all()
    print("Database created or already exists.")


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Основной маршрут для отображения главной страницы приложения.

    Поддерживает методы GET и POST. При POST запросе загружает ZIP-архив,
    извлекает из него сообщения и медиафайлы, сохраняет их в базу данных.

    Возвращает:
    str: HTML-страницу с отображением чатов и формой для загрузки файлов.
    """
    chats = Chat.query.all()

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

            new_messages = extract_messages_from_archive(filepath)

            for msg in new_messages:
                db.session.add(msg)

            db.session.commit()

            flash('Файл успешно загружен и обработан')
            return redirect(url_for('index'))

    return render_template('index.html', chats=chats)

@app.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
def view_chat(chat_id):
    """
    Маршрут для просмотра сообщений конкретного чата.

    Аргументы:
    chat_id (int): Идентификатор чата.

    Поддерживает методы GET и POST. При POST запросе удаляет выбранное сообщение.

    Возвращает:
    str: HTML-страницу с сообщениями чата и формой для удаления сообщений.
    """
    chat = Chat.query.get_or_404(chat_id)
    messages = Message.query.filter_by(chat_id=chat.id, deleted=False).all()
    media_files = Media.query.filter_by(chat_id=chat.id).all()

    if request.method == 'POST':
        message_id = request.form.get('message_id')
        if message_id:
            message = Message.query.get(message_id)
            if message:
                message.deleted = True
                db.session.commit()
                flash(f'Сообщение {message_id} удалено')
                return redirect(url_for('view_chat', chat_id=chat.id))

    return render_template('chat.html', chat=chat, messages=messages, media_files=media_files)

@app.route('/media/<path:filename>')
def media_file(filename):
    """
    Маршрут для отображения медиафайлов.

    Аргументы:
    filename (str): Имя медиафайла.

    Возвращает:
    str: Медиафайл для отображения или скачивания.
    """
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], "media"), filename)

# Запуск приложения
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
