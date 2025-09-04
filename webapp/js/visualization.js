/**
 * NiftiVisualization - Canvas-based 3D orthogonal slice viewer
 * Renders axial, coronal, and sagittal views with color-coded overlays
 */
class NiftiVisualization {
    constructor() {
        this.segmentationData = null;
        this.referenceMask = null;
        this.exclusionMask = null;
        this.probabilityMask = null;
        this.shape = null;
        this.currentSlices = { x: 0, y: 0, z: 0 };
        this.overlayOpacity = 0.7;
        this.showOverlays = {
            reference: true,
            exclusion: true,
            probability: true
        };
        
        this.canvases = {};
        this.contexts = {};
        this.sliders = {};
        this.sliceInfos = {};
        
        this.initializeElements();
        this.setupEventListeners();
    }

    /**
     * Initialize canvas elements and contexts
     */
    initializeElements() {
        // Get canvas elements
        const views = ['axial', 'coronal', 'sagittal'];
        
        views.forEach(view => {
            this.canvases[view] = document.getElementById(`${view}-canvas`);
            this.contexts[view] = this.canvases[view].getContext('2d');
            this.sliders[view] = document.getElementById(`${view}-slider`);
            this.sliceInfos[view] = document.getElementById(`${view}-slice-info`);
            
            // Set canvas size
            this.canvases[view].width = 256;
            this.canvases[view].height = 256;
        });
    }

    /**
     * Setup event listeners for controls
     */
    setupEventListeners() {
        // Slice sliders
        Object.keys(this.sliders).forEach(view => {
            this.sliders[view].addEventListener('input', (e) => {
                this.updateSlice(view, parseInt(e.target.value));
            });
        });

        // Overlay controls
        document.getElementById('overlay-opacity').addEventListener('input', (e) => {
            this.overlayOpacity = parseFloat(e.target.value);
            document.getElementById('opacity-value').textContent = this.overlayOpacity.toFixed(1);
            this.renderAll();
        });

        // Overlay toggles
        ['reference', 'exclusion', 'probability'].forEach(type => {
            document.getElementById(`show-${type}`).addEventListener('change', (e) => {
                this.showOverlays[type] = e.target.checked;
                this.renderAll();
            });
        });
    }

    /**
     * Load segmentation data and initialize visualization
     */
    loadSegmentation(data, shape) {
        this.segmentationData = data;
        this.shape = shape;
        
        // Initialize slice positions to middle
        this.currentSlices = {
            x: Math.floor(shape[0] / 2),
            y: Math.floor(shape[1] / 2),
            z: Math.floor(shape[2] / 2)
        };
        
        // Update slider ranges
        this.sliders.sagittal.max = shape[0] - 1;
        this.sliders.sagittal.value = this.currentSlices.x;
        
        this.sliders.coronal.max = shape[1] - 1;
        this.sliders.coronal.value = this.currentSlices.y;
        
        this.sliders.axial.max = shape[2] - 1;
        this.sliders.axial.value = this.currentSlices.z;
        
        this.updateSliceInfos();
        this.renderAll();
    }

    /**
     * Load processed masks for overlay visualization
     */
    loadMasks(referenceMask, exclusionMask, probabilityMask) {
        this.referenceMask = referenceMask;
        this.exclusionMask = exclusionMask;
        this.probabilityMask = probabilityMask;
        this.renderAll();
    }

    /**
     * Update slice position for a specific view
     */
    updateSlice(view, value) {
        switch(view) {
            case 'axial':
                this.currentSlices.z = value;
                break;
            case 'coronal':
                this.currentSlices.y = value;
                break;
            case 'sagittal':
                this.currentSlices.x = value;
                break;
        }
        
        this.updateSliceInfos();
        this.renderAll();
    }

    /**
     * Update slice information displays
     */
    updateSliceInfos() {
        if (!this.shape) return;
        
        this.sliceInfos.axial.textContent = 
            `Slice: ${this.currentSlices.z + 1}/${this.shape[2]}`;
        this.sliceInfos.coronal.textContent = 
            `Slice: ${this.currentSlices.y + 1}/${this.shape[1]}`;
        this.sliceInfos.sagittal.textContent = 
            `Slice: ${this.currentSlices.x + 1}/${this.shape[0]}`;
    }

