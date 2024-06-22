from sqlalchemy.exc import IntegrityError, NoResultFound
from flask_sqlalchemy import SQLAlchemy
from flask import Flask


UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Модели базы данных
class Chat(db.Model):
    """
    Модель для таблицы чатов в базе данных.
    Связана с таблицами сообщений и медиафайлов.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)  # Имя чата (список участников)
    messages = db.relationship('Message', backref='chat', lazy=True)
    media_files = db.relationship('Media', backref='chat', lazy=True)

class Message(db.Model):
    """
    Модель для таблицы сообщений в базе данных.
    """
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(20), nullable=False)
    sender = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    deleted = db.Column(db.Boolean, default=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)

class Media(db.Model):
    """
    Модель для таблицы медиафайлов в базе данных.
    """
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.String(20), nullable=False)
    sender = db.Column(db.String(100), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)