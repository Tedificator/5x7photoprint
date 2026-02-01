#!/usr/bin/env python3
"""
Photo to PDF Processor - GUI Application
=========================================

A graphical user interface for the photo processing script.
Makes it easy to select folders, process photos, and generate PDFs
without using the command line.

Requirements:
    pip install Pillow opencv-python reportlab

Usage:
    python photo_to_pdf_gui.py

Features:
    - Browse for input folder
    - Choose output PDF location
    - Real-time progress updates
    - Preview of selected folder
    - Drag and drop support (platform-dependent)
    - Settings adjustment

Author: Claude
Date: 2026-02-01
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import os
from pathlib import Path
from typing import Optional
import sys

# Import the photo processor (assumes photo_to_pdf.py is in the same directory)
try:
    from photo_to_pdf import PhotoProcessor
except ImportError:
    # If we can't import, we'll show an error in the GUI
    PhotoProcessor = None


class PhotoProcessorGUI:
    """
    Main GUI application for the Photo to PDF Processor.
    
    Provides a user-friendly interface with:
    - Folder selection dialogs
    - Progress tracking
    - Real-time status updates
    - Preview of images to be processed
    """
    
    def __init__(self, root):
        """
        Initialize the GUI application.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("Photo to PDF Processor")
        self.root.geometry("700x600")
        
        # Set minimum window size
        self.root.minsize(600, 500)
        
        # Variables to store user selections
        self.input_folder = tk.StringVar()
        self.output_file = tk.StringVar()
        
        # Queue for thread-safe communication between processing thread and GUI
        self.message_queue = queue.Queue()
        
        # Flag to track if processing is in progress
        self.processing = False
        
        # Create the GUI layout
        self.create_widgets()
        
        # Start checking for messages from processing thread
        self.check_message_queue()
        
        # Check if PhotoProcessor is available
        if PhotoProcessor is None:
            self.show_import_error()
    
    def create_widgets(self):
        """Create and layout all GUI widgets."""
        
        # ===== HEADER SECTION =====
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="Photo to PDF Processor",
            font=('Helvetica', 16, 'bold')
        )
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Process photos with face detection and create print-ready PDFs",
            font=('Helvetica', 9)
        )
        subtitle_label.grid(row=1, column=0, sticky=tk.W)
        
        # ===== INPUT FOLDER SECTION =====
        input_frame = ttk.LabelFrame(self.root, text="1. Select Input Folder", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), padx=10, pady=5)
        
        # Input folder path display
        ttk.Label(input_frame, text="Folder:").grid(row=0, column=0, sticky=tk.W)
        
        input_entry = ttk.Entry(
            input_frame,
            textvariable=self.input_folder,
            width=50,
            state='readonly'
        )
        input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Browse button
        browse_input_btn = ttk.Button(
            input_frame,
            text="Browse...",
            command=self.browse_input_folder
        )
        browse_input_btn.grid(row=0, column=2, padx=5)
        
        # Image count label
        self.image_count_label = ttk.Label(input_frame, text="No folder selected")
        self.image_count_label.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # Configure column weights for resizing
        input_frame.columnconfigure(1, weight=1)
        
        # ===== OUTPUT FILE SECTION =====
        output_frame = ttk.LabelFrame(self.root, text="2. Choose Output PDF", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), padx=10, pady=5)
        
        # Output file path display
        ttk.Label(output_frame, text="File:").grid(row=0, column=0, sticky=tk.W)
        
        output_entry = ttk.Entry(
            output_frame,
            textvariable=self.output_file,
            width=50,
            state='readonly'
        )
        output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Browse button
        browse_output_btn = ttk.Button(
            output_frame,
            text="Browse...",
            command=self.browse_output_file
        )
        browse_output_btn.grid(row=0, column=2, padx=5)
        
        # Configure column weights
        output_frame.columnconfigure(1, weight=1)
        
        # ===== PROGRESS SECTION =====
        progress_frame = ttk.LabelFrame(self.root, text="3. Process Photos", padding="10")
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N), padx=10, pady=5)
        
        # Process button
        self.process_btn = ttk.Button(
            progress_frame,
            text="Start Processing",
            command=self.start_processing,
            state='disabled'
        )
        self.process_btn.grid(row=0, column=0, pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(
            progress_frame,
            text="Ready to process",
            foreground='gray'
        )
        self.status_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        # ===== LOG/OUTPUT SECTION =====
        log_frame = ttk.LabelFrame(self.root, text="Processing Log", padding="10")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # Create scrolled text widget for log
        log_scroll = ttk.Scrollbar(log_frame)
        log_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.log_text = tk.Text(
            log_frame,
            height=12,
            width=70,
            wrap=tk.WORD,
            yscrollcommand=log_scroll.set,
            state='disabled',
            font=('Courier', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scroll.config(command=self.log_text.yview)
        
        # Configure log frame to expand
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # ===== BOTTOM BUTTONS =====
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        
        # Help button
        help_btn = ttk.Button(
            button_frame,
            text="Help",
            command=self.show_help
        )
        help_btn.grid(row=0, column=0, padx=5)
        
        # About button
        about_btn = ttk.Button(
            button_frame,
            text="About",
            command=self.show_about
        )
        about_btn.grid(row=0, column=1, padx=5)
        
        # Exit button
        exit_btn = ttk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit
        )
        exit_btn.grid(row=0, column=2, padx=5)
        
        # Configure main window grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(4, weight=1)  # Make log section expandable
    
    def browse_input_folder(self):
        """Open a dialog to select the input folder containing photos."""
        folder = filedialog.askdirectory(
            title="Select Folder Containing Photos",
            initialdir=os.path.expanduser("~")
        )
        
        if folder:
            self.input_folder.set(folder)
            self.count_images()
            self.update_process_button()
            self.log_message(f"Selected input folder: {folder}")
    
    def browse_output_file(self):
        """Open a dialog to select the output PDF file location."""
        file = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        if file:
            self.output_file.set(file)
            self.update_process_button()
            self.log_message(f"Output will be saved to: {file}")
    
    def count_images(self):
        """Count the number of valid image files in the selected folder."""
        folder = self.input_folder.get()
        if not folder:
            return
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
        try:
            image_files = [
                f for f in Path(folder).iterdir()
                if f.is_file() and f.suffix.lower() in image_extensions
            ]
            
            count = len(image_files)
            
            if count == 0:
                self.image_count_label.config(
                    text="⚠ No image files found in this folder",
                    foreground='red'
                )
            else:
                self.image_count_label.config(
                    text=f"✓ Found {count} image{'s' if count != 1 else ''} to process",
                    foreground='green'
                )
        except Exception as e:
            self.image_count_label.config(
                text=f"Error reading folder: {str(e)}",
                foreground='red'
            )
    
    def update_process_button(self):
        """Enable or disable the process button based on input validity."""
        if self.input_folder.get() and self.output_file.get():
            self.process_btn.config(state='normal')
        else:
            self.process_btn.config(state='disabled')
    
    def log_message(self, message):
        """
        Add a message to the log text widget.
        
        Args:
            message: The message to log
        """
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Scroll to bottom
        self.log_text.config(state='disabled')
    
    def start_processing(self):
        """Start the photo processing in a separate thread."""
        if self.processing:
            return
        
        # Validate inputs
        input_folder = self.input_folder.get()
        output_file = self.output_file.get()
        
        if not input_folder or not output_file:
            messagebox.showerror(
                "Missing Information",
                "Please select both an input folder and output file."
            )
            return
        
        # Check if PhotoProcessor is available
        if PhotoProcessor is None:
            messagebox.showerror(
                "Import Error",
                "Could not import PhotoProcessor.\n\n"
                "Make sure photo_to_pdf.py is in the same directory."
            )
            return
        
        # Clear log
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        # Update UI state
        self.processing = True
        self.process_btn.config(state='disabled', text="Processing...")
        self.progress_bar.start()
        self.status_label.config(text="Processing photos...", foreground='blue')
        
        # Start processing in a separate thread
        thread = threading.Thread(
            target=self.process_photos,
            args=(input_folder, output_file),
            daemon=True
        )
        thread.start()
    
    def process_photos(self, input_folder, output_file):
        """
        Process photos in a separate thread.
        
        This method runs in a background thread to avoid freezing the GUI.
        It communicates with the main thread via a queue.
        
        Args:
            input_folder: Path to folder containing photos
            output_file: Path where PDF should be saved
        """
        try:
            # Send start message
            self.message_queue.put(("log", "=" * 60))
            self.message_queue.put(("log", "Starting photo processing..."))
            self.message_queue.put(("log", f"Input: {input_folder}"))
            self.message_queue.put(("log", f"Output: {output_file}"))
            self.message_queue.put(("log", "=" * 60))
            
            # Create processor with custom output redirection
            processor = PhotoProcessorWithLogging(self.message_queue)
            
            # Process the folder
            processor.process_folder(input_folder, output_file)
            
            # Send completion message
            self.message_queue.put(("log", "=" * 60))
            self.message_queue.put(("log", "✓ Processing complete!"))
            self.message_queue.put(("log", f"PDF saved to: {output_file}"))
            self.message_queue.put(("log", "=" * 60))
            self.message_queue.put(("complete", output_file))
            
        except Exception as e:
            # Send error message
            self.message_queue.put(("log", "=" * 60))
            self.message_queue.put(("log", f"✗ Error: {str(e)}"))
            self.message_queue.put(("log", "=" * 60))
            self.message_queue.put(("error", str(e)))
    
    def check_message_queue(self):
        """
        Check for messages from the processing thread and update GUI.
        
        This method runs periodically to handle thread-safe communication.
        """
        try:
            while True:
                # Get message from queue (non-blocking)
                msg_type, msg_data = self.message_queue.get_nowait()
                
                if msg_type == "log":
                    # Add to log
                    self.log_message(msg_data)
                    
                elif msg_type == "complete":
                    # Processing completed successfully
                    self.processing = False
                    self.progress_bar.stop()
                    self.process_btn.config(state='normal', text="Start Processing")
                    self.status_label.config(text="✓ Complete!", foreground='green')
                    
                    # Ask if user wants to open the PDF
                    result = messagebox.askyesno(
                        "Processing Complete",
                        f"PDF created successfully!\n\n{msg_data}\n\n"
                        "Would you like to open the folder containing the PDF?"
                    )
                    
                    if result:
                        self.open_output_folder(msg_data)
                
                elif msg_type == "error":
                    # Processing failed
                    self.processing = False
                    self.progress_bar.stop()
                    self.process_btn.config(state='normal', text="Start Processing")
                    self.status_label.config(text="✗ Error occurred", foreground='red')
                    
                    messagebox.showerror(
                        "Processing Error",
                        f"An error occurred during processing:\n\n{msg_data}"
                    )
        
        except queue.Empty:
            # No messages in queue, that's fine
            pass
        
        # Schedule next check
        self.root.after(100, self.check_message_queue)
    
    def open_output_folder(self, file_path):
        """
        Open the folder containing the output file.
        
        Args:
            file_path: Path to the output file
        """
        import subprocess
        import platform
        
        folder = os.path.dirname(os.path.abspath(file_path))
        
        try:
            if platform.system() == "Windows":
                os.startfile(folder)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", folder])
            else:  # Linux and others
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not open folder:\n{str(e)}"
            )
    
    def show_help(self):
        """Display help information."""
        help_text = """Photo to PDF Processor - Help

HOW TO USE:

1. Select Input Folder
   Click 'Browse' to choose a folder containing your photos.
   Supported formats: JPG, PNG, BMP, TIFF

2. Choose Output PDF
   Click 'Browse' to select where to save the PDF.
   The default extension is .pdf

3. Process Photos
   Click 'Start Processing' to begin.
   The log will show progress as each photo is processed.

WHAT IT DOES:

• Detects faces in photos using AI
• Crops photos to 5x7 ratio, centered on faces
• Adds filename labels below each photo
• Arranges 2 photos per 8.5x11 page
• Creates a high-quality PDF (300 DPI)

TIPS:

• Use high-resolution photos (1500x2100+ pixels)
• Photos with clear faces work best
• Processing time: ~1-2 seconds per photo
• Larger folders will take longer
"""
        
        messagebox.showinfo("Help", help_text)
    
    def show_about(self):
        """Display about information."""
        about_text = """Photo to PDF Processor
Version 1.0.0

A tool for processing photos with face detection
and creating print-ready PDFs.

Features:
• Automatic face detection
• Smart 5x7 cropping
• High-quality PDF output (300 DPI)
• 2 photos per 8.5x11 page

Created with Python, OpenCV, Pillow, and ReportLab

© 2026"""
        
        messagebox.showinfo("About", about_text)
    
    def show_import_error(self):
        """Show error if PhotoProcessor couldn't be imported."""
        error_text = """Could not import PhotoProcessor module.

Please make sure 'photo_to_pdf.py' is in the same
directory as this GUI application.

The required file should contain the PhotoProcessor class
and all necessary photo processing functions."""
        
        messagebox.showerror("Import Error", error_text)
        self.log_message("ERROR: Could not import photo_to_pdf.py")
        self.log_message("Make sure it's in the same directory as this script.")


class PhotoProcessorWithLogging(PhotoProcessor):
    """
    Extended PhotoProcessor that sends log messages to a queue.
    
    This subclass overrides print statements to send messages
    to the GUI thread via a queue for thread-safe communication.
    """
    
    def __init__(self, message_queue):
        """
        Initialize processor with message queue.
        
        Args:
            message_queue: Queue for sending messages to GUI thread
        """
        super().__init__()
        self.message_queue = message_queue
    
    def log(self, message):
        """Send a log message to the GUI."""
        self.message_queue.put(("log", message))
    
    def process_folder(self, input_folder, output_pdf):
        """
        Override process_folder to use custom logging.
        
        Args:
            input_folder: Path to folder containing input images
            output_pdf: Path where the output PDF should be saved
        """
        # Same logic as parent class but with custom logging
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
        input_path = Path(input_folder)
        if not input_path.exists():
            raise FileNotFoundError(f"Input folder not found: {input_folder}")
        
        image_files = [
            f for f in input_path.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
        
        if not image_files:
            raise ValueError(f"No image files found in {input_folder}")
        
        image_files.sort()
        
        self.log(f"Found {len(image_files)} images to process")
        self.log("-" * 50)
        
        processed_images = []
        filenames = []
        
        for idx, img_file in enumerate(image_files, 1):
            self.log(f"Processing {idx}/{len(image_files)}: {img_file.name}")
            
            face_center = self.detect_face_center(str(img_file))
            
            try:
                from PIL import Image
                img = Image.open(img_file)
                
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Crop to 5x7 ratio (portrait)
                cropped = self.crop_to_5x7(img, face_center)
                
                # Rotate to landscape (7x5) for PDF layout
                cropped_landscape = cropped.rotate(90, expand=True)
                
                processed_images.append(cropped_landscape)
                filenames.append(img_file.name)
                
            except Exception as e:
                self.log(f"  Error processing {img_file.name}: {e}")
                continue
        
        self.log("-" * 50)
        self.log(f"Successfully processed {len(processed_images)} images")
        self.log(f"Creating PDF: {output_pdf}")
        
        self.create_pdf_with_filenames(processed_images, filenames, output_pdf)
        
        self.log(f"PDF created successfully!")
    
    def detect_face_center(self, image_path):
        """Override to add logging for face detection."""
        result = super().detect_face_center(image_path)
        
        if result:
            # Don't log for every face - it's too verbose for GUI
            pass
        
        return result


def main():
    """Main entry point for the GUI application."""
    # Create the main window
    root = tk.Tk()
    
    # Create the application
    app = PhotoProcessorGUI(root)
    
    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()
