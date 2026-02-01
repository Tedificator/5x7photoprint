#!/usr/bin/env python3
"""
Test Script for Photo to PDF Processor
=======================================

This script verifies that all dependencies are installed correctly
and demonstrates basic usage of the PhotoProcessor class.

Usage:
    python test_processor.py
"""

import sys
import os

def test_imports():
    """Test that all required libraries can be imported."""
    print("Testing imports...")
    
    try:
        import PIL
        print("✓ PIL/Pillow imported successfully")
        print(f"  Version: {PIL.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import PIL/Pillow: {e}")
        return False
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
        print(f"  Version: {cv2.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import OpenCV: {e}")
        return False
    
    try:
        import reportlab
        print("✓ ReportLab imported successfully")
        print(f"  Version: {reportlab.Version}")
    except ImportError as e:
        print(f"✗ Failed to import ReportLab: {e}")
        return False
    
    return True


def test_face_cascade():
    """Test that the Haar cascade file can be loaded."""
    print("\nTesting face detection cascade...")
    
    try:
        import cv2
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        
        if not os.path.exists(cascade_path):
            print(f"✗ Cascade file not found at: {cascade_path}")
            return False
        
        cascade = cv2.CascadeClassifier(cascade_path)
        
        if cascade.empty():
            print("✗ Cascade classifier is empty")
            return False
        
        print("✓ Face detection cascade loaded successfully")
        print(f"  Location: {cascade_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error loading cascade: {e}")
        return False


def test_photo_processor():
    """Test that PhotoProcessor class can be instantiated."""
    print("\nTesting PhotoProcessor class...")
    
    try:
        from photo_to_pdf import PhotoProcessor
        
        processor = PhotoProcessor()
        print("✓ PhotoProcessor instantiated successfully")
        
        # Test aspect ratio calculation
        expected_ratio = 5.0 / 7.0
        if abs(processor.ASPECT_RATIO - expected_ratio) < 0.0001:
            print(f"✓ Aspect ratio correct: {processor.ASPECT_RATIO:.4f}")
        else:
            print(f"✗ Aspect ratio incorrect: {processor.ASPECT_RATIO}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error instantiating PhotoProcessor: {e}")
        return False


def create_sample_image():
    """Create a sample test image for demonstration."""
    print("\nCreating sample test image...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple test image
        width, height = 2100, 1500  # 7x5 inches at 300 DPI
        img = Image.new('RGB', (width, height), color='lightblue')
        
        draw = ImageDraw.Draw(img)
        
        # Draw a simple "face" (circle)
        face_size = 400
        face_x = width // 2
        face_y = height // 2
        draw.ellipse(
            [face_x - face_size//2, face_y - face_size//2,
             face_x + face_size//2, face_y + face_size//2],
            fill='peachpuff',
            outline='black',
            width=3
        )
        
        # Draw eyes
        eye_size = 60
        eye_offset = 120
        # Left eye
        draw.ellipse(
            [face_x - eye_offset - eye_size//2, face_y - 80 - eye_size//2,
             face_x - eye_offset + eye_size//2, face_y - 80 + eye_size//2],
            fill='black'
        )
        # Right eye
        draw.ellipse(
            [face_x + eye_offset - eye_size//2, face_y - 80 - eye_size//2,
             face_x + eye_offset + eye_size//2, face_y - 80 + eye_size//2],
            fill='black'
        )
        
        # Draw smile
        draw.arc(
            [face_x - 150, face_y - 50, face_x + 150, face_y + 150],
            start=0,
            end=180,
            fill='black',
            width=5
        )
        
        # Add text
        text = "Test Image"
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) // 2, 100), text, fill='navy', font=font)
        
        # Create test directory if it doesn't exist
        test_dir = 'test_images'
        os.makedirs(test_dir, exist_ok=True)
        
        # Save the image
        img_path = os.path.join(test_dir, 'sample_photo.jpg')
        img.save(img_path, 'JPEG', quality=95)
        
        print(f"✓ Sample image created: {img_path}")
        print(f"  Dimensions: {width}x{height} pixels")
        return test_dir
        
    except Exception as e:
        print(f"✗ Error creating sample image: {e}")
        return None


def run_test_processing(test_dir):
    """Run a test of the full processing pipeline."""
    print("\nRunning test processing...")
    
    try:
        from photo_to_pdf import PhotoProcessor
        
        processor = PhotoProcessor()
        output_pdf = 'test_output.pdf'
        
        print(f"  Processing images from: {test_dir}")
        print(f"  Output PDF: {output_pdf}")
        
        processor.process_folder(test_dir, output_pdf)
        
        if os.path.exists(output_pdf):
            file_size = os.path.getsize(output_pdf)
            print(f"✓ Test PDF created successfully")
            print(f"  File size: {file_size:,} bytes")
            print(f"  Location: {os.path.abspath(output_pdf)}")
            return True
        else:
            print("✗ PDF was not created")
            return False
            
    except Exception as e:
        print(f"✗ Error during test processing: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Photo to PDF Processor - Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
        print("\n⚠ Import test failed. Please install dependencies:")
        print("  pip install -r requirements.txt")
        return
    
    # Test face cascade
    if not test_face_cascade():
        all_passed = False
    
    # Test PhotoProcessor class
    if not test_photo_processor():
        all_passed = False
    
    # Create sample image and test processing
    test_dir = create_sample_image()
    if test_dir:
        if not run_test_processing(test_dir):
            all_passed = False
    else:
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        print("\nYou can now use the script:")
        print("  python photo_to_pdf.py <input_folder> <output.pdf>")
        print("\nOr try the test output:")
        print("  Open test_output.pdf to see the sample result")
    else:
        print("✗ Some tests failed")
        print("Please check the error messages above and fix any issues")
    print("=" * 60)


if __name__ == "__main__":
    main()
