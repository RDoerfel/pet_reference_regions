/**
 * Tests for PETRefRegionApp main application
 */

const PyodideBridge = require('../js/pyodide-bridge.js');
const NiftiVisualization = require('../js/visualization.js');
const PETRefRegionApp = require('../js/app.js');

// Mock the classes
jest.mock('../js/pyodide-bridge.js');
jest.mock('../js/visualization.js');

describe('PETRefRegionApp', () => {
    let app;
    let mockPyodideBridge;
    let mockVisualization;

    beforeEach(() => {
        jest.clearAllMocks();
        
        // Setup mocks
        mockPyodideBridge = {
            init: jest.fn().mockResolvedValue(true),
            loadNifti: jest.fn().mockResolvedValue({
                data: new Array(10).fill(new Array(10).fill(new Array(10).fill(0))),
                shape: [10, 10, 10],
                affine: [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
                header: {}
            }),
            processReferenceRegions: jest.fn().mockResolvedValue({
                referenceMask: new Array(10).fill(new Array(10).fill(new Array(10).fill(false))),
                exclusionMask: new Array(10).fill(new Array(10).fill(new Array(10).fill(false))),
                probabilityMask: new Array(10).fill(new Array(10).fill(new Array(10).fill(true))),
                stats: {
                    reference_voxels: 100,
                    exclusion_voxels: 50,
                    probability_removed: 25,
                    total_brain_voxels: 1000
                }
            }),
            saveNifti: jest.fn().mockResolvedValue(new Uint8Array([1, 2, 3, 4])),
            isInitialized: jest.fn().mockReturnValue(true)
        };

        mockVisualization = {
            loadSegmentation: jest.fn(),
            loadMasks: jest.fn(),
            reset: jest.fn()
        };

        PyodideBridge.mockImplementation(() => mockPyodideBridge);
        NiftiVisualization.mockImplementation(() => mockVisualization);
        
        // Create app instance
        app = new PETRefRegionApp();
    });

    describe('Initialization', () => {
        test('should initialize with correct default state', () => {
            expect(app.segmentationFile).toBeNull();
            expect(app.probabilityFile).toBeNull();
            expect(app.segmentationData).toBeNull();
            expect(app.probabilityData).toBeNull();
            expect(app.processedResults).toBeNull();
        });

        test('should initialize PyodideBridge and NiftiVisualization', () => {
            expect(PyodideBridge).toHaveBeenCalled();
            expect(NiftiVisualization).toHaveBeenCalled();
        });
    });

    describe('File Handling', () => {
        test('should identify NIfTI files correctly', () => {
            expect(app.isNiftiFile({ name: 'test.nii' })).toBe(true);
            expect(app.isNiftiFile({ name: 'test.nii.gz' })).toBe(true);
            expect(app.isNiftiFile({ name: 'test.NII' })).toBe(true);
            expect(app.isNiftiFile({ name: 'test.txt' })).toBe(false);
        });

        test('should handle segmentation file upload', async () => {
            const mockFile = new File(['mock-data'], 'segmentation.nii.gz');
            
            await app.handleSegmentationFile(mockFile);
            
            expect(app.segmentationFile).toBe(mockFile);
            expect(mockPyodideBridge.loadNifti).toHaveBeenCalledWith(mockFile);
            expect(app.elements.segFileInfo.textContent).toContain('segmentation.nii.gz');
            expect(mockVisualization.loadSegmentation).toHaveBeenCalled();
        });

        test('should handle probability file upload', async () => {
            const mockFile = new File(['mock-data'], 'probability.nii');
            
            await app.handleProbabilityFile(mockFile);
            
            expect(app.probabilityFile).toBe(mockFile);
            expect(mockPyodideBridge.loadNifti).toHaveBeenCalledWith(mockFile);
            expect(app.elements.probFileInfo.textContent).toContain('probability.nii');
        });
    });

    describe('Parameter Processing', () => {
        test('should parse processing parameters correctly', () => {
            app.elements.refIndices.value = '1,2,3';
            app.elements.exclIndices.value = '4,5';
            app.elements.probThreshold.value = '0.8';
            app.elements.erosionSize.value = '2';
            app.elements.exclDilation.value = '3';
            
            const params = app.getProcessingParameters();
            
            expect(params.referenceIndices).toEqual([1, 2, 3]);
            expect(params.exclusionIndices).toEqual([4, 5]);
            expect(params.probThreshold).toBe(0.8);
            expect(params.erosionSize).toBe(2);
            expect(params.exclusionDilation).toBe(3);
        });

        test('should handle empty parameter fields', () => {
            app.elements.refIndices.value = '';
            app.elements.exclIndices.value = '';
            
            const params = app.getProcessingParameters();
            
            expect(params.referenceIndices).toEqual([]);
            expect(params.exclusionIndices).toEqual([]);
        });

        test('should filter out invalid indices', () => {
            app.elements.refIndices.value = '1,abc,2,3.5,4';
            
            const params = app.getProcessingParameters();
            
            expect(params.referenceIndices).toEqual([1, 2, 4]);
        });
    });

    describe('Processing Pipeline', () => {
        beforeEach(() => {
            app.segmentationData = {
                data: new Array(10).fill(new Array(10).fill(new Array(10).fill(0))),
                shape: [10, 10, 10],
                affine: [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
                header: {}
            };
        });

        test('should process reference regions successfully', async () => {
            await app.processReferenceRegions();
            
            expect(mockPyodideBridge.processReferenceRegions).toHaveBeenCalled();
            expect(mockVisualization.loadMasks).toHaveBeenCalled();
            expect(app.processedResults).toBeDefined();
        });

        test('should handle missing segmentation data', async () => {
            app.segmentationData = null;
            
            await app.processReferenceRegions();
            
            expect(global.alert).toHaveBeenCalledWith(
                expect.stringContaining('Please load a segmentation file first')
            );
        });

        test('should validate reference indices', async () => {
            app.elements.refIndices.value = '';
            
            await app.processReferenceRegions();
            
            expect(global.alert).toHaveBeenCalledWith(
                expect.stringContaining('Please specify at least one reference index')
            );
        });
    });

    describe('Results and Download', () => {
        beforeEach(() => {
            app.processedResults = {
                referenceMask: new Array(10).fill(new Array(10).fill(new Array(10).fill(false))),
                stats: {
                    reference_voxels: 100,
                    exclusion_voxels: 50,
                    probability_removed: 25,
                    total_brain_voxels: 1000
                }
            };
            
            app.segmentationData = {
                affine: [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
                header: {}
            };
            
            app.segmentationFile = { name: 'test.nii.gz' };
        });

        test('should display processing results correctly', () => {
            app.showProcessingResults(app.processedResults.stats);
            
            const summary = app.elements.processingSummary.innerHTML;
            expect(summary).toContain('Processing Complete!');
            expect(summary).toContain('100');
            expect(summary).toContain('50');
            expect(summary).toContain('25');
            expect(summary).toContain('1,000');
        });

        test('should generate appropriate filename for download', () => {
            app.elements.refIndices.value = '7,8';
            
            const filename = app.generateFilename();
            
            expect(filename).toBe('test_refregion_7-8.nii.gz');
        });

        test('should handle download process', async () => {
            const mockLink = {
                href: '',
                download: '',
                click: jest.fn()
            };
            
            document.createElement.mockReturnValue(mockLink);
            
            await app.downloadResults();
            
            expect(mockPyodideBridge.saveNifti).toHaveBeenCalled();
            expect(global.Blob).toHaveBeenCalled();
            expect(mockLink.click).toHaveBeenCalled();
        });

        test('should handle download without results', async () => {
            app.processedResults = null;
            
            await app.downloadResults();
            
            expect(global.alert).toHaveBeenCalledWith(
                expect.stringContaining('No processed results to download')
            );
        });
    });

    describe('UI Utilities', () => {
        test('should format file sizes correctly', () => {
            expect(app.formatFileSize(500)).toBe('500.0 B');
            expect(app.formatFileSize(1536)).toBe('1.5 KB');
            expect(app.formatFileSize(1048576)).toBe('1.0 MB');
            expect(app.formatFileSize(1073741824)).toBe('1.0 GB');
        });

        test('should show and hide status overlay', () => {
            app.showStatus('Testing...', 50);
            
            expect(app.elements.statusMessage.textContent).toBe('Testing...');
            expect(app.elements.progressFill.style.width).toBe('50%');
            expect(app.elements.statusOverlay.style.display).toBe('flex');
            
            app.hideStatus();
            
            expect(app.elements.statusOverlay.style.display).toBe('none');
        });
    });
});