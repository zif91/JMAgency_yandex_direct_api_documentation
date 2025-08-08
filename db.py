import sqlite3
import secrets

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('DROP TABLE IF EXISTS users')
    conn.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            yandex_login TEXT NOT NULL,
            yandex_token TEXT NOT NULL,
            secret_code TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def save_token(yandex_login, yandex_token):
    secret_code = secrets.token_urlsafe(16)
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO users (yandex_login, yandex_token, secret_code) VALUES (?, ?, ?)',
        (yandex_login, yandex_token, secret_code)
    )
    conn.commit()
    conn.close()
    return secret_code

def get_user_by_secret_code(secret_code):
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE secret_code = ?', (secret_code,)
    ).fetchone()
    conn.close()
    return user
