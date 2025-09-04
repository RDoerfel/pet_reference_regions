/**
 * PyodideBridge - JavaScript ↔ Python WebAssembly Communication Bridge
 * Handles Pyodide initialization, Python package loading, and data transfer
 */
class PyodideBridge {
    constructor() {
        this.pyodide = null;
        this.initialized = false;
        this.packages = ['numpy', 'scipy', 'nibabel', 'scikit-image'];
        this.initPromise = null;
    }

    /**
     * Initialize Pyodide runtime and load required packages
     */
    async init(onProgress = null) {
        if (this.initPromise) {
            return this.initPromise;
        }

        this.initPromise = this._doInit(onProgress);
        return this.initPromise;
    }

    async _doInit(onProgress) {
        try {
            // Update status
            if (onProgress) onProgress('Loading Pyodide runtime...', 10);

            // Load Pyodide
            this.pyodide = await loadPyodide();
            
            if (onProgress) onProgress('Installing Python packages...', 30);

            // Install required packages
            await this.pyodide.loadPackage(['numpy', 'scipy']);
            
            if (onProgress) onProgress('Installing nibabel...', 50);
            await this.pyodide.loadPackage(['nibabel']);
            
            if (onProgress) onProgress('Installing scikit-image...', 70);
            await this.pyodide.loadPackage(['scikit-image']);

            if (onProgress) onProgress('Loading refregion package...', 85);

            // Install local refregion package
            await this._installLocalPackage();

            if (onProgress) onProgress('Initialization complete!', 100);

            this.initialized = true;
            return true;

        } catch (error) {
            console.error('Pyodide initialization failed:', error);
            throw new Error(`Failed to initialize Python runtime: ${error.message}`);
        }
    }

    /**
     * Install the local refregion package in Pyodide environment
     */
    async _installLocalPackage() {
        // Create Python code to define refregion functions directly
        const refregionCode = `
import numpy as np
from scipy import ndimage
import nibabel as nib
from skimage import morphology
import io

class RefRegion:
    """WebAssembly-optimized reference region processing"""
    
    @staticmethod
    def load_nifti_from_buffer(buffer_data):
        """Load NIfTI from JavaScript ArrayBuffer"""
        try:
            # Convert buffer to file-like object
            file_obj = io.BytesIO(bytes(buffer_data))
            img = nib.load(file_obj)
            return img
        except Exception as e:
            raise ValueError(f"Failed to load NIfTI file: {str(e)}")
    
    @staticmethod
    def create_reference_region(segmentation_data, reference_indices, 
                              exclusion_indices=None, probability_data=None,
                              prob_threshold=0.5, erosion_size=1, exclusion_dilation=2):
        """
        Create reference region with morphological operations
        
        Parameters:
        -----------
        segmentation_data : ndarray
            Segmentation mask with labeled regions
        reference_indices : list
            Indices of regions to include in reference
        exclusion_indices : list, optional
            Indices of regions to exclude
        probability_data : ndarray, optional
            Probability mask for thresholding
        prob_threshold : float
            Probability threshold (0.0-1.0)
        erosion_size : int
            Erosion kernel size for reference regions
        exclusion_dilation : int
            Dilation kernel size for exclusion regions
        
        Returns:
        --------
        dict with 'reference_mask', 'exclusion_mask', 'probability_mask', 'stats'
        """
        
        # Create reference mask from selected indices
        reference_mask = np.zeros_like(segmentation_data, dtype=bool)
        for idx in reference_indices:
            reference_mask |= (segmentation_data == idx)
        
        # Create exclusion mask if specified
        exclusion_mask = np.zeros_like(segmentation_data, dtype=bool)
        if exclusion_indices:
            for idx in exclusion_indices:
                exclusion_mask |= (segmentation_data == idx)
        
        # Apply probability thresholding if probability data provided
        probability_mask = np.ones_like(segmentation_data, dtype=bool)
        if probability_data is not None:
            probability_mask = probability_data >= prob_threshold
            reference_mask &= probability_mask
        
        # Apply morphological operations
        if erosion_size > 0:
            kernel = morphology.ball(erosion_size)
            reference_mask = morphology.binary_erosion(reference_mask, kernel)
        
        if exclusion_dilation > 0 and np.any(exclusion_mask):
            kernel = morphology.ball(exclusion_dilation)
            exclusion_mask = morphology.binary_dilation(exclusion_mask, kernel)
        
        # Remove exclusion regions from reference
        reference_mask = reference_mask & ~exclusion_mask
        
        # Calculate statistics
        stats = {
            'reference_voxels': int(np.sum(reference_mask)),
            'exclusion_voxels': int(np.sum(exclusion_mask)),
            'probability_removed': int(np.sum(~probability_mask)) if probability_data is not None else 0,
            'total_brain_voxels': int(np.sum(segmentation_data > 0))
        }
        
        return {
            'reference_mask': reference_mask,
            'exclusion_mask': exclusion_mask,
            'probability_mask': probability_mask,
            'stats': stats
        }
    
    @staticmethod
    def save_nifti_to_buffer(data, affine, header=None):
        """Save NIfTI data to buffer for download"""
        try:
            # Create NIfTI image
            if header is not None:
                img = nib.Nifti1Image(data, affine, header)
            else:
                img = nib.Nifti1Image(data, affine)
            
            # Save to buffer
            buffer = io.BytesIO()
            nib.save(img, buffer)
            buffer.seek(0)
            
            return buffer.getvalue()
        except Exception as e:
            raise ValueError(f"Failed to save NIfTI: {str(e)}")

# Make RefRegion available globally
globals()['RefRegion'] = RefRegion
`;

        // Execute the Python code in Pyodide
        this.pyodide.runPython(refregionCode);
    }

