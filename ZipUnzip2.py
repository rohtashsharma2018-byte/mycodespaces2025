from ttkbootstrap import *
from ttkbootstrap.scrolled import ScrolledFrame
from tkinter import filedialog, messagebox, StringVar, BooleanVar
from tkinter.constants import *
import zipfile
import os
from pathlib import Path
import threading

class ZipManagerApp(Window):
    def __init__(self):
        super().__init__(title="Zip Manager", themename="flatly")
        self.geometry("750x700")
        
        # Create main frame with scrollability
        self.main_frame = ScrolledFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill=BOTH, expand=True)
        
        # Title
        self.title_label = Label(self.main_frame, text="Zip Manager", bootstyle="header")
        self.title_label.pack(pady=20)
        
        # Tab container frame with fixed height
        tab_frame = Frame(self.main_frame, height=550)
        tab_frame.pack(padx=10, pady=10, fill=BOTH, expand=True)
        tab_frame.pack_propagate(False)
        
        # Create notebook for tabs
        self.tabview = ttk.Notebook(tab_frame)
        self.tabview.pack(fill=BOTH, expand=True)
        
        # Create tabs
        self.zip_tab = Frame(self.tabview)
        self.unzip_tab = Frame(self.tabview)
        self.tabview.add(self.zip_tab, text="Zip Files/Folders")
        self.tabview.add(self.unzip_tab, text="Unzip Archive")
        
        # Setup zip tab
        self.setup_zip_tab()
        
        # Setup unzip tab
        self.setup_unzip_tab()
        self.tabview.bind('<<NotebookTabChanged>>', self.on_tab_change)
        self.on_tab_change(None)
        
        # Status label
        self.status_label = Label(self.main_frame, text="Ready", foreground="gray")
        self.status_label.pack(pady=10)
    
    def setup_zip_tab(self):
        # Main container for zip tab with scroll
        self.zip_container = ScrolledFrame(self.zip_tab)
        self.zip_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Files to zip selection
        self.files_frame = Frame(self.zip_container)
        self.files_frame.pack(fill=X, pady=10)
        
        self.files_label = Label(self.files_frame, text="Items to Zip:")
        self.files_label.pack(anchor=W, pady=(0, 10))
        
        self.files_listbox = Text(self.files_frame, height=8, state=DISABLED)
        self.files_listbox.pack(fill=X, pady=(0, 10))
        
        # Button frame for file/folder selection
        self.selection_button_frame = Frame(self.files_frame)
        self.selection_button_frame.pack(fill=X, pady=(0, 10))
        
        self.select_files_button = Button(self.selection_button_frame, text="Select Files", command=self.select_files, bootstyle=PRIMARY)
        self.select_files_button.pack(side=LEFT, padx=(0, 10))
        
        self.select_folder_button = Button(self.selection_button_frame, text="Select Folder", command=self.select_folder, bootstyle=PRIMARY)
        self.select_folder_button.pack(side=LEFT, padx=(0, 10))
        
        self.clear_files_button = Button(self.selection_button_frame, text="Clear Selection", command=self.clear_files, bootstyle=OUTLINE)
        self.clear_files_button.pack(side=LEFT)
        
        # Output zip file selection
        self.output_frame = Frame(self.zip_container)
        self.output_frame.pack(fill=X, pady=10)
        
        self.output_label = Label(self.output_frame, text="Output Zip File:")
        self.output_label.pack(anchor=W, pady=(0, 10))
        
        self.output_path_var = StringVar()
        self.output_entry = Entry(self.output_frame, textvariable=self.output_path_var, bootstyle=INFO)
        self.output_entry.pack(fill=X, pady=(0, 10))
        
        self.select_output_button = Button(self.output_frame, text="Choose Output Location", command=self.select_output_location, bootstyle=INFO)
        self.select_output_button.pack()
        
        # Zip options
        self.options_frame = Frame(self.zip_container)
        self.options_frame.pack(fill=X, pady=10)
        
        
        # Zip name option
        self.zip_name_frame = Frame(self.options_frame)
        self.zip_name_frame.pack(fill=X, pady=(0, 10))
        
        self.zip_name_label = Label(self.zip_name_frame, text="Zip File Name:")
        self.zip_name_label.pack(anchor=W, pady=(0, 5))
        
        self.zip_name_var = StringVar(value="archive")
        self.zip_name_entry = Entry(self.zip_name_frame, textvariable=self.zip_name_var, bootstyle=INFO)
        self.zip_name_entry.pack(fill=X)
        
        # Zip button frame - Making it more prominent
        self.zip_button_frame = Frame(self.zip_container)
        self.zip_button_frame.pack(fill=X, pady=20)
        
        # Zip button - More prominent styling
        self.zip_button = Button(self.zip_button_frame, text="📁 CREATE ZIP ARCHIVE", command=self.start_zip_process, bootstyle=SUCCESS)
        self.zip_button.pack(fill=X, pady=5)
        
        # Store selected items
        self.selected_items = []
    
    def setup_unzip_tab(self):
        # Main container for unzip tab
        self.unzip_container = ScrolledFrame(self.unzip_tab)
        self.unzip_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Zip file selection
        self.zip_file_frame = Frame(self.unzip_container)
        self.zip_file_frame.pack(fill=X, pady=10)
        
        self.zip_file_label = Label(self.zip_file_frame, text="Zip File to Extract:")
        self.zip_file_label.pack(anchor=W, pady=(0, 10))
        
        self.zip_file_path_var = StringVar()
        self.zip_file_entry = Entry(self.zip_file_frame, textvariable=self.zip_file_path_var, bootstyle=INFO)
        self.zip_file_entry.pack(fill=X, pady=(0, 10))
        
        self.select_zip_button = Button(self.zip_file_frame, text="Select Zip File", command=self.select_zip_file, bootstyle=INFO)
        self.select_zip_button.pack()
        
        # Output directory selection
        self.extract_dir_frame = Frame(self.unzip_container)
        self.extract_dir_frame.pack(fill=X, pady=10)
        
        self.extract_dir_label = Label(self.extract_dir_frame, text="Extract To:")
        self.extract_dir_label.pack(anchor=W, pady=(0, 10))
        
        self.extract_dir_var = StringVar()
        self.extract_dir_entry = Entry(self.extract_dir_frame, textvariable=self.extract_dir_var, bootstyle=INFO)
        self.extract_dir_entry.pack(fill=X, pady=(0, 10))
        
        self.select_extract_dir_button = Button(self.extract_dir_frame, text="Choose Extraction Directory", command=self.select_extract_directory, bootstyle=INFO)
        self.select_extract_dir_button.pack()
        
        # Unzip options
        self.unzip_options_frame = Frame(self.unzip_container)
        self.unzip_options_frame.pack(fill=X, pady=10)
        
        self.overwrite_var = BooleanVar(value=True)
        self.overwrite_check = Checkbutton(self.unzip_options_frame, text="Overwrite existing files", variable=self.overwrite_var, bootstyle="round-toggle")
        self.overwrite_check.pack(anchor=W, pady=(0, 10))
        
        # Unzip button frame
        self.unzip_button_frame = Frame(self.unzip_container)
        self.unzip_button_frame.pack(fill=X, pady=20)
        
        # Unzip button - More prominent styling
        self.unzip_button = Button(self.unzip_button_frame, text="📂 EXTRACT ARCHIVE", command=self.start_unzip_process, bootstyle=PRIMARY)
        self.unzip_button.pack(fill=X, pady=5)
    
    def on_tab_change(self, event):
        selected_tab = self.tabview.select()
        # Reset all tabs to default style
        self.zip_container.configure(style='')
        self.unzip_container.configure(style='')
        if selected_tab == self.zip_tab:
            self.zip_container.configure(style='Primary.TFrame')
        elif selected_tab == self.unzip_tab:
            self.unzip_container.configure(style='Success.TFrame')
    
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select files to zip",
            filetypes=[("All files", "*.*")]
        )
        
        if files:
            for file in files:
                if file not in self.selected_items:
                    self.selected_items.append(file)
            self.update_files_listbox()
    
    def select_folder(self):
        folder = filedialog.askdirectory(title="Select folder to zip")
        
        if folder and folder not in self.selected_items:
            self.selected_items.append(folder)
            self.update_files_listbox()
    
    def clear_files(self):
        self.selected_items = []
        self.update_files_listbox()
    
    def update_files_listbox(self):
        self.files_listbox.config(state="normal")
        self.files_listbox.delete("1.0", "end")
        
        if self.selected_items:
            for item in self.selected_items:
                if os.path.isfile(item):
                    self.files_listbox.insert("end", f"📄 File: {os.path.basename(item)}\n")
                else:
                    self.files_listbox.insert("end", f"📁 Folder: {os.path.basename(item)}/\n")
            self.files_listbox.insert("end", f"\nTotal items: {len(self.selected_items)}")
        else:
            self.files_listbox.insert("end", "No items selected")
        
        self.files_listbox.config(state="disabled")
    
    def select_output_location(self):
        default_name = f"{self.zip_name_var.get()}.zip"
        file_path = filedialog.asksaveasfilename(
            title="Save zip file as",
            defaultextension=".zip",
            initialfile=default_name,
            filetypes=[("Zip files", "*.zip")]
        )
        
        if file_path:
            self.output_path_var.set(file_path)
    
    def select_zip_file(self):
        file_path = filedialog.askopenfilename(
            title="Select zip file",
            filetypes=[("Zip files", "*.zip"), ("All files", "*.*")]
        )
        
        if file_path:
            self.zip_file_path_var.set(file_path)
    
    def select_extract_directory(self):
        directory = filedialog.askdirectory(title="Select extraction directory")
        
        if directory:
            self.extract_dir_var.set(directory)
    
    
    def start_zip_process(self):
        if not self.selected_items:
            messagebox.showerror("Error", "Please select files or folders to zip")
            return
        
        if not self.output_path_var.get():
            # Auto-generate output path if not specified
            default_dir = os.path.dirname(self.selected_items[0]) if self.selected_items else os.getcwd()
            default_name = f"{self.zip_name_var.get()}.zip"
            auto_path = os.path.join(default_dir, default_name)
            self.output_path_var.set(auto_path)
        
        # Run in separate thread to avoid freezing the UI
        thread = threading.Thread(target=self.create_zip)
        thread.daemon = True
        thread.start()
    
    def create_zip(self):
        try:
            self.after(0, lambda: self.status_label.config(
                text="Creating zip archive...", 
                foreground="yellow"
            ))
            self.after(0, lambda: self.zip_button.config(state="disabled"))
            
            compression = zipfile.ZIP_DEFLATED
            
            with zipfile.ZipFile(self.output_path_var.get(), 'w', compression=compression) as zipf:
                for item_path in self.selected_items:
                    if os.path.isfile(item_path):
                        # Add individual file
                        zipf.write(item_path, os.path.basename(item_path))
                    elif os.path.isdir(item_path):
                        # Add folder and all its contents
                        folder_name = os.path.basename(item_path)
                        for root, dirs, files in os.walk(item_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                # Create relative path for zip
                                arcname = os.path.join(folder_name, os.path.relpath(file_path, item_path))
                                zipf.write(file_path, arcname)
            
            self.after(0, lambda: self.status_label.config(
                text=f"Zip created successfully: {os.path.basename(self.output_path_var.get())}", 
                foreground="green"
            ))
            self.after(0, lambda: self.zip_button.config(state="normal"))
            self.after(0, lambda: messagebox.showinfo("Success", "Zip archive created successfully!"))
            
        except Exception as e:
            self.after(0, lambda: self.status_label.config(
                text=f"Error: {str(e)}", 
                foreground="red"
            ))
            self.after(0, lambda: self.zip_button.config(state="normal"))
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to create zip: {str(e)}"))
    
    def start_unzip_process(self):
        zip_file = self.zip_file_path_var.get()
        extract_dir = self.extract_dir_var.get()
        
        if not zip_file or not os.path.exists(zip_file):
            messagebox.showerror("Error", "Please select a valid zip file")
            return
        
        if not extract_dir:
            messagebox.showerror("Error", "Please select extraction directory")
            return
        
        # Run in separate thread to avoid freezing the UI
        thread = threading.Thread(target=self.extract_zip, args=(zip_file, extract_dir))
        thread.daemon = True
        thread.start()
    
    def extract_zip(self, zip_file, extract_dir):
        try:
            self.after(0, lambda: self.status_label.config(
                text="Extracting archive...", 
                foreground="yellow"
            ))
            self.after(0, lambda: self.unzip_button.config(state="disabled"))
            
            with zipfile.ZipFile(zip_file, 'r') as zipf:
                # Extract all files, overwriting if the option is selected
                zipf.extractall(extract_dir)
            
            self.after(0, lambda: self.status_label.config(
                text=f"Extraction completed to: {os.path.basename(extract_dir)}", 
                foreground="green"
            ))
            self.after(0, lambda: self.unzip_button.config(state="normal"))
            self.after(0, lambda: messagebox.showinfo("Success", "Archive extracted successfully!"))
            
        except Exception as e:
            self.after(0, lambda: self.status_label.config(
                text=f"Error: {str(e)}", 
                foreground="red"
            ))
            self.after(0, lambda: self.unzip_button.config(state="normal"))
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to extract zip: {str(e)}"))

if __name__ == "__main__":
    app = ZipManagerApp()
    app.mainloop()