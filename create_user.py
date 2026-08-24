import json
import os
from werkzeug.security import generate_password_hash

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def create_user():
    username = input("Masukkan username baru: ").strip()
    password = input("Masukkan password: ").strip()

    users = load_users()

    if username in users:
        print("❌ Username sudah ada.")
        return

    password_hash = generate_password_hash(password)
    users[username] = {"password_hash": password_hash}

    save_users(users)
    print(f"✅ User '{username}' berhasil dibuat.")

if __name__ == "__main__":
    create_user()

