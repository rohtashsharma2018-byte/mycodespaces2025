import sqlite3
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

APP_TITLE = "Student Management System"
LOGIN_DB = "login.db"
STUDENTS_DB = "students.db"


# ---------------- Helper Functions ----------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_login_db():
    conn = sqlite3.connect(LOGIN_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    # Default admin if no users exist
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            ("admin", hash_password("admin123"), datetime.utcnow().isoformat()),
        )
        conn.commit()
    conn.close()


def init_students_db():
    conn = sqlite3.connect(STUDENTS_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            school_name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ---------------- GUI Frames ----------------
class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)
        self.controller = controller

        ttk.Label(self, text="🔑 Login", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )

        ttk.Label(self, text="Username").grid(row=1, column=0, sticky="e", padx=(0, 5), pady=5)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(self, textvariable=self.username_var, width=20)
        username_entry.grid(row=1, column=1, pady=5)

        ttk.Label(self, text="Password").grid(row=2, column=0, sticky="e", padx=(0, 5), pady=5)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(self, textvariable=self.password_var, show="*", width=20)
        password_entry.grid(row=2, column=1, pady=5)

        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Login", command=self.attempt_login).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Quit", command=self.controller.quit).pack(side="left", padx=5)

        # Bind Enter key to login
        username_entry.bind('<Return>', lambda e: self.attempt_login())
        password_entry.bind('<Return>', lambda e: self.attempt_login())

    def attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showwarning("Missing Info", "Please enter both username and password.")
            return

        try:
            conn = sqlite3.connect(LOGIN_DB)
            c = conn.cursor()
            c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            row = c.fetchone()
            conn.close()

            if row and row[0] == hash_password(password):
                # Clear the login form
                self.username_var.set("")
                self.password_var.set("")
                # Show registration frame
                self.controller.show_registration(username)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")


class RegistrationFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller
        self.logged_in_user = ""
        self.sort_column = None
        self.sort_reverse = False

        # --- User info label ---
        self.user_label = ttk.Label(self, text="", font=("Segoe UI", 10, "bold"))
        self.user_label.pack(anchor="ne", pady=(0, 10))

        # --- Top Frame: Entry Form ---
        form_frame = ttk.LabelFrame(self, text="➕ Student Form")
        form_frame.pack(fill="x", pady=5)

        ttk.Label(form_frame, text="Student Name").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.student_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.student_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="School Name").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.school_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.school_name_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(form_frame, text="Add Student", command=self.add_record).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(form_frame, text="Update Selected", command=self.update_record).grid(row=1, column=2, padx=5, pady=5)

        # --- Buttons for Delete, Export ---
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", pady=5)
        ttk.Button(action_frame, text="🗑 Delete Selected", command=self.delete_record).pack(side="left", padx=5)
        ttk.Button(action_frame, text="💾 Export to CSV", command=self.export_csv).pack(side="left", padx=5)
        ttk.Button(action_frame, text="🚪 Logout", command=self.logout).pack(side="right", padx=5)

        # --- Search Filter ---
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill="x", pady=5)
        ttk.Label(filter_frame, text="Search").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Filter", command=self.refresh_table).pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Clear", command=self.clear_filter).pack(side="left", padx=5)

        # --- Students Table ---
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, pady=5)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Name", "School", "Created"), show="headings")
        for col in ("ID", "Name", "School", "Created"):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by(c))
            self.tree.column(col, anchor="center" if col == "ID" else "w", width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ---------------- Functions ----------------
    def set_user(self, username: str):
        self.logged_in_user = username
        self.user_label.config(text=f"Logged in as: {username}")
        self.refresh_table()

    def logout(self):
        self.logged_in_user = ""
        self.user_label.config(text="")
        self.clear_form()
        self.controller.show_login()

    def add_record(self):
        name = self.student_name_var.get().strip()
        school = self.school_name_var.get().strip()

        if not name or not school:
            messagebox.showwarning("Missing Info", "Please enter both fields.")
            return

        try:
            conn = sqlite3.connect(STUDENTS_DB)
            c = conn.cursor()
            c.execute(
                "INSERT INTO students (student_name, school_name, created_at) VALUES (?, ?, ?)",
                (name, school, datetime.utcnow().isoformat()),
            )
            conn.commit()
            conn.close()
            self.refresh_table()
            self.clear_form()
            messagebox.showinfo("Success", "Student added successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def update_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a record to update.")
            return

        item = self.tree.item(selected[0])
        record_id = item["values"][0]

        name = self.student_name_var.get().strip()
        school = self.school_name_var.get().strip()
        if not name or not school:
            messagebox.showwarning("Missing Info", "Please enter both fields.")
            return

        try:
            conn = sqlite3.connect(STUDENTS_DB)
            c = conn.cursor()
            c.execute(
                "UPDATE students SET student_name=?, school_name=? WHERE id=?",
                (name, school, record_id),
            )
            conn.commit()
            conn.close()
            self.refresh_table()
            self.clear_form()
            messagebox.showinfo("Success", "Student updated successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a record to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
        if not confirm:
            return

        item = self.tree.item(selected[0])
        record_id = item["values"][0]

        try:
            conn = sqlite3.connect(STUDENTS_DB)
            c = conn.cursor()
            c.execute("DELETE FROM students WHERE id=?", (record_id,))
            conn.commit()
            conn.close()
            self.refresh_table()
            self.clear_form()
            messagebox.showinfo("Success", "Student deleted successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def export_csv(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Save CSV File"
            )
            if not filename:
                return

            conn = sqlite3.connect(STUDENTS_DB)
            c = conn.cursor()
            c.execute("SELECT * FROM students")
            rows = c.fetchall()
            conn.close()

            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Student Name", "School Name", "Created At"])
                writer.writerows(rows)

            messagebox.showinfo("Export Successful", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred: {str(e)}")

    def refresh_table(self):
        # Clear existing items
        for row in self.tree.get_children():
            self.tree.delete(row)

        search = self.search_var.get().strip().lower()

        try:
            conn = sqlite3.connect(STUDENTS_DB)
            c = conn.cursor()
            c.execute("SELECT id, student_name, school_name, created_at FROM students ORDER BY id DESC")
            rows = c.fetchall()
            conn.close()

            for row in rows:
                # Apply search filter
                if not search or search in row[1].lower() or search in row[2].lower():
                    # Format the datetime for display
                    try:
                        created_date = datetime.fromisoformat(row[3]).strftime("%Y-%m-%d %H:%M")
                    except:
                        created_date = row[3]
                    
                    display_row = (row[0], row[1], row[2], created_date)
                    self.tree.insert("", "end", values=display_row)
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred while refreshing: {str(e)}")

    def clear_filter(self):
        self.search_var.set("")
        self.refresh_table()

    def clear_form(self):
        self.student_name_var.set("")
        self.school_name_var.set("")

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item["values"]
            if len(values) >= 3:
                self.student_name_var.set(values[1])
                self.school_name_var.set(values[2])

    def sort_by(self, column):
        items = [(self.tree.set(k, column), k) for k in self.tree.get_children("")]
        
        # Sort by ID as integer, others as string
        if column == "ID":
            try:
                items.sort(key=lambda t: int(t[0]), reverse=self.sort_reverse)
            except ValueError:
                items.sort(key=lambda t: t[0], reverse=self.sort_reverse)
        else:
            items.sort(key=lambda t: t[0].lower(), reverse=self.sort_reverse)

        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)

        # Toggle sort order for next click
        self.sort_reverse = not self.sort_reverse


# ---------------- Main App ----------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("800x600")
        self.minsize(700, 500)

        # Configure style
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except:
            pass  # Use default theme if clam is not available
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        # Create main container
        self.container = ttk.Frame(self, padding=10)
        self.container.pack(fill="both", expand=True)

        # Configure grid weights for proper resizing
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Initialize frames
        self.login_frame = LoginFrame(self.container, controller=self)
        self.registration_frame = RegistrationFrame(self.container, controller=self)

        # Place frames in the same grid cell
        self.login_frame.grid(row=0, column=0, sticky="nsew")
        self.registration_frame.grid(row=0, column=0, sticky="nsew")

        # Start with login frame
        self.show_login()

    def show_login(self):
        """Show the login frame"""
        self.login_frame.tkraise()
        self.title(f"{APP_TITLE} - Login")

    def show_registration(self, username):
        """Show the registration/main frame"""
        self.registration_frame.set_user(username)
        self.registration_frame.tkraise()
        self.title(f"{APP_TITLE} - Welcome, {username}")


# ---------------- Run App ----------------
def main():
    try:
        init_login_db()
        init_students_db()
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        messagebox.showerror("Startup Error", f"Failed to start application: {str(e)}")


if __name__ == "__main__":
    main()