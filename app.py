from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'membership.db'


def init_db():
    if not os.path.exists(DATABASE):
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS members (
                            iid INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE,
                            email TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL,
                            phone TEXT,
                            birthdate TEXT)''')
            c.execute('''INSERT OR IGNORE INTO members (username, email, password, phone, birthdate)
                         VALUES (?, ?, ?, ?, ?)''',
                      ('admin', 'admin@example.com', 'admin123', '0912345678', '1990-01-01'))
            conn.commit()


@app.template_filter('add_stars')
def add_stars(s: str) -> str:
    return f'★{s.upper()}★'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        birthdate = request.form.get('birthdate')

        if not username or not email or not password:
            return render_template('error.html', message='請輸入用戶名、電子郵件和密碼')

        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM members WHERE username=?", (username,))
            if c.fetchone():
                return render_template('error.html', message='用戶名已存在')
            c.execute("INSERT INTO members (username, email, password, phone, birthdate) VALUES (?, ?, ?, ?, ?)",
                      (username, email, password, phone, birthdate))
            conn.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return render_template('error.html', message='請輸入電子郵件和密碼')

        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("SELECT iid, username FROM members WHERE email=? AND password=?", (email, password))
            user = c.fetchone()
            if user:
                return render_template('welcome.html', iid=user[0], username=user[1])
            else:
                return render_template('error.html', message='電子郵件或密碼錯誤')
    return render_template('login.html')


@app.route('/edit_profile/<int:iid>', methods=['GET', 'POST'])
def edit_profile(iid):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            phone = request.form.get('phone')
            birthdate = request.form.get('birthdate')

            if not email or not password:
                return render_template('error.html', message='請輸入電子郵件和密碼')

            c.execute("SELECT * FROM members WHERE email=? AND iid!=?", (email, iid))
            if c.fetchone():
                return render_template('error.html', message='電子郵件已被使用')

            c.execute("UPDATE members SET email=?, password=?, phone=?, birthdate=? WHERE iid=?",
                      (email, password, phone, birthdate, iid))
            conn.commit()
            c.execute("SELECT username FROM members WHERE iid=?", (iid,))
            username = c.fetchone()[0]
            return render_template('welcome.html', iid=iid, username=username)

        c.execute("SELECT * FROM members WHERE iid=?", (iid,))
        user = c.fetchone()
        if user:
            return render_template('edit_profile.html', user=user)
        else:
            return redirect(url_for('index'))


@app.route('/delete/<int:iid>')
def delete_user(iid):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM members WHERE iid=?", (iid,))
        conn.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