    /**
     * Render all views
     */
    renderAll() {
        if (!this.segmentationData || !this.shape) return;
        
        this.renderView('axial');
        this.renderView('coronal');
        this.renderView('sagittal');
    }

    /**
     * Render a specific view (axial, coronal, or sagittal)
     */
    renderView(view) {
        const canvas = this.canvases[view];
        const ctx = this.contexts[view];
        const { x, y, z } = this.currentSlices;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Extract 2D slice based on view
        let slice, overlaySlices = {};
        
        switch(view) {
            case 'axial':
                slice = this.getAxialSlice(this.segmentationData, z);
                if (this.referenceMask) overlaySlices.reference = this.getAxialSlice(this.referenceMask, z);
                if (this.exclusionMask) overlaySlices.exclusion = this.getAxialSlice(this.exclusionMask, z);
                if (this.probabilityMask) overlaySlices.probability = this.getAxialSlice(this.probabilityMask, z);
                break;
            case 'coronal':
                slice = this.getCoronalSlice(this.segmentationData, y);
                if (this.referenceMask) overlaySlices.reference = this.getCoronalSlice(this.referenceMask, y);
                if (this.exclusionMask) overlaySlices.exclusion = this.getCoronalSlice(this.exclusionMask, y);
                if (this.probabilityMask) overlaySlices.probability = this.getCoronalSlice(this.probabilityMask, y);
                break;
            case 'sagittal':
                slice = this.getSagittalSlice(this.segmentationData, x);
                if (this.referenceMask) overlaySlices.reference = this.getSagittalSlice(this.referenceMask, x);
                if (this.exclusionMask) overlaySlices.exclusion = this.getSagittalSlice(this.exclusionMask, x);
                if (this.probabilityMask) overlaySlices.probability = this.getSagittalSlice(this.probabilityMask, x);
                break;
        }
        
        // Render base segmentation as grayscale
        this.renderGrayscaleSlice(ctx, slice, canvas.width, canvas.height);
        
        // Render overlays
        if (this.showOverlays.reference && overlaySlices.reference) {
            this.renderOverlay(ctx, overlaySlices.reference, canvas.width, canvas.height, 
                              [0, 255, 0], this.overlayOpacity); // Green
        }
        
        if (this.showOverlays.exclusion && overlaySlices.exclusion) {
            this.renderOverlay(ctx, overlaySlices.exclusion, canvas.width, canvas.height, 
                              [255, 0, 0], this.overlayOpacity); // Red
        }
        
        if (this.showOverlays.probability && overlaySlices.probability) {
            this.renderOverlay(ctx, overlaySlices.probability, canvas.width, canvas.height, 
                              [255, 165, 0], this.overlayOpacity * 0.5); // Orange, lower opacity
        }
    }

    /**
     * Extract axial slice (XY plane at given Z)
     */
    getAxialSlice(data, z) {
        if (!data || z < 0 || z >= this.shape[2]) return null;
        
        const slice = [];
        for (let y = 0; y < this.shape[1]; y++) {
            for (let x = 0; x < this.shape[0]; x++) {
                slice.push(data[x][y][z]);
            }
        }
        return { data: slice, width: this.shape[0], height: this.shape[1] };
    }

    /**
     * Extract coronal slice (XZ plane at given Y)
     */
    getCoronalSlice(data, y) {
        if (!data || y < 0 || y >= this.shape[1]) return null;
        
        const slice = [];
        for (let z = this.shape[2] - 1; z >= 0; z--) { // Flip Z for proper orientation
            for (let x = 0; x < this.shape[0]; x++) {
                slice.push(data[x][y][z]);
            }
        }
        return { data: slice, width: this.shape[0], height: this.shape[2] };
    }

    /**
     * Extract sagittal slice (YZ plane at given X)
     */
    getSagittalSlice(data, x) {
        if (!data || x < 0 || x >= this.shape[0]) return null;
        
        const slice = [];
        for (let z = this.shape[2] - 1; z >= 0; z--) { // Flip Z for proper orientation
            for (let y = 0; y < this.shape[1]; y++) {
                slice.push(data[x][y][z]);
            }
        }
        return { data: slice, width: this.shape[1], height: this.shape[2] };
    }

