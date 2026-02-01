# GUI User Guide

## Quick Start with the Graphical Interface

The Photo to PDF Processor includes an easy-to-use graphical interface that requires no command-line knowledge.

## Installation

1. **Install Python** (if you haven't already):
   - Download from https://www.python.org/downloads/
   - Version 3.7 or higher required

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the GUI**:
   ```bash
   python photo_to_pdf_gui.py
   ```
   
   Or on Windows, you can double-click `photo_to_pdf_gui.py` if Python is set up correctly.

## GUI Overview

When you launch the application, you'll see a window with several sections:

### 1. Select Input Folder
- **Purpose**: Choose the folder containing your photos
- **Action**: Click the "Browse..." button
- **Result**: The path appears in the text field, and the app counts how many images it found

### 2. Choose Output PDF
- **Purpose**: Decide where to save your PDF
- **Action**: Click the "Browse..." button
- **Result**: You can name your PDF and choose the save location

### 3. Process Photos
- **Purpose**: Start the processing
- **Action**: Click "Start Processing" (enabled once steps 1 & 2 are complete)
- **Result**: Progress bar shows activity, log displays what's happening

### 4. Processing Log
- **Purpose**: See detailed information about what's happening
- **Shows**: 
  - Which photos are being processed
  - Face detection results
  - Any errors or warnings
  - Completion status

## Step-by-Step Tutorial

### Basic Usage

1. **Launch the Application**
   ```bash
   python photo_to_pdf_gui.py
   ```

2. **Select Your Photos**
   - Click "Browse..." next to "Select Input Folder"
   - Navigate to the folder with your photos
   - Click "Select Folder" (or "Choose" on Mac)
   - The app will show: "✓ Found X images to process"

3. **Choose Output Location**
   - Click "Browse..." next to "Choose Output PDF"
   - Navigate to where you want to save the PDF
   - Type a filename (e.g., "family_photos.pdf")
   - Click "Save"

4. **Start Processing**
   - Click the "Start Processing" button
   - Watch the progress bar and log for updates
   - Wait for completion message

5. **View Your PDF**
   - When complete, a dialog asks if you want to open the folder
   - Click "Yes" to open the folder containing your PDF
   - Or click "No" and navigate there manually

## Features Explained

### Input Folder Selection
- **Supported formats**: JPG, JPEG, PNG, BMP, TIFF
- **Recursive search**: No - only looks in the selected folder, not subfolders
- **Image count**: Automatically counts valid images and displays the total
- **Warning**: Shows a warning if no images are found

### Output File Selection
- **Default extension**: .pdf is automatically added if you don't specify it
- **Overwrite warning**: System will warn you if the file already exists
- **Location**: Can be saved anywhere on your computer

### Progress Tracking
- **Progress bar**: Shows actual completion percentage (0-100%)
  - 0-80%: Processing individual photos
  - 80-95%: Creating PDF pages
  - 95-100%: Saving PDF to disk
- **Progress percentage**: Displays exact percentage (e.g., "45%")
- **Status label**: Shows current state:
  - "Ready to process" - waiting to start
  - "Processing photos..." - actively working
  - "✓ Complete!" - finished successfully
  - "✗ Error occurred" - something went wrong

### Processing Log
- **Real-time updates**: See each photo as it's processed
- **Face detection**: Shows when faces are detected
- **Errors**: Any problems are logged here
- **Scrollable**: Automatically scrolls to show latest messages
- **Read-only**: Can't accidentally edit the log

## Button Functions

### Browse Buttons
- **What they do**: Open file/folder selection dialogs
- **Keyboard shortcut**: None (use mouse)

### Start Processing
- **When enabled**: Only when both input and output are selected
- **What it does**: Begins the photo processing workflow
- **During processing**: Disabled to prevent multiple runs
- **Text changes**: Shows "Processing..." while running

### Help
- **What it shows**: Quick help guide
- **Information includes**:
  - How to use the app
  - What the app does
  - Tips for best results

### About
- **What it shows**: Application information
- **Information includes**:
  - Version number
  - Features list
  - Credits

### Exit
- **What it does**: Closes the application
- **Warning**: Does not warn if processing is in progress

## Understanding the Log

The processing log shows detailed information. Here's what to look for:

### Normal Messages
```
Selected input folder: /home/user/photos
Output will be saved to: /home/user/output.pdf
Found 25 images to process
Processing 1/25: IMG_001.jpg
  Found 2 face(s) in IMG_001.jpg
Processing 2/25: IMG_002.jpg
...
Successfully processed 25 images
Creating PDF: /home/user/output.pdf
  Added page 1/13 to PDF
  Added page 2/13 to PDF
  ...
  Added page 13/13 to PDF
Saving PDF file...
✓ Processing complete!
```

### Warning Messages
```
Processing 5/25: IMG_005.jpg
  Error processing IMG_005.jpg: Cannot identify image file
```
This means one photo couldn't be processed, but others will continue.

### Error Messages
```
✗ Error: No image files found in /home/user/empty_folder
```
This means the entire process stopped due to an error.

## Tips for Best Results

### Photo Quality
- **Resolution**: Use photos at least 1500×2100 pixels
- **Format**: JPEG works best; PNG also good
- **Compression**: Avoid heavily compressed images

### Face Detection
- **Works best with**:
  - Clear, front-facing portraits
  - Good lighting
  - Single or small groups
- **May struggle with**:
  - Side profiles
  - Blurry photos
  - Very small faces in large groups
  - People wearing sunglasses or hats

### Folder Organization
- **Before processing**:
  - Remove any non-photo files
  - Delete unwanted photos
  - Rename files in desired order (01_photo.jpg, 02_photo.jpg, etc.)
- **During processing**:
  - Don't add/remove files from the folder
  - Don't modify the photos

### Processing Time
- **Small batch** (1-10 photos): Under 30 seconds
- **Medium batch** (10-50 photos): 1-2 minutes
- **Large batch** (50-100 photos): 3-5 minutes
- **Very large** (100+ photos): Consider splitting into smaller batches

## Troubleshooting

### "Start Processing" Button is Disabled
- **Cause**: Missing input folder or output file
- **Solution**: Make sure both are selected

### "No image files found in this folder"
- **Cause**: Folder doesn't contain supported image formats
- **Solution**: 
  - Check folder path is correct
  - Ensure files are .jpg, .png, .bmp, or .tiff
  - Look in subfolders (app only checks main folder)

### Application Won't Start
- **Cause**: Missing dependencies
- **Solution**: Run `pip install -r requirements.txt`

### "Could not import PhotoProcessor"
- **Cause**: `photo_to_pdf.py` is missing
- **Solution**: 
  - Make sure `photo_to_pdf.py` is in the same directory
  - Don't separate the GUI from the main script

### Processing Freezes or Hangs
- **Cause**: Very large photos or many photos
- **Solution**: 
  - Wait longer (processing can take time)
  - Process fewer photos at once
  - Check the log for error messages

### PDF Quality is Poor
- **Cause**: Source photos are low resolution
- **Solution**: 
  - Use higher resolution source images
  - Ensure photos are at least 1500×2100 pixels
  - The script outputs at 300 DPI, quality depends on input

### Faces are Cut Off
- **Cause**: Face detection centered on average position
- **Solution**: 
  - For group photos, some faces may be cropped
  - Consider processing individuals separately
  - Crop photos manually before processing

## Keyboard Shortcuts

The GUI currently doesn't have custom keyboard shortcuts, but standard system shortcuts work:

- **Tab**: Move between fields
- **Enter**: Activate focused button
- **Alt+F4** (Windows) / **Cmd+Q** (Mac): Quit application

## Advanced Usage

### Processing Multiple Folders
1. Process first folder
2. When complete, select new input folder
3. Choose new output filename (or different location)
4. Process again

### Batch Processing
For many folders, consider using the command-line version with a script:
```bash
for folder in photo_folder_*; do
    python photo_to_pdf.py "$folder" "output_${folder}.pdf"
done
```

### Automation
The GUI isn't designed for automation. For automated workflows, use the command-line version (`photo_to_pdf.py`) instead.

## Getting Help

If you encounter issues:

1. **Check the log**: Error messages appear in the processing log
2. **Read the error dialog**: Click "OK" on errors to see details
3. **Try the command-line version**: Sometimes provides more detailed errors
4. **Check the main README**: Has comprehensive troubleshooting section
5. **Verify dependencies**: Run `pip list | grep -E "(Pillow|opencv|reportlab)"`

## Feature Comparison

| Feature | GUI | Command-Line |
|---------|-----|--------------|
| Ease of use | ✓✓✓ Very Easy | ✓ Moderate |
| Progress tracking | ✓ Visual | ✓ Text only |
| Error handling | ✓ Dialogs | ✓ Console messages |
| Batch processing | ✗ One at a time | ✓ Scriptable |
| Automation | ✗ Manual only | ✓ Full automation |
| Memory usage | Higher | Lower |
| Customization | Limited | Full access |

## System Requirements

### Minimum
- Python 3.7+
- 2 GB RAM
- 100 MB disk space
- Display resolution: 800×600

### Recommended
- Python 3.9+
- 4 GB RAM
- 500 MB disk space (for processing)
- Display resolution: 1024×768 or higher

### Operating Systems
- ✓ Windows 10/11
- ✓ macOS 10.14+
- ✓ Linux (Ubuntu, Fedora, etc.)

## FAQ

**Q: Can I process photos from multiple folders at once?**
A: No, select one folder at a time. Process each separately.

**Q: Can I cancel processing once it starts?**
A: Not currently. Close the application to stop (PDF may be incomplete).

**Q: Where is my PDF saved?**
A: In the exact location you specified in step 2.

**Q: Can I change the photo size from 5x7?**
A: Not in the GUI. Edit the source code or use the command-line version.

**Q: Does it work offline?**
A: Yes! No internet connection required.

**Q: Can I use this commercially?**
A: Yes, all dependencies use permissive licenses. See main README.

**Q: How do I report a bug?**
A: Check the processing log for error details and consult the troubleshooting section.

## Credits

Built with:
- **Python**: Programming language
- **tkinter**: GUI framework (built into Python)
- **OpenCV**: Face detection
- **Pillow**: Image processing
- **ReportLab**: PDF generation

---

**Enjoy using the Photo to PDF Processor!**

For more detailed information, see the main README.md file.
