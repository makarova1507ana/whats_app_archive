# whats_app_archive

### Архитектура проекта
  ```bash
project/
│
├── for_test/                  # Папка с тестовыми архивами чатов WhatsApp
│   ├── new_chat_1.zip         # Пример архива чата WhatsApp
│   ├── RENAME_WhatsApp_1.zip  # Пример архива чата WhatsApp
│   └── WhatsApp_1.zip         # Пример архива чата WhatsApp
│
├── templates/                 # Папка с HTML-шаблонами для Flask-приложения
│   ├── index.html             # Шаблон для главной страницы
│   ├── chat.html              # Шаблон для страницы просмотра чата
│   └── chats.html             # Шаблон для страницы со списком чатов
│
├── uploads/                   # Папка, куда загружаются и распаковываются архивы
│
├── app.py                     # Основной файл Flask-приложения
│
└── chatParse.py               # Скрипт для парсинга архива чатов WhatsApp

  ```

пример приложения:
![image](https://github.com/makarova1507ana/whats_app_archive/assets/103330304/5282b30e-ca46-417c-9e94-50c182b1080c)

Чтобы скачать проект с GitHub и запустить его, вам понадобится выполнить несколько шагов:

### Шаги для скачивания и запуска проекта

#### Клонирование репозитория:

- Откройте терминал (командную строку).
- Перейдите в папку, в которой вы хотите сохранить проект, используя команду `cd ПУТЬ_К_ПАПКЕ`.
- Выполните команду для клонирования репозитория с GitHub:

    ```bash
    git clone <URL_РЕПОЗИТОРИЯ>
    ```

    Замените `<URL_РЕПОЗИТОРИЯ>` на URL вашего репозитория на GitHub. Например:

    ```bash
    git clone https://github.com/username/repository.git
    ```

    Это загрузит содержимое репозитория в выбранную вами папку.

#### Установка зависимостей:

- Перейдите в папку проекта, которую вы только что склонировали:

    ```bash
    cd repository
    ```

- Убедитесь, что у вас есть файл `requirements.txt`, который должен содержать все необходимые зависимости для проекта.
- Установите зависимости, выполнив следующую команду:

    ```bash
    pip install -r requirements.txt
    ```

    Это установит все зависимости, указанные в файле `requirements.txt`.

#### Запуск приложения:

- После успешной установки зависимостей вы можете запустить ваше Flask приложение.
- Запустите приложение с помощью команды:

    ```bash
    python app.py
    ```

    Здесь `app.py` - это файл, содержащий основной код вашего Flask приложения. Если у вас другое имя файла, замените его соответствующим образом.
- После запуска, вы увидите сообщение о том, что Flask приложение запущено на локальном сервере. Обычно это будет выглядеть как `Running on http://127.0.0.1:5000/` или подобное.

#### Просмотр приложения:

- Откройте веб-браузер и перейдите по адресу, указанному в выводе Flask (обычно `http://127.0.0.1:5000/`).
- Теперь вы должны увидеть ваше приложение в работе.


