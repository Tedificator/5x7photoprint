# Photo to PDF Processor

A Python script that automatically processes photos for printing by detecting faces, cropping to 5x7 ratio, and arranging them on 8.5x11 inch pages in a PDF format.

## Features

- **Face Detection**: Automatically detects faces in photos using OpenCV's Haar Cascade classifier
- **Smart Cropping**: Crops images to 5x7 aspect ratio, centered on detected faces
- **Face-Centered**: When multiple faces are detected, crops around the average center point
- **Fallback Centering**: If no faces are detected, centers the crop on the image
- **PDF Generation**: Creates a lossless PDF with 2 photos per 8.5x11 inch page
- **Filename Labels**: Each photo includes its original filename for easy identification
- **High Quality**: 300 DPI output suitable for professional printing
- **Lossless Compression**: Uses PNG compression to preserve image quality

## Requirements

### Python Version
- Python 3.7 or higher

### Dependencies
```bash
pip install Pillow opencv-python reportlab
```

Or install from requirements file:
```bash
pip install -r requirements.txt
```

## Installation

1. **Clone or download the script**:
   ```bash
   wget https://example.com/photo_to_pdf.py
   # or just copy the photo_to_pdf.py file to your project
   ```

2. **Install dependencies**:
   ```bash
   pip install Pillow opencv-python reportlab
   ```

3. **Verify installation**:
   ```bash
   python photo_to_pdf.py
   # Should show usage instructions
   ```

## Usage

### Basic Usage

```bash
python photo_to_pdf.py <input_folder> <output_pdf>
```

### Examples

**Process a folder of family photos:**
```bash
python photo_to_pdf.py ./family_photos family_album.pdf
```

**Process vacation photos:**
```bash
python photo_to_pdf.py /home/user/Pictures/vacation2024 vacation_2024.pdf
```

**Relative paths:**
```bash
python photo_to_pdf.py ../photos output.pdf
```

## How It Works

### 1. Face Detection
- Uses OpenCV's Haar Cascade classifier to detect faces
- Supports multiple faces per image
- Calculates average center point when multiple faces are found
- Falls back to image center if no faces detected

### 2. Cropping Algorithm
The script crops images to exactly 5:7 aspect ratio using this logic:

```
IF image_width/image_height > 5/7:
    # Image is wider than target ratio
    - Use full height
    - Crop width to match 5:7 ratio
ELSE:
    # Image is taller than target ratio
    - Use full width
    - Crop height to match 5:7 ratio

THEN center crop box on:
    - Average face location (if faces detected)
    - Image center (if no faces)
```

### 3. PDF Layout
- Page size: 8.5 x 11 inches (US Letter)
- Photos per page: 2 (arranged vertically)
- Photo size: 5 x 7 inches each
- Margins: 0.5 inches
- Spacing between photos: 20 points (~0.28 inches)
- Resolution: 300 DPI for high-quality printing

### 4. Output Quality
- Compression: PNG (lossless)
- Color space: RGB
- Suitable for professional printing services

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff, .tif)

## Advanced Usage

### Customizing the Script

You can modify these constants in the `PhotoProcessor` class:

```python
# Change photo dimensions (currently 5x7)
PHOTO_WIDTH_INCHES = 5.0
PHOTO_HEIGHT_INCHES = 7.0

# Change output quality (currently 300 DPI)
DPI = 300

# Change page margins (currently 0.5 inches)
MARGIN = 36  # in points (72 points = 1 inch)

# Change spacing between photos
SPACING = 20  # in points
```

### Using as a Library

You can also import and use the processor programmatically:

```python
from photo_to_pdf import PhotoProcessor

# Create processor
processor = PhotoProcessor()

# Process folder
processor.process_folder('input_folder', 'output.pdf')

# Or process individual images
from PIL import Image

img = Image.open('photo.jpg')
face_center = processor.detect_face_center('photo.jpg')
cropped = processor.crop_to_5x7(img, face_center)
labeled = processor.add_filename_to_image(cropped, 'photo.jpg')
```

## Troubleshooting

