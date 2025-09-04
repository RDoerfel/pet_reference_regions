/**
 * Main Application Controller
 * Coordinates file handling, processing pipeline, and UI interactions
 */
class PETRefRegionApp {
    constructor(PyodideBridgeClass = null, NiftiVisualizationClass = null) {
        // Handle dependency injection for testing
        const PyodideBridgeConstructor = PyodideBridgeClass || 
            (typeof PyodideBridge !== 'undefined' ? PyodideBridge : 
             (typeof window !== 'undefined' && window.PyodideBridge ? window.PyodideBridge : 
              (typeof require !== 'undefined' ? require('./pyodide-bridge.js') : null)));
        
        const NiftiVisualizationConstructor = NiftiVisualizationClass || 
            (typeof NiftiVisualization !== 'undefined' ? NiftiVisualization : 
             (typeof window !== 'undefined' && window.NiftiVisualization ? window.NiftiVisualization : 
              (typeof require !== 'undefined' ? require('./visualization.js') : null)));
        
        if (!PyodideBridgeConstructor) {
            throw new Error('PyodideBridge class not available');
        }
        if (!NiftiVisualizationConstructor) {
            throw new Error('NiftiVisualization class not available');
        }
        
        this.pyodideBridge = new PyodideBridgeConstructor();
        this.visualization = new NiftiVisualizationConstructor();
        
        // Application state
        this.segmentationFile = null;
        this.probabilityFile = null;
        this.segmentationData = null;
        this.probabilityData = null;
        this.processedResults = null;
        
        // UI elements
        this.elements = {};
        this.initializeElements();
        this.setupEventListeners();
        
        // Initialize application
        this.initializeApp();
    }

    /**
     * Initialize UI elements
     */
    initializeElements() {
        // File upload elements
        this.elements.segUploadArea = document.getElementById('segmentation-upload');
        this.elements.segInput = document.getElementById('segmentation-input');
        this.elements.segFileInfo = document.getElementById('seg-file-info');
        
        this.elements.probUploadArea = document.getElementById('probability-upload');
        this.elements.probInput = document.getElementById('probability-input');
        this.elements.probFileInfo = document.getElementById('prob-file-info');
        
        // Parameter controls
        this.elements.refIndices = document.getElementById('reference-indices');
        this.elements.exclIndices = document.getElementById('exclusion-indices');
        this.elements.probThreshold = document.getElementById('prob-threshold');
        this.elements.probThresholdValue = document.getElementById('prob-threshold-value');
        this.elements.erosionSize = document.getElementById('erosion-size');
        this.elements.exclDilation = document.getElementById('exclusion-dilation');
        
        // Control buttons
        this.elements.processBtn = document.getElementById('process-btn');
        this.elements.downloadBtn = document.getElementById('download-btn');
        
        // Sections
        this.elements.parametersSection = document.getElementById('parameters-section');
        this.elements.visualizationSection = document.getElementById('visualization-section');
        this.elements.resultsSection = document.getElementById('results-section');
        
        // Status overlay
        this.elements.statusOverlay = document.getElementById('status-overlay');
        this.elements.statusMessage = document.getElementById('status-message');
        this.elements.progressFill = document.getElementById('progress-fill');
        this.elements.processingSummary = document.getElementById('processing-summary');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // File upload events
        this.setupFileUpload(this.elements.segUploadArea, this.elements.segInput, 
                           this.handleSegmentationFile.bind(this));
        this.setupFileUpload(this.elements.probUploadArea, this.elements.probInput, 
                           this.handleProbabilityFile.bind(this));
        
        // Parameter updates
        this.elements.probThreshold.addEventListener('input', (e) => {
            this.elements.probThresholdValue.textContent = e.target.value;
        });
        
        // Process button
        this.elements.processBtn.addEventListener('click', () => {
            this.processReferenceRegions();
        });
        
        // Download button
        this.elements.downloadBtn.addEventListener('click', () => {
            this.downloadResults();
        });
    }

