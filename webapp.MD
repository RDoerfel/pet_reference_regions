PET Reference Regions WebAssembly Neuroimaging Application

Purpose: Create reference regions from brain segmentation masks for PET (Positron Emission Tomography) analysis using a fully client-side WebAssembly application
that ensures complete data privacy.

Core Functionality:
- Drag-and-drop NIfTI upload: Load brain segmentation files (.nii/.nii.gz) directly in browser
- Dual mask support: Primary segmentation + optional probability mask
- Region selection: Choose anatomical indices to include/exclude from regions
- Morphological processing: Apply erosion/dilation to refine regions
- Probability thresholding: Filter regions based on probability values (0.0-1.0)
- Binary mask generation: Create final reference regions for PET quantification

Processing Pipeline:
1. Input: Segmentation mask (labeled regions 1-N) + optional probability mask (0.0-1.0 values)
2. Selection: Reference indices (e.g., 4,7,15) and exclusion indices (e.g., 2,8)
3. Probability filtering: Apply threshold to probability mask (e.g., >0.5)
4. Morphology: Erosion on reference regions, dilation on exclusion regions
5. Output: Binary reference mask preserving original NIfTI geometry

Interactive 3D Visualization:
- Orthogonal slice views: Real-time Axial (Z), Coronal (Y), Sagittal (X) navigation
- Canvas-based rendering: Hardware-accelerated slice display
- Color-coded overlays:
- Green: Final processed reference regions
- Red: Excluded regions
- Orange: Probability-removed regions (below threshold)
- Interactive controls: Slice sliders, overlay toggles, opacity adjustment
- Synchronized navigation: Linked slice positions across views

WebAssembly Architecture:
- Pyodide runtime: Execute Python (nibabel, numpy, scipy) in browser
- Zero server dependency: All processing on user's device
- Complete privacy: Medical data never transmitted
- Near-native performance: WASM-compiled scientific computing
- Offline capability: Works without internet after initial load

Deployment & Distribution:
- GitHub Pages hosting: Static files, zero infrastructure cost
- Progressive loading: Pyodide + packages downloaded on demand

Technical Stack:
- Frontend: HTML5, Canvas API, modern JavaScript ES6+
- Compute: Pyodide WebAssembly Python runtime
- Python: nibabel (NIfTI I/O), numpy (arrays), local package refregion (morphology, region ops)
- Visualization: Custom Canvas rendering for medical imaging