### "Failed to load face detection cascade"
**Problem**: OpenCV can't find the Haar cascade file.

**Solution**: Ensure opencv-python is properly installed:
```bash
pip uninstall opencv-python
pip install opencv-python
```

### "No image files found in folder"
**Problem**: The script doesn't recognize the images in your folder.

**Solution**: 
- Ensure your images have supported extensions (.jpg, .png, .bmp, .tiff)
- Check folder path is correct
- Ensure you have read permissions on the folder

### Low Quality Output
**Problem**: Images appear blurry or pixelated.

**Solution**: 
- Ensure source images are high resolution (at least 1500x2100 pixels for 5x7 at 300 DPI)
- Check that images aren't already heavily compressed
- The script uses lossless PNG compression, so quality loss comes from source images

### Photos Cutting Off Faces
**Problem**: Important parts of faces are being cropped out.

**Solution**: 
- The algorithm centers on average face location
- For group photos with faces far apart, some may be cut off
- Consider using wider aspect ratio or processing faces individually
- Manual cropping may be needed for some photos

### Memory Issues with Large Folders
**Problem**: Script crashes or runs out of memory with hundreds of photos.

**Solution**:
- Process photos in smaller batches
- Reduce source image resolution before processing
- Close other applications to free up RAM

### Wrong Face Detection
**Problem**: Script detects faces that aren't there or misses real faces.

**Solution**:
- Face detection isn't perfect
- Adjust detection parameters in `detect_face_center()`:
  ```python
  faces = self.face_cascade.detectMultiScale(
      gray,
      scaleFactor=1.1,    # Try values between 1.05-1.3
      minNeighbors=5,     # Try values between 3-8
      minSize=(30, 30)    # Adjust minimum face size
  )
  ```

## Technical Details

### Face Detection Algorithm
Uses OpenCV's Haar Cascade Classifier:
- Pre-trained on thousands of face images
- Fast and efficient for real-time detection
- Works on grayscale images
- Returns bounding boxes: (x, y, width, height)

### Cropping Math
For an image with dimensions W×H:

**If W/H > 5/7** (wide image):
- new_height = H
- new_width = H × (5/7)
- Crop horizontally, keep full height

**If W/H ≤ 5/7** (tall image):
- new_width = W  
- new_height = W × (7/5)
- Crop vertically, keep full width

Center point constrained to valid range:
```
left = max(0, min(center_x - new_width/2, W - new_width))
top = max(0, min(center_y - new_height/2, H - new_height))
```

### PDF Coordinate System
ReportLab uses bottom-left origin:
- (0, 0) is bottom-left corner
- X increases rightward
- Y increases upward
- Units are in points (72 points = 1 inch)

Page layout calculation:
```
Letter size: 612 × 792 points (8.5 × 11 inches)
Photo size: 360 × 504 points (5 × 7 inches)
Margin: 36 points (0.5 inches)

First photo Y: 792 - 36 - 504 = 252 points from bottom
Second photo Y: First_Y - 504 - 20 = below first photo
```

## Performance

Typical processing times on a modern laptop:
- Face detection: ~0.1-0.5 seconds per image
- Cropping: ~0.01 seconds per image  
- PDF generation: ~0.1 seconds per page
- **Total**: ~0.5-1 seconds per image

For 100 photos: ~1-2 minutes total processing time

## License

This script is provided as-is for personal and commercial use.

## Contributing

Suggestions for improvements:
- [ ] Add support for custom aspect ratios
- [ ] Implement better face detection (dlib, face_recognition library)
- [ ] Add GUI interface
- [ ] Support for multiple photos per page (e.g., 4x6 grid)
- [ ] Add image enhancement options (brightness, contrast, sharpness)
- [ ] Batch processing with progress bar
- [ ] Support for portrait/landscape orientation mixing

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Ensure all dependencies are correctly installed
3. Verify your Python version is 3.7+
4. Check that input images are in supported formats

## Version History

- **1.0.0** (2026-02-01): Initial release
  - Face detection and smart cropping
  - 5x7 ratio with 2 photos per page
  - Lossless PDF output
  - Filename labeling
