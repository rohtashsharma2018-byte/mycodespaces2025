import sqlite3
import hashlib
from datetime import datetime, timezone
import customtkinter as ctk
from pathlib import Path
import traceback

# ---------- Settings ----------
# Always save DB next to the script so path/working-dir issues don't bite you
DB_PATH = Path(__file__).with_name("login.db")

# Initialize CustomTkinter
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

def init_db():
    """Create the users table if it doesn't exist."""
    DB_PATH.touch(exist_ok=True)  # ensure file exists
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()
    print(f"DB initialized at: {DB_PATH.resolve()}")

def add_user():
    username = entry_username.get().strip()
    password = entry_password.get()

    if not username or not password:
        label_result.configure(text="Please enter both username and password.", text_color="red")
        return

    # (For production: replace SHA-256 with PBKDF2/bcrypt/argon2)
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, password_hash, datetime.now(timezone.utc).isoformat())
            )
            conn.commit()
        label_result.configure(text=f"User '{username}' added successfully!", text_color="green")
        entry_password.delete(0, "end")  # clear password for UX
    except sqlite3.IntegrityError:
        label_result.configure(text=f"Username '{username}' already exists!", text_color="red")
    except Exception as e:
        # Show errors in the UI and print stack for debugging
        label_result.configure(text=f"DB error: {e}", text_color="red")
        traceback.print_exc()

# ---------- GUI ----------
app = ctk.CTk()
app.title("User Registration")
app.geometry("400x300")

# Username Entry
entry_username = ctk.CTkEntry(app, placeholder_text="Username")
entry_username.pack(pady=10)

# Password Entry
entry_password = ctk.CTkEntry(app, placeholder_text="Password", show="*")
entry_password.pack(pady=10)

# Submit Button
btn_submit = ctk.CTkButton(app, text="Add User", command=add_user)
btn_submit.pack(pady=10)

# Result Label
label_result = ctk.CTkLabel(app, text="")
label_result.pack(pady=10)

# Initialize DB before starting the UI
init_db()

# Run the app
app.mainloop()
