# Quick Reference Guide

## Installation (One-Time Setup)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python test_processor.py
```

## Basic Usage

```bash
# Process a folder of photos
python photo_to_pdf.py <folder> <output.pdf>

# Example
python photo_to_pdf.py ./wedding_photos wedding_album.pdf
```

## Common Tasks

### 1. Process Photos from Current Directory
```bash
python photo_to_pdf.py . my_photos.pdf
```

### 2. Process Photos from Subdirectory
```bash
python photo_to_pdf.py ./family_reunion/photos reunion_2024.pdf
```

### 3. Process with Absolute Paths
```bash
python photo_to_pdf.py /home/user/Pictures/vacation vacation.pdf
```

### 4. Run Tests
```bash
python test_processor.py
```

## What the Script Does

1. ✓ Finds all images in the folder (.jpg, .png, .bmp, .tiff)
2. ✓ Detects faces in each image
3. ✓ Crops to 5x7 ratio centered on faces
4. ✓ Adds filename below each photo
5. ✓ Arranges 2 photos per 8.5x11 page
6. ✓ Saves as high-quality PDF (300 DPI, lossless)

## File Structure

```
your-project/
├── photo_to_pdf.py      # Main script
├── requirements.txt     # Dependencies
├── test_processor.py    # Test script
├── README.md           # Full documentation
└── QUICK_REFERENCE.md  # This file
```

## Expected Output

**Input**: Folder with 10 photos
**Output**: PDF with 5 pages (2 photos per page)

Each photo will be:
- 5 inches wide × 7 inches tall
- Cropped to maximize the image
- Centered on detected faces (if any)
- Labeled with original filename

## Troubleshooting Quick Fixes

### "No module named 'cv2'"
```bash
pip install opencv-python
```

### "No module named 'PIL'"
```bash
pip install Pillow
```

### "No module named 'reportlab'"
```bash
pip install reportlab
```

### "No image files found"
- Check folder path is correct
- Ensure images have extensions: .jpg, .jpeg, .png, .bmp, .tiff
- Try absolute path instead of relative path

### PDF quality is poor
- Source images must be high resolution (1500×2100+ pixels)
- Script outputs at 300 DPI - quality depends on source
- Check source images aren't already heavily compressed

## Customization

### Change Photo Size
Edit `photo_to_pdf.py`, modify these lines in `PhotoProcessor` class:
```python
PHOTO_WIDTH_INCHES = 5.0   # Change width
PHOTO_HEIGHT_INCHES = 7.0  # Change height
ASPECT_RATIO = PHOTO_WIDTH_INCHES / PHOTO_HEIGHT_INCHES
```

### Change DPI (Quality)
```python
DPI = 300  # Higher = better quality, larger file size
```

### Change Page Margins
```python
MARGIN = 36  # in points (72 points = 1 inch)
```

### Photos per Page
Changing this requires modifying the `create_pdf()` method layout logic.

## Performance

| Photos | Processing Time | PDF Size |
|--------|----------------|----------|
| 10     | ~10 seconds    | ~15 MB   |
| 50     | ~1 minute      | ~75 MB   |
| 100    | ~2 minutes     | ~150 MB  |
| 500    | ~10 minutes    | ~750 MB  |

*Times approximate on modern laptop*

## Command Cheat Sheet

```bash
# Install
pip install -r requirements.txt

# Test
python test_processor.py

# Use
python photo_to_pdf.py <folder> <output.pdf>

# Check Python version
python --version

# List installed packages
pip list | grep -E "(Pillow|opencv|reportlab)"
```

## Getting Help

1. Read README.md for detailed documentation
2. Run test_processor.py to verify setup
3. Check error messages for specific issues
4. Ensure Python 3.7+ is installed

## Example Workflow

```bash
# 1. Download photos to a folder
mkdir vacation_photos
# ... copy photos into folder ...

# 2. Process them
python photo_to_pdf.py vacation_photos vacation_album.pdf

# 3. Check output
# Open vacation_album.pdf

# 4. If satisfied, send to printer!
```

## Pro Tips

- **Sort photos first**: Rename files with numbers (01_beach.jpg, 02_dinner.jpg) for specific ordering
- **High resolution**: Use photos at least 1500×2100 pixels for best quality
- **Face detection**: Works best with clear, front-facing portraits
- **Batch processing**: Process photos in groups of 50-100 for easier management
- **Backup originals**: Keep original photos in a separate folder
- **Test first**: Run on a small batch to check cropping before processing hundreds

## Quick Validation

After running the script, check:
- ✓ PDF file was created
- ✓ File size seems reasonable (≈1.5MB per photo)
- ✓ Open PDF and verify quality
- ✓ Check that faces aren't cropped awkwardly
- ✓ Verify filenames are readable

---

**Ready to use?**
```bash
python photo_to_pdf.py my_photos output.pdf
```
