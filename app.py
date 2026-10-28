import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Рядок підключення до PostgreSQL (змінна середовища DATABASE_URL)
# Приклад локально або за замовчуванням:
DB_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@host:5432/dbname')

def get_db_connection():
    conn = psycopg2.connect(DB_URL)
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            title VARCHAR(150) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Ініціалізація таблиці при старті
try:
    init_db()
except Exception as e:
    print(f"Помилка ініціалізації БД: {e}")

@app.route('/', methods=['GET'])
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM notes ORDER BY created_at DESC;')
    notes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', notes=notes)

@app.route('/add', methods=['POST'])
def add_note():
    title = request.form.get('title')
    content = request.form.get('content')
    if title and content:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO notes (title, content) VALUES (%s, %s);',
            (title, content)
        )
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM notes WHERE id = %s;', (note_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