    /**
     * Setup drag-and-drop file upload for an area
     */
    setupFileUpload(uploadArea, fileInput, handler) {
        // Click to browse
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handler(e.target.files[0]);
            }
        });
        
        // Drag and drop events
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            if (e.dataTransfer.files.length > 0) {
                const file = e.dataTransfer.files[0];
                if (this.isNiftiFile(file)) {
                    handler(file);
                } else {
                    this.showError('Please drop a valid NIfTI file (.nii or .nii.gz)');
                }
            }
        });
    }

    /**
     * Check if file is a valid NIfTI file with size validation
     */
    isNiftiFile(file) {
        const name = file.name.toLowerCase();
        const isValidExtension = name.endsWith('.nii') || name.endsWith('.nii.gz');
        
        // Security: Limit file size to 500MB to prevent memory exhaustion
        const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500MB
        if (file.size > MAX_FILE_SIZE) {
            this.showError(`File too large (${this.formatFileSize(file.size)}). Maximum size is ${this.formatFileSize(MAX_FILE_SIZE)}.`);
            return false;
        }
        
        // Basic file type validation
        if (!isValidExtension) {
            this.showError('Invalid file type. Please upload a NIfTI file (.nii or .nii.gz).');
            return false;
        }
        
        return true;
    }

    /**
     * Handle segmentation file upload
     */
    async handleSegmentationFile(file) {
        try {
            this.showStatus('Loading segmentation file...', 0);
            
            this.segmentationFile = file;
            this.elements.segFileInfo.textContent = `${file.name} (${this.formatFileSize(file.size)})`;
            
            // Load file data
            this.segmentationData = await this.pyodideBridge.loadNifti(file);
            
            // Show parameters section
            this.elements.parametersSection.style.display = 'block';
            
            // Load visualization
            this.visualization.loadSegmentation(this.segmentationData.data, this.segmentationData.shape);
            this.elements.visualizationSection.style.display = 'block';
            
            this.hideStatus();
            
        } catch (error) {
            this.showError(`Failed to load segmentation file: ${error.message}`);
        }
    }

    /**
     * Handle probability file upload
     */
    async handleProbabilityFile(file) {
        try {
            this.showStatus('Loading probability file...', 0);
            
            this.probabilityFile = file;
            this.elements.probFileInfo.textContent = `${file.name} (${this.formatFileSize(file.size)})`;
            
            // Load file data
            this.probabilityData = await this.pyodideBridge.loadNifti(file);
            
            this.hideStatus();
            
        } catch (error) {
            this.showError(`Failed to load probability file: ${error.message}`);
        }
    }

    /**
     * Process reference regions with current parameters
     */
    async processReferenceRegions() {
        if (!this.segmentationData) {
            this.showError('Please load a segmentation file first');
            return;
        }

        try {
            this.showStatus('Processing reference regions...', 0);
            this.elements.processBtn.disabled = true;

            // Parse parameters
            const parameters = this.getProcessingParameters();
            
            // Validate parameters
            if (parameters.referenceIndices.length === 0) {
                throw new Error('Please specify at least one reference index');
            }

            this.showStatus('Applying morphological operations...', 50);
            
            // Process in Python
            this.processedResults = await this.pyodideBridge.processReferenceRegions(
                this.segmentationData, parameters
            );

            this.showStatus('Updating visualization...', 80);
            
            // Update visualization with results
            this.visualization.loadMasks(
                this.processedResults.referenceMask,
                this.processedResults.exclusionMask,
                this.processedResults.probabilityMask
            );

            // Show results
            this.showProcessingResults(this.processedResults.stats);
            this.elements.resultsSection.style.display = 'block';

            this.hideStatus();
            
        } catch (error) {
            this.showError(`Processing failed: ${error.message}`);
        } finally {
            this.elements.processBtn.disabled = false;
        }
    }

    /**
     * Get processing parameters from UI
     */
    getProcessingParameters() {
        // Parse reference indices
        const refIndicesText = this.elements.refIndices.value.trim();
        const referenceIndices = refIndicesText 
            ? refIndicesText.split(',').map(idx => parseInt(idx.trim())).filter(idx => !isNaN(idx))
            : [];

        // Parse exclusion indices
        const exclIndicesText = this.elements.exclIndices.value.trim();
        const exclusionIndices = exclIndicesText 
            ? exclIndicesText.split(',').map(idx => parseInt(idx.trim())).filter(idx => !isNaN(idx))
            : [];

        return {
            referenceIndices,
            exclusionIndices,
            probabilityData: this.probabilityData,
            probThreshold: parseFloat(this.elements.probThreshold.value),
            erosionSize: parseInt(this.elements.erosionSize.value),
            exclusionDilation: parseInt(this.elements.exclDilation.value)
        };
    }

    /**
     * Show processing results summary
     */
    showProcessingResults(stats) {
        const summary = `
            <strong>Processing Complete!</strong><br>
            Reference region voxels: ${stats.reference_voxels.toLocaleString()}<br>
            Excluded voxels: ${stats.exclusion_voxels.toLocaleString()}<br>
            ${stats.probability_removed > 0 ? 
                `Probability-filtered voxels: ${stats.probability_removed.toLocaleString()}<br>` : ''}
            Total brain voxels: ${stats.total_brain_voxels.toLocaleString()}<br>
            Coverage: ${((stats.reference_voxels / stats.total_brain_voxels) * 100).toFixed(1)}%
        `;
        
        this.elements.processingSummary.innerHTML = summary;
    }

    /**
     * Download processed results as NIfTI
     */
    async downloadResults() {
        if (!this.processedResults) {
            this.showError('No processed results to download');
            return;
        }

        try {
            this.showStatus('Preparing download...', 0);

            // Save as NIfTI buffer
            const niftiBuffer = await this.pyodideBridge.saveNifti(
                this.processedResults.referenceMask,
                this.segmentationData.affine,
                this.segmentationData.header
            );

            // Create download
            const blob = new Blob([niftiBuffer], { type: 'application/octet-stream' });
            const url = URL.createObjectURL(blob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = this.generateFilename();
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            URL.revokeObjectURL(url);
            this.hideStatus();

        } catch (error) {
            this.showError(`Download failed: ${error.message}`);
        }
    }

    /**
     * Generate filename for download
     */
    generateFilename() {
        const baseName = this.segmentationFile.name.replace(/\.nii(\.gz)?$/, '');
        const params = this.getProcessingParameters();
        const refIndices = params.referenceIndices.join('-');
        
        return `${baseName}_refregion_${refIndices}.nii.gz`;
    }

    /**
     * Initialize application
     */
    async initializeApp() {
        try {
            this.showStatus('Initializing Python runtime...', 0);
            
            await this.pyodideBridge.init((message, progress) => {
                this.showStatus(message, progress);
            });
            
            this.hideStatus();
            
        } catch (error) {
            this.showError(`Initialization failed: ${error.message}`);
        }
    }

    /**
     * Show status overlay
     */
    showStatus(message, progress = 0) {
        this.elements.statusMessage.textContent = message;
        this.elements.progressFill.style.width = `${progress}%`;
        this.elements.statusOverlay.style.display = 'flex';
    }

    /**
     * Hide status overlay
     */
    hideStatus() {
        this.elements.statusOverlay.style.display = 'none';
    }

    /**
     * Show error message with better UX
     */
    showError(message) {
        console.error('WebApp Error:', message);
        
        // Create or update error modal
        let errorModal = document.getElementById('error-modal');
        if (!errorModal) {
            errorModal = this.createErrorModal();
        }
        
        // Update error content
        const errorMessage = errorModal.querySelector('.error-message');
        const errorDetails = errorModal.querySelector('.error-details');
        
        errorMessage.textContent = 'Application Error';
        errorDetails.textContent = message;
        
        // Show modal
        errorModal.style.display = 'flex';
        this.hideStatus();
        
        // Auto-hide after 10 seconds for non-critical errors
        if (!message.includes('Failed to') && !message.includes('Critical')) {
            setTimeout(() => {
                if (errorModal.style.display === 'flex') {
                    errorModal.style.display = 'none';
                }
            }, 10000);
        }
    }

    /**
     * Create error modal for better error display
     */
    createErrorModal() {
        const modal = document.createElement('div');
        modal.id = 'error-modal';
        modal.className = 'error-modal';
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8); display: none; align-items: center;
            justify-content: center; z-index: 10000;
        `;
        
        modal.innerHTML = `
            <div class="error-content" style="
                background: white; padding: 30px; border-radius: 12px;
                max-width: 500px; margin: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            ">
                <h3 class="error-message" style="color: #d32f2f; margin: 0 0 15px 0;">Error</h3>
                <p class="error-details" style="margin: 0 0 20px 0; line-height: 1.5;"></p>
                <div style="text-align: right;">
                    <button class="error-close-btn" style="
                        background: #1976d2; color: white; border: none; padding: 10px 20px;
                        border-radius: 6px; cursor: pointer; font-size: 16px;
                    ">OK</button>
                </div>
            </div>
        `;
        
        // Close button functionality
        const closeBtn = modal.querySelector('.error-close-btn');
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
        
        document.body.appendChild(modal);
        return modal;
    }

    /**
     * Format file size for display
     */
    formatFileSize(bytes) {
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(1)} ${units[unitIndex]}`;
    }
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PETRefRegionApp;
} else {
    window.PETRefRegionApp = PETRefRegionApp;
}

// Initialize application when DOM is loaded
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        window.petRefRegionApp = new PETRefRegionApp();
    });
}