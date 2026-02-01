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
    ASPECT_RATIO = 5.0 / 7.0  # 5x7 photo ratio
    DPI = 300  # High quality for printing
    PHOTO_WIDTH_INCHES = 5.0
    PHOTO_HEIGHT_INCHES = 7.0
    
    # PDF layout constants (in points: 72 points = 1 inch)
    PAGE_WIDTH, PAGE_HEIGHT = letter  # 612 x 792 points (8.5 x 11 inches)
    MARGIN = 36  # 0.5 inch margin
    SPACING = 20  # Space between photos and text
    
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
    
    def add_filename_to_image(self, image: Image.Image, filename: str, font_size: int = 24) -> Image.Image:
        """
        Add filename text to the bottom of an image.
        
        Creates a new image with extra space at the bottom containing the filename.
        The text is centered and uses a clean sans-serif font.
        
        Args:
            image: PIL Image to add text to
            filename: Text to display (typically the original filename)
            font_size: Size of the font in points
            
        Returns:
            New PIL Image with filename label at the bottom
        """
        # Calculate dimensions for the new image with text area
        text_height = font_size + 20  # Extra padding around text
        new_height = image.height + text_height
        
        # Create new image with white background
        new_image = Image.new('RGB', (image.width, new_height), 'white')
        
        # Paste original image at the top
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
        
        # Get text bounding box to center it
        bbox = draw.textbbox((0, 0), filename, font=font)
        text_width = bbox[2] - bbox[0]
        text_height_actual = bbox[3] - bbox[1]
        
        # Calculate position to center text horizontally
        x = (image.width - text_width) // 2
        y = image.height + (text_height - text_height_actual) // 2
        
        # Draw the text in black
        draw.text((x, y), filename, fill='black', font=font)
        
        return new_image
    
    def process_folder(self, input_folder: str, output_pdf: str):
        """
        Main processing function: loads all images, crops them, and creates PDF.
        
        This orchestrates the entire workflow:
        1. Find all image files in the input folder
        2. Detect faces and crop each image to 5x7
        3. Add filename labels
        4. Arrange images on 8.5x11 pages (2 per page)
        5. Generate lossless PDF
        
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
                
                # Crop to 5x7 ratio
                cropped = self.crop_to_5x7(img, face_center)
                
                # Add filename label
                labeled = self.add_filename_to_image(cropped, img_file.name)
                
                processed_images.append(labeled)
                
            except Exception as e:
                print(f"  Error processing {img_file.name}: {e}")
                continue
        
        print("-" * 50)
        print(f"Successfully processed {len(processed_images)} images")
        print(f"Creating PDF: {output_pdf}")
        
        # Create the PDF
        self.create_pdf(processed_images, output_pdf)
        
        print(f"PDF created successfully: {output_pdf}")
    
    def create_pdf(self, images: List[Image.Image], output_path: str):
        """
        Create a PDF with 2 images per page, arranged vertically.
        
        Images are saved losslessly using PNG compression to maintain quality.
        Each 8.5x11 page contains two 5x7 photos with their filenames.
        
        Args:
            images: List of PIL Image objects (already cropped and labeled)
            output_path: Path where PDF should be saved
        """
        # Create PDF canvas
        c = canvas.Canvas(output_path, pagesize=letter)
        
        # Calculate photo dimensions in points (1 inch = 72 points)
        photo_width_pts = self.PHOTO_WIDTH_INCHES * 72
        photo_height_pts = self.PHOTO_HEIGHT_INCHES * 72
        
        # We'll add text height separately since we added it to the image
        # But we need to account for it in positioning
        
        # Process images in pairs (2 per page)
        for i in range(0, len(images), 2):
            # Center photos horizontally on the page
            x_position = (self.PAGE_WIDTH - photo_width_pts) / 2
            
            # First photo: positioned from top with margin
            y_position_top = self.PAGE_HEIGHT - self.MARGIN - photo_height_pts
            
            # Draw first photo
            img1_buffer = io.BytesIO()
            # Save as PNG for lossless compression
            images[i].save(img1_buffer, format='PNG', compress_level=9)
            img1_buffer.seek(0)
            
            # Scale image to fit exact dimensions
            c.drawImage(
                ImageReader(img1_buffer),
                x_position,
                y_position_top,
                width=photo_width_pts,
                height=photo_height_pts,
                preserveAspectRatio=True
            )
            
            # Draw second photo if it exists
            if i + 1 < len(images):
                # Position second photo below first with spacing
                y_position_bottom = y_position_top - photo_height_pts - self.SPACING
                
                img2_buffer = io.BytesIO()
                images[i + 1].save(img2_buffer, format='PNG', compress_level=9)
                img2_buffer.seek(0)
                
                c.drawImage(
                    ImageReader(img2_buffer),
                    x_position,
                    y_position_bottom,
                    width=photo_width_pts,
                    height=photo_height_pts,
                    preserveAspectRatio=True
                )
            
            # Move to next page (unless this is the last page)
            if i + 2 < len(images):
                c.showPage()
        
        # Save the PDF
        c.save()


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
