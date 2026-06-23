import bcrypt
import MySQLdb

conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='elmira1601dav2008#$$',
    db='myprojectdb'
)
cursor = conn.cursor()

users = [
    ('admin', 'admin123', 'admin'),
    ('worker', 'worker123', 'worker')
]

for login, password, role in users:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("""
        INSERT INTO Пользователи (логин, пароль_hash, роль)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            пароль_hash = VALUES(пароль_hash),
            роль = VALUES(роль)
    """, (login, hashed.decode('utf-8'), role))
    print(f"Пользователь {login} добавлен")

conn.commit()
cursor.close()
conn.close()
print("Готово!")