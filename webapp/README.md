# PET Reference Region Morphology Editor

A browser-based web application for editing PET reference region masks with morphological operations. All processing happens locally in your browser - no data is uploaded to any server.

## Features

- Load and visualize T1w images, segmentation masks, and probability masks (NIfTI format)
- Interactive 3-plane visualization (Axial, Coronal, Sagittal)
- Select specific mask regions for processing
- Apply erosion and dilation operations with configurable radius
- Apply probability thresholding to masks
- Real-time mask overlay visualization
- Download processed masks as NIfTI files

## Files

- `index.html` - Main HTML interface
- `app.py` - Python application logic
- `refregion-0.1.0-py3-none-any.whl` - The refregion package wheel

## Usage

### Running Locally

1. Make sure all three files are in the same directory
2. Serve the directory using a local web server:

```bash
# Using Python's built-in server
python -m http.server 8000

# Or using Node.js http-server
npx http-server .
```

3. Open your browser and navigate to `http://localhost:8000`
4. Wait for Python packages to load (this may take a minute on first load)

### Using the Application

1. **Load Images**
   - Click "Choose File" for T1w Image and select your structural image (.nii or .nii.gz)
   - Click "Choose File" for Segmentation Mask and select your mask file
   - (Optional) Load a probability mask if available

2. **Select Mask Indices**
   - After loading a mask, checkboxes will appear for each region index
   - Select which regions you want to process
   - By default, all regions are selected

3. **Configure Morphology Operations**
   - Set the erosion radius (0-10 voxels)
   - Set the dilation radius (0-10 voxels)
   - Set the probability threshold (0.0-1.0) if using a probability mask

4. **Apply Operations**
   - Click "Apply Operations" to process the selected regions
   - The visualization will update to show the processed mask
   - Click "Reset to Original" to revert changes

5. **Visualize**
   - Use the sliders under each view to navigate through different slices
   - Masks are overlaid in red on the T1 image
   - The processed or original mask is shown depending on your current state

6. **Save**
   - Click "Download Processed Mask" to save the result as a NIfTI file
   - The file will be downloaded as `processed_mask.nii.gz`

## Technical Details

### Technologies Used

- **PyScript**: Runs Python code in the browser using WebAssembly
- **Pyodide**: Python runtime for the browser
- **nibabel**: NIfTI file I/O
- **numpy**: Numerical operations
- **scikit-image**: Morphological operations
- **refregion**: Custom morphology functions

### Privacy

All processing happens locally in your browser. No data is transmitted to any server. Your medical imaging data stays on your computer.

### Browser Compatibility

Works best in modern browsers:
- Chrome/Edge 90+
- Firefox 90+
- Safari 15+

### Performance

- First load may take 30-60 seconds to download Python packages
- Subsequent loads are faster due to browser caching
- Large images (>512³) may take several seconds to process
- Processing time depends on:
  - Image size
  - Number of selected regions
  - Erosion/dilation radius

## Deployment

To deploy this application:

1. Ensure all three files are in the same directory:
   - `index.html`
   - `app.py`
   - `refregion-0.1.0-py3-none-any.whl`

2. Upload to any static hosting service:
   - GitHub Pages
   - Netlify
   - Vercel
   - AWS S3 + CloudFront
   - Any web server

3. Access via the hosted URL

## Updating the Package

When you update the refregion package:

1. Rebuild the package:
   ```bash
   cd /path/to/pet_reference_regions
   poetry build
   ```

2. Copy the new wheel file to the webapp directory:
   ```bash
   cp dist/refregion-*.whl webapp/
   ```

3. Update the wheel filename in `app.py` if the version changed

## Troubleshooting

**Application won't load**
- Check browser console for errors
- Ensure you're serving over HTTP (not opening file:// directly)
- Try clearing browser cache

**File won't load**
- Ensure file is valid NIfTI format (.nii or .nii.gz)
- Check browser console for specific error messages

**Operations are slow**
- Reduce the erosion/dilation radius
- Process fewer regions at once
- Use smaller images if possible

**Visualization looks wrong**
- Try adjusting the sliders to different positions
- Ensure the T1 and mask have matching dimensions

## License

MIT License - see the main project for details
