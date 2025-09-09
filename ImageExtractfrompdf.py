import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import fitz  # PyMuPDF
from PIL import Image
import io
import zipfile
from pathlib import Path

class PDFImageExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Image Extractor & Combiner")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Variables
        self.pdf_path = tk.StringVar()
        self.output_folder = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "PDF_Images"))
        self.images_info = []
        
        # Create output folder if it doesn't exist
        os.makedirs(self.output_folder.get(), exist_ok=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # PDF selection
        ttk.Label(main_frame, text="PDF File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        pdf_frame = ttk.Frame(main_frame)
        pdf_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        pdf_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(pdf_frame, textvariable=self.pdf_path).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(pdf_frame, text="Browse", command=self.browse_pdf).grid(row=0, column=1)
        
        # Output folder selection
        ttk.Label(main_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_folder).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_folder).grid(row=0, column=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Extract Images", command=self.extract_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Combine to PDF", command=self.combine_images_to_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Extracted Images", padding="5")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Treeview to display extracted images
        columns = ("filename", "page", "size")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings")
        
        # Define headings
        self.tree.heading("filename", text="Filename")
        self.tree.heading("page", text="Page")
        self.tree.heading("size", text="Size")
        
        # Define columns
        self.tree.column("filename", width=300)
        self.tree.column("page", width=80, anchor=tk.CENTER)
        self.tree.column("size", width=100, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
    def browse_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.pdf_path.set(file_path)
            
    def browse_output_folder(self):
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.output_folder.set(folder_path)
            
    def extract_images(self):
        if not self.pdf_path.get():
            messagebox.showerror("Error", "Please select a PDF file first.")
            return
            
        if not os.path.exists(self.pdf_path.get()):
            messagebox.showerror("Error", "The selected PDF file does not exist.")
            return
            
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.images_info = []
            
        # Start progress bar
        self.progress.start()
        self.status_var.set("Extracting images...")
        self.root.update()
        
        try:
            pdf_document = fitz.open(self.pdf_path.get())
            image_count = 0
            
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Generate filename
                    image_filename = f"image_page{page_num+1}_{img_index+1}.{image_ext}"
                    image_path = os.path.join(self.output_folder.get(), image_filename)
                    
                    # Save image
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    
                    # Get file size
                    file_size = os.path.getsize(image_path)
                    size_str = self.format_file_size(file_size)
                    
                    # Add to treeview
                    self.tree.insert("", "end", values=(image_filename, page_num+1, size_str))
                    
                    # Store image info
                    self.images_info.append({
                        'filename': image_filename,
                        'path': image_path,
                        'page': page_num + 1,
                        'index': img_index + 1
                    })
                    
                    image_count += 1
            
            pdf_document.close()
            
            self.status_var.set(f"Extracted {image_count} images successfully.")
            messagebox.showinfo("Success", f"Extracted {image_count} images successfully.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract images: {str(e)}")
            self.status_var.set("Error extracting images.")
        
        finally:
            self.progress.stop()
            
    def combine_images_to_pdf(self):
        if not self.images_info:
            messagebox.showwarning("Warning", "No images to combine. Please extract images first.")
            return
            
        # Ask for output PDF filename
        output_pdf = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not output_pdf:
            return
            
        # Start progress bar
        self.progress.start()
        self.status_var.set("Combining images to PDF...")
        self.root.update()
        
        try:
            images = []
            for img_info in self.images_info:
                img_path = img_info['path']
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    images.append(img)
            
            if images:
                images[0].save(
                    output_pdf, "PDF", 
                    resolution=100.0, 
                    save_all=True, 
                    append_images=images[1:]
                )
                
                self.status_var.set(f"PDF created successfully: {os.path.basename(output_pdf)}")
                messagebox.showinfo("Success", f"PDF created successfully: {output_pdf}")
            else:
                messagebox.showwarning("Warning", "No valid images found to combine.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF: {str(e)}")
            self.status_var.set("Error creating PDF.")
            
        finally:
            self.progress.stop()
            
    def open_output_folder(self):
        output_path = self.output_folder.get()
        if os.path.exists(output_path):
            os.startfile(output_path)  # Works on Windows
        else:
            messagebox.showwarning("Warning", "Output folder does not exist.")
            
    def format_file_size(self, size_bytes):
        """Convert file size to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFImageExtractor(root)
    root.mainloop()