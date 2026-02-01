#!/usr/bin/env python3
"""
Photo to PDF Processor
======================

This script processes a folder of photos by:
1. Detecting faces in each image
2. Cropping images to a 5x7 aspect ratio, centered on detected faces
3. Arranging 2 photos per 8.5x11 inch page
4. Adding filenames as labels
5. Saving everything as a lossless PDF

Requirements:
    pip install Pillow opencv-python reportlab

Usage:
    python photo_to_pdf.py input_folder output.pdf

Author: Claude
Date: 2026-02-01
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import cv2
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io


class PhotoProcessor:
    """
    Main class for processing photos and generating PDFs.
    
    Attributes:
        ASPECT_RATIO (float): Target aspect ratio (5/7 for 5x7 photos)
        DPI (int): Dots per inch for high-quality output
        PHOTO_WIDTH_INCHES (float): Photo width in inches
        PHOTO_HEIGHT_INCHES (float): Photo height in inches
    """
    
    # Constants for photo dimensions and quality
    ASPECT_RATIO = 5.0 / 7.0  # 5x7 photo ratio (before rotation)
    DPI = 300  # High quality for printing
    PHOTO_WIDTH_INCHES = 7.0   # Width when landscape (was 5.0)
    PHOTO_HEIGHT_INCHES = 5.0  # Height when landscape (was 7.0)
    
    # PDF layout constants (in points: 72 points = 1 inch)
    PAGE_WIDTH, PAGE_HEIGHT = letter  # 612 x 792 points (8.5 x 11 inches)
    MARGIN = 36  # 0.5 inch margin (0.5 * 72)
    SPACING = 10  # Space between photos (reduced for tighter layout)
    TEXT_FONT_SIZE = 5  # Small font for filename labels
    
    def __init__(self, face_cascade_path: Optional[str] = None):
        """
        Initialize the PhotoProcessor.
        
        Args:
            face_cascade_path: Optional path to custom Haar cascade XML file.
                             If None, uses OpenCV's default frontal face cascade.
        """
        # Load the Haar Cascade classifier for face detection
        if face_cascade_path and os.path.exists(face_cascade_path):
            self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        else:
            # Use OpenCV's pre-trained frontal face detector
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
        if self.face_cascade.empty():
            raise RuntimeError("Failed to load face detection cascade")
    
    def detect_face_center(self, image_path: str) -> Optional[Tuple[int, int]]:
        """
        Detect faces in an image and return the average center point.
        
        This method uses OpenCV's Haar Cascade classifier to detect faces.
        If multiple faces are found, it returns the average center point
        of all detected faces.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (x, y) coordinates representing the average face center,
            or None if no faces are detected
        """
        # Load image in grayscale for face detection (faster and more reliable)
        img = cv2.imread(image_path)
        if img is None:
            print(f"Warning: Could not load {image_path}")
            return None
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        # Parameters:
        #   scaleFactor: compensates for faces closer/farther from camera
        #   minNeighbors: higher value = fewer but more reliable detections
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            return None
        
        # Calculate average center of all detected faces
        total_x = 0
        total_y = 0
        for (x, y, w, h) in faces:
            # Center of each face rectangle
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            total_x += face_center_x
            total_y += face_center_y
        
        avg_x = total_x // len(faces)
        avg_y = total_y // len(faces)
        
        print(f"  Found {len(faces)} face(s) in {os.path.basename(image_path)}")
        return (avg_x, avg_y)
    
    def crop_to_5x7(self, image: Image.Image, face_center: Optional[Tuple[int, int]] = None) -> Image.Image:
        """
        Crop an image to 5x7 aspect ratio, maximizing the smaller dimension.
        
        The crop is centered on detected faces if available, otherwise centered
        on the image. The algorithm ensures we get the largest possible 5x7 crop
        without letterboxing or distortion.
        
        Args:
            image: PIL Image object to crop
            face_center: Optional (x, y) tuple of face center coordinates
            
        Returns:
            Cropped PIL Image object with 5x7 aspect ratio
        """
        width, height = image.size
        current_ratio = width / height
        
        # Determine crop dimensions based on which dimension is limiting
        if current_ratio > self.ASPECT_RATIO:
            # Image is wider than 5:7 ratio - height is the limiting dimension
            # We'll use full height and crop the width
            new_height = height
            new_width = int(height * self.ASPECT_RATIO)
        else:
            # Image is taller than 5:7 ratio - width is the limiting dimension
            # We'll use full width and crop the height
            new_width = width
            new_height = int(width / self.ASPECT_RATIO)
        
        # Determine center point for cropping
        if face_center:
            center_x, center_y = face_center
        else:
            # No faces detected - use image center
            center_x, center_y = width // 2, height // 2
        
        # Calculate crop box, ensuring it stays within image bounds
        # We want to center on face_center but constrain to image boundaries
        left = center_x - new_width // 2
        top = center_y - new_height // 2
        
        # Constrain to image boundaries
        left = max(0, min(left, width - new_width))
        top = max(0, min(top, height - new_height))
        
        right = left + new_width
        bottom = top + new_height
        
        # Perform the crop
        cropped = image.crop((left, top, right, bottom))
        
        return cropped
    
    def add_filename_to_image(self, image: Image.Image, filename: str, font_size: int = 12) -> Image.Image:
        """
        Add filename text to the right side of an image.
        
        For landscape 7x5 photos, adds the filename vertically on the right edge.
        The text is small (5pt default in PDF) but readable for identification.
        
        Args:
            image: PIL Image to add text to
            filename: Text to display (typically the original filename)
            font_size: Size of the font in points (default 12 for image, scaled in PDF)
            
        Returns:
            New PIL Image with filename label on the right side
        """
        # We'll add a small strip on the right for the filename
        text_width = 40  # Small strip on the right side
        new_width = image.width + text_width
        
        # Create new image with white background
        new_image = Image.new('RGB', (new_width, image.height), 'white')
        
        # Paste original image on the left
        new_image.paste(image, (0, 0))
        
        # Prepare to draw text
        draw = ImageDraw.Draw(new_image)
        
        # Try to load a nice font, fall back to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                # Use default font as last resort
                font = ImageFont.load_default()
        
        # Rotate text to be vertical
        # Create a temporary image for the text
        temp_img = Image.new('RGB', (image.height, text_width), 'white')
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Draw text on temp image (will be rotated)
        # Position text in the middle of the temp image
        bbox = temp_draw.textbbox((0, 0), filename, font=font)
        text_height = bbox[3] - bbox[1]
        text_x = (image.height - text_height) // 2
        text_y = (text_width - (bbox[2] - bbox[0])) // 2
        
        temp_draw.text((text_x, text_y), filename, fill='black', font=font)
        
        # Rotate temp image 90 degrees counter-clockwise
        rotated_text = temp_img.rotate(90, expand=True)
        
        # Paste rotated text onto the right side
        new_image.paste(rotated_text, (image.width, 0))
        
        return new_image
    
    def process_folder(self, input_folder: str, output_pdf: str):
        """
        Main processing function: loads all images, crops them, and creates PDF.
        
        This orchestrates the entire workflow:
        1. Find all image files in the input folder
        2. Detect faces and crop each image to 5x7
        3. Rotate to landscape orientation (7x5)
        4. Arrange images on 8.5x11 pages (2 per page)
        5. Generate lossless PDF with filenames
        
        Args:
            input_folder: Path to folder containing input images
            output_pdf: Path where the output PDF should be saved
        """
        # Supported image formats
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
        # Find all image files in the input folder
        input_path = Path(input_folder)
        if not input_path.exists():
            raise FileNotFoundError(f"Input folder not found: {input_folder}")
        
        image_files = [
            f for f in input_path.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
        
        if not image_files:
            raise ValueError(f"No image files found in {input_folder}")
        
        # Sort files for consistent ordering
        image_files.sort()
        
        print(f"Found {len(image_files)} images to process")
        print("-" * 50)
        
        # Process each image
        processed_images = []
        filenames = []
        
        for img_file in image_files:
            print(f"Processing: {img_file.name}")
            
            # Detect faces
            face_center = self.detect_face_center(str(img_file))
            
            # Load image with PIL
            try:
                img = Image.open(img_file)
                
                # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Crop to 5x7 ratio (portrait)
                cropped = self.crop_to_5x7(img, face_center)
                
                # Rotate to landscape (7x5) for PDF layout
                # The cropped image is portrait (5 wide x 7 tall)
                # We need it landscape (7 wide x 5 tall)
                cropped_landscape = cropped.rotate(90, expand=True)
                
                processed_images.append(cropped_landscape)
                filenames.append(img_file.name)
                
            except Exception as e:
                print(f"  Error processing {img_file.name}: {e}")
                continue
        
        print("-" * 50)
        print(f"Successfully processed {len(processed_images)} images")
        print(f"Creating PDF: {output_pdf}")
        
        # Create the PDF with filenames
        self.create_pdf_with_filenames(processed_images, filenames, output_pdf)
        
        print(f"PDF created successfully: {output_pdf}")
    
    def create_pdf_with_filenames(self, images: List[Image.Image], filenames: List[str], output_path: str):
        """
        Create a PDF with 2 landscape images per page with filename labels.
        
        This is a wrapper around create_pdf that includes filename information.
        
        Args:
            images: List of PIL Image objects (already cropped and rotated to landscape)
            filenames: List of original filenames corresponding to each image
            output_path: Path where PDF should be saved
        """
        # Store filenames for use in get_original_filename
        self._current_filenames = filenames
        
        # Call the main PDF creation method
        self.create_pdf(images, output_path)
        
        # Clean up
        self._current_filenames = None
    
    def create_pdf(self, images: List[Image.Image], output_path: str):
        """
        Create a PDF with 2 landscape images per page, arranged vertically.
        
        Images are 7x5 inches (landscape orientation) and are positioned to fit
        perfectly on an 8.5x11 inch portrait page with 0.5 inch margins.
        
        Layout:
        - Page: 8.5" wide x 11" tall (portrait)
        - Photos: 7" wide x 5" tall (landscape)
        - Margins: 0.5" on all sides
        - Available space: 7.5" wide x 10" tall
        - Two photos vertically with spacing between
        
        Args:
            images: List of PIL Image objects (already cropped and labeled)
            output_path: Path where PDF should be saved
        """
        # Create PDF canvas
        c = canvas.Canvas(output_path, pagesize=letter)
        
        # Calculate photo dimensions in points (1 inch = 72 points)
        photo_width_pts = self.PHOTO_WIDTH_INCHES * 72    # 7" = 504 points
        photo_height_pts = self.PHOTO_HEIGHT_INCHES * 72  # 5" = 360 points
        
        # Calculate positions to center photos horizontally with proper margins
        # Page width is 8.5" = 612 points
        # Photo width is 7" = 504 points
        # Left margin = (612 - 504) / 2 = 54 points = 0.75"
        # This gives us 0.75" margins on left and right (slightly more than 0.5" minimum)
        x_position = (self.PAGE_WIDTH - photo_width_pts) / 2
        
        # Calculate vertical positions for two photos
        # Page height is 11" = 792 points
        # Each photo is 5" = 360 points
        # Total photo height = 2 * 360 = 720 points
        # Remaining space = 792 - 720 = 72 points = 1"
        # We want 0.5" top margin, 0.5" bottom margin, and space between photos
        # Top margin = 36 points (0.5")
        # Bottom margin = 36 points (0.5")
        # Space between = 72 - 36 - 36 = 0 points
        # Actually let's distribute: top=0.5", spacing=0.25", bottom=0.25" (total 1")
        
        top_margin = 36  # 0.5 inch
        spacing_between = 18  # 0.25 inch between photos
        
        # First photo: positioned from top
        y_position_top = self.PAGE_HEIGHT - top_margin - photo_height_pts
        
        # Second photo: positioned below first with spacing
        y_position_bottom = y_position_top - spacing_between - photo_height_pts
        
        # Process images in pairs (2 per page)
        for i in range(0, len(images), 2):
            # Draw first photo
            img1_buffer = io.BytesIO()
            # Rotate image to landscape if it's not already
            img1 = images[i]
            if img1.height > img1.width:
                img1 = img1.rotate(90, expand=True)
            
            # Save as PNG for lossless compression
            img1.save(img1_buffer, format='PNG', compress_level=9)
            img1_buffer.seek(0)
            
            # Draw first image
            c.drawImage(
                ImageReader(img1_buffer),
                x_position,
                y_position_top,
                width=photo_width_pts,
                height=photo_height_pts,
                preserveAspectRatio=True
            )
            
            # Draw filename text for first photo (small, 5pt)
            # Position text just below the photo
            text_y = y_position_top - 8  # 8 points below photo
            c.setFont("Helvetica", self.TEXT_FONT_SIZE)
            c.setFillColorRGB(0, 0, 0)  # Black text
            
            # Get original filename (strip the added text area info)
            # Text is centered below the photo
            filename1 = self.get_original_filename(i, len(images))
            text_width = c.stringWidth(filename1, "Helvetica", self.TEXT_FONT_SIZE)
            text_x = x_position + (photo_width_pts - text_width) / 2
            c.drawString(text_x, text_y, filename1)
            
            # Draw second photo if it exists
            if i + 1 < len(images):
                img2 = images[i + 1]
                if img2.height > img2.width:
                    img2 = img2.rotate(90, expand=True)
                
                img2_buffer = io.BytesIO()
                img2.save(img2_buffer, format='PNG', compress_level=9)
                img2_buffer.seek(0)
                
                c.drawImage(
                    ImageReader(img2_buffer),
                    x_position,
                    y_position_bottom,
                    width=photo_width_pts,
                    height=photo_height_pts,
                    preserveAspectRatio=True
                )
                
                # Draw filename text for second photo
                text_y2 = y_position_bottom - 8
                filename2 = self.get_original_filename(i + 1, len(images))
                text_width2 = c.stringWidth(filename2, "Helvetica", self.TEXT_FONT_SIZE)
                text_x2 = x_position + (photo_width_pts - text_width2) / 2
                c.drawString(text_x2, text_y2, filename2)
            
            # Move to next page (unless this is the last page)
            if i + 2 < len(images):
                c.showPage()
        
        # Save the PDF
        c.save()
    
    def get_original_filename(self, index: int, total: int) -> str:
        """
        Helper method to get the original filename for display in PDF.
        
        Args:
            index: Index of the current image
            total: Total number of images
            
        Returns:
            Original filename or placeholder
        """
        if hasattr(self, '_current_filenames') and self._current_filenames:
            return self._current_filenames[index]
        return f"Photo {index + 1}"


def main():
    """
    Command-line interface for the photo processor.
    
    Usage:
        python photo_to_pdf.py <input_folder> <output_pdf>
    
    Example:
        python photo_to_pdf.py ./family_photos output.pdf
    """
    if len(sys.argv) != 3:
        print("Usage: python photo_to_pdf.py <input_folder> <output_pdf>")
        print("\nExample:")
        print("  python photo_to_pdf.py ./photos family_album.pdf")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_pdf = sys.argv[2]
    
    try:
        # Create processor and run
        processor = PhotoProcessor()
        processor.process_folder(input_folder, output_pdf)
        
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
