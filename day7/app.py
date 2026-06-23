from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import bcrypt
from functools import wraps
import random

app = Flask(__name__)
app.secret_key = 'my_super_secret_key_2026'

# Настройки MySQL 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'elmira1601dav2008#$$'
app.config['MYSQL_DB'] = 'myprojectdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Декораторы
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Доступ запрещён. Нужны права администратора.', 'danger')
            return redirect(url_for('worker_dashboard'))
        return f(*args, **kwargs)
    return decorated

#Маршруты 
@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('worker_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        captcha_user = request.form['captcha']

        # Проверка капчи
        if int(captcha_user) != session.get('captcha_result'):
            flash('Неверно введена капча', 'danger')
            return redirect(url_for('login'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Пользователи WHERE логин = %s", (login,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['пароль_hash'].encode('utf-8')):
            session['user_id'] = user['id_пользователя']
            session['login'] = user['логин']
            session['role'] = user['роль']
            flash(f'Добро пожаловать, {user["логин"]}!', 'success')
            if user['роль'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('worker_dashboard'))
        else:
            flash('Неверный логин или пароль', 'danger')

    # Генерация капчи
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    session['captcha_result'] = num1 + num2
    return render_template('login.html', num1=num1, num2=num2)

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/worker/dashboard')
@login_required
def worker_dashboard():
    return render_template('worker/dashboard.html')

@app.route('/admin/users')
@admin_required
def admin_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_пользователя, логин, роль, created_at FROM Пользователи")
    users = cur.fetchall()
    cur.close()
    return render_template('admin/users.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)