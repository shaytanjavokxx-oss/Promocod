import sqlite3
from datetime import datetime

DB = "skidka.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT,
        first_name TEXT,
        phone TEXT,
        sana TEXT
    )''')
    conn.commit()
    conn.close()

def user_qoshish(user_id, username, first_name, phone=None):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO users (user_id, username, first_name, phone, sana)
                 VALUES (?, ?, ?, ?, ?)''',
              (user_id, username or "", first_name or "", phone,
               datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def phone_saqlash(user_id, phone):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET phone=? WHERE user_id=?", (phone, user_id))
    conn.commit()
    conn.close()

def barcha_users():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT user_id, username, first_name, phone, sana FROM users ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def jami_users():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    n = c.fetchone()[0]
    conn.close()
    return n
