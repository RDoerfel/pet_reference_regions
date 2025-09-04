# PET Reference Regions WebApp 🧠

**A fully client-side WebAssembly neuroimaging application for creating PET reference regions from brain segmentations**

[![Deploy WebApp](https://github.com/RDoerfel/pet_reference_regions/actions/workflows/deploy-webapp.yml/badge.svg)](https://github.com/RDoerfel/pet_reference_regions/actions/workflows/deploy-webapp.yml)

## 🎯 Purpose

Create reference regions from brain segmentation masks for PET (Positron Emission Tomography) analysis using a privacy-first, fully client-side WebAssembly application. All processing happens in your browser - **your medical data never leaves your device**.

## ✨ Features

### 🔒 **Complete Privacy**
- **Zero server dependency**: All processing on your device
- **No data transmission**: Medical data stays completely private  
- **Offline capability**: Works without internet after initial load

### 📁 **File Processing**
- **Drag-and-drop upload**: Load brain segmentation files (`.nii`/`.nii.gz`)
- **Dual mask support**: Primary segmentation + optional probability mask
- **NIfTI format**: Full support for neuroimaging standard format

### 🎛️ **Interactive Controls**
- **Region selection**: Choose anatomical indices to include/exclude
- **Morphological operations**: Apply erosion/dilation to refine regions  
- **Probability thresholding**: Filter regions based on probability values (0.0-1.0)
- **Real-time parameters**: Adjust settings with immediate feedback

### 📊 **3D Visualization**
- **Orthogonal views**: Real-time Axial (Z), Coronal (Y), Sagittal (X) navigation
- **Color-coded overlays**:
  - 🟢 **Green**: Final processed reference regions
  - 🔴 **Red**: Excluded regions  
  - 🟠 **Orange**: Probability-removed regions
- **Interactive controls**: Slice sliders, overlay toggles, opacity adjustment
- **Synchronized navigation**: Linked slice positions across views

### ⚡ **High Performance**
- **WebAssembly runtime**: Near-native speed for medical image processing
- **Pyodide integration**: Full Python scientific stack (NumPy, SciPy, nibabel)
- **Progressive loading**: Optimized package downloading

## 🚀 Quick Start

### Online Usage
1. **Visit the webapp**: [https://rdoerfel.github.io/pet_reference_regions/](https://rdoerfel.github.io/pet_reference_regions/)
2. **Upload files**: Drag & drop your brain segmentation file (`.nii` or `.nii.gz`)
3. **Set parameters**: Choose reference indices (e.g., `7,8` for cerebellar regions)
4. **Process**: Click "Process Reference Regions"
5. **Visualize**: Explore results in interactive 3D viewer
6. **Download**: Save processed reference mask

### Local Development
```bash
# Clone repository
git clone https://github.com/RDoerfel/pet_reference_regions.git
cd pet_reference_regions/webapp

# Install dependencies
npm install

# Run local server
npm run serve
# or
python -m http.server 8000

# Open browser
open http://localhost:8000
```

## 📋 Processing Pipeline

1. **Input**: Segmentation mask (labeled regions 1-N) + optional probability mask (0.0-1.0 values)
2. **Selection**: Reference indices (e.g., `4,7,15`) and exclusion indices (e.g., `2,8`)  
3. **Probability filtering**: Apply threshold to probability mask (e.g., >0.5)
4. **Morphology**: Erosion on reference regions, dilation on exclusion regions
5. **Output**: Binary reference mask preserving original NIfTI geometry

### Example Parameters
```
Reference Indices: 7,8        # Cerebellar gray matter regions
Exclusion Indices: 16         # Brain stem (optional)
Probability Threshold: 0.5    # 50% confidence threshold
Erosion Size: 1 voxel         # Refine reference regions
Exclusion Dilation: 2 voxels  # Expand exclusion zones
```

## 🏗️ Technical Architecture

### Frontend Stack
- **HTML5**: Modern responsive interface
- **Canvas API**: Hardware-accelerated medical image rendering
- **ES6+ JavaScript**: Modular, efficient code architecture
- **CSS Grid/Flexbox**: Responsive design for all devices

### WebAssembly Integration  
- **Pyodide Runtime**: Execute Python in browser with full scientific stack
- **Memory Management**: Efficient handling of large medical datasets
- **Scientific Computing**: numpy, scipy, nibabel, scikit-image
- **Custom Bridge**: Seamless JavaScript ↔ Python communication

### Medical Imaging
- **NIfTI I/O**: Complete support via nibabel
- **Morphological Operations**: scikit-image for region refinement
- **Geometry Preservation**: Maintains original coordinate systems
- **Multi-dimensional**: Handles 3D/4D medical imaging data

## 🧪 Development

### Testing
```bash
npm test              # Run full test suite
npm run test:watch    # Watch mode for development
npm run lint          # Code quality checks
npm run validate      # WebApp integrity validation
```

### Build & Deploy
```bash
npm run build         # Prepare for deployment (if needed)
node scripts/validate-webapp.js  # Validate before deploy
```

### Project Structure
```
webapp/
├── index.html              # Main application
├── css/styles.css          # Responsive styling
├── js/
│   ├── app.js             # Application controller
│   ├── pyodide-bridge.js  # Python integration
│   └── visualization.js   # 3D canvas viewer
├── tests/                 # Comprehensive test suite
├── scripts/               # Validation and utilities
└── package.json           # Dependencies and config
```

## 📊 Performance

- **Initialization**: ~10-30s (one-time Pyodide + packages download)
- **File Loading**: ~1-5s for typical brain scans (50-200MB)
- **Processing**: ~2-10s depending on image size and operations
- **Memory Usage**: ~500MB-2GB RAM (depends on image dimensions)
- **Browser Requirements**: Modern browsers with WebAssembly support

## 🔧 Browser Compatibility

### Supported Browsers
- **Chrome**: 57+ (recommended for best performance)
- **Firefox**: 52+
- **Safari**: 11+
- **Edge**: 79+

### Requirements
- **WebAssembly**: Required for Python runtime
- **Canvas API**: For medical image visualization  
- **File API**: For drag-and-drop functionality
- **Memory**: 2GB+ RAM recommended for large datasets

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Test** your changes (`npm test`)
4. **Validate** webapp (`npm run validate`)
5. **Commit** changes (`git commit -m 'Add amazing feature'`)
6. **Push** to branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### Development Guidelines
- Follow existing code style and patterns
- Add tests for new functionality  
- Validate webapp before submitting PRs
- Document any new features or APIs

## 📄 License

**MIT License** - see [LICENSE](../LICENSE) file for details.

## 🙋 Support

- **Issues**: [GitHub Issues](https://github.com/RDoerfel/pet_reference_regions/issues)
- **Discussions**: [GitHub Discussions](https://github.com/RDoerfel/pet_reference_regions/discussions)
- **Documentation**: [Main Project README](../README.md)

## 🔬 Scientific Background

This webapp implements the same scientifically validated algorithms as the Python package, providing:

- **Cerebellar reference regions**: Standard approaches for PET quantification
- **Morphological refinement**: Erosion/dilation to avoid partial volume effects
- **Probability-based filtering**: Quality control for automated segmentations
- **Custom region creation**: Flexible region selection for research applications

Perfect for researchers, clinicians, and students working with PET neuroimaging data who need a fast, private, and accessible solution for reference region creation.

---

**🧠 Built for the neuroimaging community with privacy and performance in mind.**