    /**
     * Load NIfTI file from JavaScript File object
     */
    async loadNifti(file) {
        if (!this.initialized) {
            throw new Error('Pyodide not initialized');
        }

        try {
            // Convert File to ArrayBuffer
            const arrayBuffer = await file.arrayBuffer();
            const uint8Array = new Uint8Array(arrayBuffer);

            // Transfer to Python and load
            this.pyodide.globals.set('nifti_buffer', uint8Array);
            
            const result = this.pyodide.runPython(`
                try:
                    img = RefRegion.load_nifti_from_buffer(nifti_buffer)
                    {
                        'data': img.get_fdata(),
                        'affine': img.affine,
                        'header': img.header,
                        'shape': img.shape,
                        'success': True
                    }
                except Exception as e:
                    {'success': False, 'error': str(e)}
            `);

            if (!result.success) {
                throw new Error(result.error);
            }

            return {
                data: result.data,
                affine: result.affine,
                header: result.header,
                shape: result.shape
            };

        } catch (error) {
            console.error('NIfTI loading error:', error);
            throw new Error(`Failed to load NIfTI file: ${error.message}`);
        }
    }

    /**
     * Process reference regions with given parameters
     */
    async processReferenceRegions(segmentationData, parameters) {
        if (!this.initialized) {
            throw new Error('Pyodide not initialized');
        }

        try {
            // Transfer data to Python
            this.pyodide.globals.set('seg_data', segmentationData.data);
            this.pyodide.globals.set('prob_data', parameters.probabilityData?.data || null);
            this.pyodide.globals.set('ref_indices', parameters.referenceIndices);
            this.pyodide.globals.set('excl_indices', parameters.exclusionIndices || []);
            this.pyodide.globals.set('prob_threshold', parameters.probThreshold || 0.5);
            this.pyodide.globals.set('erosion_size', parameters.erosionSize || 1);
            this.pyodide.globals.set('exclusion_dilation', parameters.exclusionDilation || 2);

            // Process in Python
            const result = this.pyodide.runPython(`
                try:
                    result = RefRegion.create_reference_region(
                        seg_data, ref_indices, excl_indices, prob_data,
                        prob_threshold, erosion_size, exclusion_dilation
                    )
                    result['success'] = True
                    result
                except Exception as e:
                    {'success': False, 'error': str(e)}
            `);

            if (!result.success) {
                throw new Error(result.error);
            }

            return {
                referenceMask: result.reference_mask,
                exclusionMask: result.exclusion_mask,
                probabilityMask: result.probability_mask,
                stats: result.stats
            };

        } catch (error) {
            console.error('Processing error:', error);
            throw new Error(`Failed to process reference regions: ${error.message}`);
        }
    }

    /**
     * Save processed mask as NIfTI for download
     */
    async saveNifti(maskData, affine, header) {
        if (!this.initialized) {
            throw new Error('Pyodide not initialized');
        }

        try {
            // Transfer data to Python
            this.pyodide.globals.set('mask_data', maskData);
            this.pyodide.globals.set('affine', affine);
            this.pyodide.globals.set('header', header);

            // Save to buffer in Python
            const result = this.pyodide.runPython(`
                try:
                    buffer_data = RefRegion.save_nifti_to_buffer(mask_data, affine, header)
                    {'success': True, 'data': buffer_data}
                except Exception as e:
                    {'success': False, 'error': str(e)}
            `);

            if (!result.success) {
                throw new Error(result.error);
            }

            return new Uint8Array(result.data);

        } catch (error) {
            console.error('Save error:', error);
            throw new Error(`Failed to save NIfTI: ${error.message}`);
        }
    }

    /**
     * Check if Pyodide is initialized
     */
    isInitialized() {
        return this.initialized;
    }

    /**
     * Get Pyodide instance (for advanced usage)
     */
    getPyodide() {
        return this.pyodide;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PyodideBridge;
} else {
    window.PyodideBridge = PyodideBridge;
}