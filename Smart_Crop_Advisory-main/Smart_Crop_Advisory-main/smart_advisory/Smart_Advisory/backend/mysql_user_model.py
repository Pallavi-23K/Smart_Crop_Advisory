from backend.models import db, cursor
from werkzeug.security import generate_password_hash, check_password_hash

def init_users_table():
    sql = '''
    CREATE TABLE IF NOT EXISTS users (
      id INT AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(100) NOT NULL UNIQUE,
      password_hash VARCHAR(255) NOT NULL,
      phone VARCHAR(30),
      name VARCHAR(100)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    '''
    cursor.execute(sql)
    db.commit()

def create_user(username: str, password: str, phone: str = None, name: str = None) -> bool:
    hashed = generate_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, phone, name) VALUES (%s, %s, %s, %s)",
            (username, hashed, phone, name),
        )
        db.commit()
        return True
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        return False

def authenticate_user(username: str, password: str):
    cursor.execute("SELECT id, username, password_hash, phone, name FROM users WHERE username=%s", (username,))
    row = cursor.fetchone()
    if row and check_password_hash(row["password_hash"], password):
        return {"id": row["id"], "username": row["username"], "phone": row.get("phone"), "name": row.get("name")}
    return None

init_users_table()
