import tkinter as tk
from tkinter import filedialog, messagebox, Text
from ttkbootstrap import Style
from ttkbootstrap.widgets import Button, Label
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Optional: Set path to tesseract executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class MultiImageTextExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Image Text Extractor")
        self.root.geometry("800x600")
        self.style = Style("flatly")

        # UI Elements
        self.label = Label(root, text="Extracted Text:", font=("Helvetica", 12),background="orange",foreground="white",borderwidth=5)
        self.label.pack(pady=10)

        self.text_box = Text(root, wrap="word", height=25, font=("Helvetica", 11 ))
        self.text_box.pack(padx=10, pady=10, fill="both", expand=True)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        self.upload_btn = Button(self.button_frame, text="Upload Images", command=self.upload_images)
        self.upload_btn.pack(side="left", padx=10)

        self.save_btn = Button(self.button_frame, text="Save as Text File", command=self.save_text)
        self.save_btn.pack(side="left", padx=10)

        self.clear_btn = Button(self.button_frame, text="Clear Text", command=self.clear_text)
        self.clear_btn.pack(side="left", padx=10)

    def upload_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if file_paths:
            combined_text = ""
            for path in file_paths:
                try:
                    image = Image.open(path)
                    text = pytesseract.image_to_string(image)
                    combined_text += f"\n--- Text from {path} ---\n{text}\n"
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to process image {path}:\n{e}")
            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, combined_text)

    def save_text(self):
        text = self.text_box.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No text to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                messagebox.showinfo("Success", "Text saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def clear_text(self):
        self.text_box.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiImageTextExtractorApp(root)
    root.mainloop()