    /**
     * Render grayscale base slice
     */
    renderGrayscaleSlice(ctx, slice, canvasWidth, canvasHeight) {
        if (!slice) return;
        
        const imageData = ctx.createImageData(canvasWidth, canvasHeight);
        const data = imageData.data;
        
        // Scale slice to canvas size
        const scaleX = slice.width / canvasWidth;
        const scaleY = slice.height / canvasHeight;
        
        for (let canvasY = 0; canvasY < canvasHeight; canvasY++) {
            for (let canvasX = 0; canvasX < canvasWidth; canvasX++) {
                const sliceX = Math.floor(canvasX * scaleX);
                const sliceY = Math.floor(canvasY * scaleY);
                const sliceIndex = sliceY * slice.width + sliceX;
                
                let value = slice.data[sliceIndex] || 0;
                
                // Normalize to 0-255 range
                if (value > 0) {
                    value = Math.min(255, Math.max(50, value * 10)); // Enhance contrast
                }
                
                const pixelIndex = (canvasY * canvasWidth + canvasX) * 4;
                data[pixelIndex] = value;     // R
                data[pixelIndex + 1] = value; // G
                data[pixelIndex + 2] = value; // B
                data[pixelIndex + 3] = 255;   // A
            }
        }
        
        ctx.putImageData(imageData, 0, 0);
    }

    /**
     * Render colored overlay
     */
    renderOverlay(ctx, slice, canvasWidth, canvasHeight, color, opacity) {
        if (!slice) return;
        
        const imageData = ctx.createImageData(canvasWidth, canvasHeight);
        const data = imageData.data;
        
        const scaleX = slice.width / canvasWidth;
        const scaleY = slice.height / canvasHeight;
        
        for (let canvasY = 0; canvasY < canvasHeight; canvasY++) {
            for (let canvasX = 0; canvasX < canvasWidth; canvasX++) {
                const sliceX = Math.floor(canvasX * scaleX);
                const sliceY = Math.floor(canvasY * scaleY);
                const sliceIndex = sliceY * slice.width + sliceX;
                
                const value = slice.data[sliceIndex];
                
                if (value && value > 0) {
                    const pixelIndex = (canvasY * canvasWidth + canvasX) * 4;
                    data[pixelIndex] = color[0];     // R
                    data[pixelIndex + 1] = color[1]; // G
                    data[pixelIndex + 2] = color[2]; // B
                    data[pixelIndex + 3] = Math.floor(opacity * 255); // A
                }
            }
        }
        
        // Blend with existing canvas content
        ctx.globalCompositeOperation = 'source-over';
        ctx.putImageData(imageData, 0, 0);
    }

    /**
     * Reset visualization
     */
    reset() {
        this.segmentationData = null;
        this.referenceMask = null;
        this.exclusionMask = null;
        this.probabilityMask = null;
        this.shape = null;
        
        // Clear all canvases
        Object.values(this.contexts).forEach(ctx => {
            ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
        });
    }

    /**
     * Get current visualization state
     */
    getState() {
        return {
            currentSlices: { ...this.currentSlices },
            overlayOpacity: this.overlayOpacity,
            showOverlays: { ...this.showOverlays }
        };
    }

    /**
     * Set visualization state
     */
    setState(state) {
        if (state.currentSlices) {
            this.currentSlices = { ...state.currentSlices };
            this.updateSliceInfos();
        }
        
        if (state.overlayOpacity !== undefined) {
            this.overlayOpacity = state.overlayOpacity;
            document.getElementById('overlay-opacity').value = this.overlayOpacity;
            document.getElementById('opacity-value').textContent = this.overlayOpacity.toFixed(1);
        }
        
        if (state.showOverlays) {
            this.showOverlays = { ...state.showOverlays };
            Object.keys(this.showOverlays).forEach(type => {
                document.getElementById(`show-${type}`).checked = this.showOverlays[type];
            });
        }
        
        this.renderAll();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NiftiVisualization;
} else {
    window.NiftiVisualization = NiftiVisualization;
}