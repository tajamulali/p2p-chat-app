import sqlite3
import hashlib

def setup_db():
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_login(username, password):
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return verify_password(row[0], password)
    return False

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

def save_message(username, message):
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (username, message) VALUES (?, ?)', (username, message))
    conn.commit()
    conn.close()
