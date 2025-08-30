import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader

# ---------- App Logic ----------
def open_file():
    filename = filedialog.askopenfilename(
        title="Open PDF file",
        initialdir=r'D:\codefirst.io\Tkinter Extract PDF Text',
        filetypes=[('PDF files', '*.pdf')]
    )
    if not filename:
        return

    # Show only the filename (not the whole path) in the label
    filename_label.configure(text=os.path.basename(filename))

    # Clear previous output
    output_text.delete("1.0", "end")

    try:
        # Read PDF text
        with open(filename, "rb") as f:
            reader = PdfReader(f)

            # New PyPDF2 API: iterate pages via reader.pages
            for page in reader.pages:
                current_text = page.extract_text() or ""
                output_text.insert("end", current_text + "\n")

        # Scroll to top after load
        output_text.see("1.0")

    except Exception as e:
        messagebox.showerror("Error", f"Could not read PDF.\n\n{e}")

def clear_text():
    output_text.delete("1.0", "end")

def save_text():
    text = output_text.get("1.0", "end").strip()
    if not text:
        messagebox.showinfo("Nothing to save", "The text box is empty.")
        return

    save_path = filedialog.asksaveasfilename(
        title="Save extracted text",
        defaultextension=".txt",
        filetypes=[("Text file", "*.txt"), ("All files", "*.*")]
    )
    if save_path:
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Saved", f"Text saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file.\n\n{e}")

# ---------- UI Setup (CustomTkinter) ----------
ctk.set_appearance_mode("System")      # "Light", "Dark", or "System"
ctk.set_default_color_theme("blue")    # "blue", "green", "dark-blue", or a custom JSON theme

app = ctk.CTk()
app.title("PDF Text Extractor (CustomTkinter)")
app.geometry("900x600")

# Make the main window responsive
app.grid_rowconfigure(1, weight=1)
app.grid_columnconfigure(0, weight=1)

# Top bar: buttons + filename
top_frame = ctk.CTkFrame(app, corner_radius=8)
top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
top_frame.grid_columnconfigure(2, weight=1)

open_button = ctk.CTkButton(top_frame, text="Open PDF", command=open_file)
open_button.grid(row=0, column=0, padx=(10, 6), pady=10)

save_button = ctk.CTkButton(top_frame, text="Save Text", command=save_text)
save_button.grid(row=0, column=1, padx=6, pady=10)

filename_label = ctk.CTkLabel(top_frame, text="No file selected", anchor="w")
filename_label.grid(row=0, column=2, sticky="ew", padx=(6, 10), pady=10)

# Text area (scrollable)
output_text = ctk.CTkTextbox(app, wrap="word")
output_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(6, 10))

# Optional: Clear button at the bottom
bottom_frame = ctk.CTkFrame(app, fg_color="transparent")
bottom_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
clear_button = ctk.CTkButton(bottom_frame, text="Clear", command=clear_text, width=100)
clear_button.pack(anchor="e")

app.mainloop()
