/**
 * Tests for PyodideBridge WebAssembly integration
 */

// Mock Pyodide
const mockPyodide = {
    runPython: jest.fn(),
    loadPackage: jest.fn().mockResolvedValue(undefined),
    globals: {
        set: jest.fn(),
        get: jest.fn()
    }
};

global.loadPyodide = jest.fn().mockResolvedValue(mockPyodide);

// Import the class directly
const PyodideBridge = require('../js/pyodide-bridge.js');

describe('PyodideBridge', () => {
    let bridge;

    beforeEach(() => {
        jest.clearAllMocks();
        bridge = new PyodideBridge();
    });

    describe('Initialization', () => {
        test('should initialize with correct default state', () => {
            expect(bridge.initialized).toBe(false);
            expect(bridge.pyodide).toBeNull();
            expect(bridge.packages).toEqual(['numpy', 'scipy', 'nibabel', 'scikit-image']);
        });

        test('should initialize Pyodide successfully', async () => {
            const progressCallback = jest.fn();
            
            await bridge.init(progressCallback);
            
            expect(global.loadPyodide).toHaveBeenCalled();
            expect(mockPyodide.loadPackage).toHaveBeenCalledWith(['numpy', 'scipy']);
            expect(mockPyodide.loadPackage).toHaveBeenCalledWith(['nibabel']);
            expect(mockPyodide.loadPackage).toHaveBeenCalledWith(['scikit-image']);
            expect(mockPyodide.runPython).toHaveBeenCalled();
            expect(bridge.initialized).toBe(true);
            expect(progressCallback).toHaveBeenCalledTimes(5);
        });

        test('should handle initialization errors', async () => {
            global.loadPyodide = jest.fn().mockRejectedValue(new Error('Pyodide load failed'));
            
            await expect(bridge.init()).rejects.toThrow('Failed to initialize Python runtime');
        });

        test('should return existing promise on multiple init calls', async () => {
            const promise1 = bridge.init();
            const promise2 = bridge.init();
            
            expect(promise1).toBe(promise2);
        });
    });

    describe('NIfTI Loading', () => {
        beforeEach(async () => {
            await bridge.init();
        });

        test('should load NIfTI file successfully', async () => {
            const mockFile = {
                arrayBuffer: jest.fn().mockResolvedValue(new ArrayBuffer(100))
            };

            const mockResult = {
                success: true,
                data: new Array(10).fill(new Array(10).fill(new Array(10).fill(0))),
                affine: [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
                header: {},
                shape: [10, 10, 10]
            };

            mockPyodide.runPython.mockReturnValue(mockResult);

            const result = await bridge.loadNifti(mockFile);

            expect(mockFile.arrayBuffer).toHaveBeenCalled();
            expect(mockPyodide.globals.set).toHaveBeenCalledWith('nifti_buffer', expect.any(Uint8Array));
            expect(mockPyodide.runPython).toHaveBeenCalled();
            expect(result).toEqual({
                data: mockResult.data,
                affine: mockResult.affine,
                header: mockResult.header,
                shape: mockResult.shape
            });
        });

        test('should handle NIfTI loading errors', async () => {
            const mockFile = {
                arrayBuffer: jest.fn().mockResolvedValue(new ArrayBuffer(100))
            };

            mockPyodide.runPython.mockReturnValue({
                success: false,
                error: 'Invalid NIfTI file'
            });

            await expect(bridge.loadNifti(mockFile)).rejects.toThrow('Invalid NIfTI file');
        });

        test('should throw error if not initialized', async () => {
            const uninitializedBridge = new window.PyodideBridge();
            const mockFile = { arrayBuffer: jest.fn() };

            await expect(uninitializedBridge.loadNifti(mockFile)).rejects.toThrow('Pyodide not initialized');
        });
    });

    describe('Reference Region Processing', () => {
        beforeEach(async () => {
            await bridge.init();
        });

        test('should process reference regions successfully', async () => {
            const mockSegmentation = {
                data: new Array(10).fill(new Array(10).fill(new Array(10).fill(1)))
            };

            const mockParameters = {
                referenceIndices: [1, 2],
                exclusionIndices: [3],
                probabilityData: null,
                probThreshold: 0.5,
                erosionSize: 1,
                exclusionDilation: 2
            };

            const mockResult = {
                success: true,
                reference_mask: new Array(10).fill(new Array(10).fill(new Array(10).fill(true))),
                exclusion_mask: new Array(10).fill(new Array(10).fill(new Array(10).fill(false))),
                probability_mask: new Array(10).fill(new Array(10).fill(new Array(10).fill(true))),
                stats: {
                    reference_voxels: 800,
                    exclusion_voxels: 100,
                    probability_removed: 0,
                    total_brain_voxels: 1000
                }
            };

            mockPyodide.runPython.mockReturnValue(mockResult);

            const result = await bridge.processReferenceRegions(mockSegmentation, mockParameters);

            expect(mockPyodide.globals.set).toHaveBeenCalledWith('seg_data', mockSegmentation.data);
            expect(mockPyodide.globals.set).toHaveBeenCalledWith('ref_indices', mockParameters.referenceIndices);
            expect(mockPyodide.globals.set).toHaveBeenCalledWith('excl_indices', mockParameters.exclusionIndices);
            
            expect(result).toEqual({
                referenceMask: mockResult.reference_mask,
                exclusionMask: mockResult.exclusion_mask,
                probabilityMask: mockResult.probability_mask,
                stats: mockResult.stats
            });
        });

        test('should handle processing errors', async () => {
            const mockSegmentation = { data: [] };
            const mockParameters = { referenceIndices: [1] };

            mockPyodide.runPython.mockReturnValue({
                success: false,
                error: 'Processing failed'
            });

            await expect(bridge.processReferenceRegions(mockSegmentation, mockParameters))
                .rejects.toThrow('Processing failed');
        });

        test('should handle probability data correctly', async () => {
            const mockSegmentation = { data: [] };
            const mockProbability = { data: new Array(1000).fill(0.8) };
            const mockParameters = {
                referenceIndices: [1],
                probabilityData: mockProbability,
                probThreshold: 0.5
            };

            mockPyodide.runPython.mockReturnValue({ success: true, stats: {} });

            await bridge.processReferenceRegions(mockSegmentation, mockParameters);

            expect(mockPyodide.globals.set).toHaveBeenCalledWith('prob_data', mockProbability.data);
            expect(mockPyodide.globals.set).toHaveBeenCalledWith('prob_threshold', 0.5);
        });
    });

    describe('NIfTI Saving', () => {
        beforeEach(async () => {
            await bridge.init();
        });

        test('should save NIfTI successfully', async () => {
            const mockMask = new Array(10).fill(new Array(10).fill(new Array(10).fill(true)));
            const mockAffine = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
            const mockHeader = {};

            const mockResult = {
                success: true,
                data: [1, 2, 3, 4, 5]
            };

            mockPyodide.runPython.mockReturnValue(mockResult);

            const result = await bridge.saveNifti(mockMask, mockAffine, mockHeader);

            expect(mockPyodide.globals.set).toHaveBeenCalledWith('mask_data', mockMask);
            expect(mockPyodide.globals.set).toHaveBeenCalledWith('affine', mockAffine);
            expect(mockPyodide.globals.set).toHaveBeenCalledWith('header', mockHeader);
            expect(result).toBeInstanceOf(Uint8Array);
            expect(Array.from(result)).toEqual([1, 2, 3, 4, 5]);
        });

        test('should handle saving errors', async () => {
            mockPyodide.runPython.mockReturnValue({
                success: false,
                error: 'Save failed'
            });

            await expect(bridge.saveNifti([], [], {})).rejects.toThrow('Save failed');
        });
    });

    describe('Utility Methods', () => {
        test('should report initialization status correctly', () => {
            expect(bridge.isInitialized()).toBe(false);
        });

        test('should provide access to Pyodide instance', async () => {
            await bridge.init();
            
            expect(bridge.getPyodide()).toBe(mockPyodide);
        });

        test('should report initialization status correctly after init', async () => {
            await bridge.init();
            
            expect(bridge.isInitialized()).toBe(true);
        });
    });

    describe('Error Handling', () => {
        test('should handle Pyodide loading failure gracefully', async () => {
            global.loadPyodide = jest.fn().mockRejectedValue(new Error('Network error'));
            const newBridge = new window.PyodideBridge();

            await expect(newBridge.init()).rejects.toThrow('Failed to initialize Python runtime: Network error');
        });

        test('should handle package loading failure', async () => {
            mockPyodide.loadPackage = jest.fn().mockRejectedValue(new Error('Package not found'));
            const newBridge = new window.PyodideBridge();

            await expect(newBridge.init()).rejects.toThrow('Failed to initialize Python runtime');
        });
    });
});