/**
 * Tests for NiftiVisualization Canvas-based 3D viewer
 */

// Mock Canvas API
const mockCanvas = {
    width: 256,
    height: 256,
    getContext: jest.fn(() => ({
        clearRect: jest.fn(),
        createImageData: jest.fn(() => ({
            data: new Uint8ClampedArray(256 * 256 * 4)
        })),
        putImageData: jest.fn(),
        globalCompositeOperation: ''
    }))
};

// Mock DOM elements
const createMockElement = (id, type = 'div') => {
    const element = {
        id,
        type,
        value: type === 'input' ? '50' : '',
        textContent: '',
        max: '100',
        min: '0',
        checked: true,
        style: { display: 'block' },
        addEventListener: jest.fn()
    };
    
    if (id.includes('canvas')) {
        Object.assign(element, mockCanvas);
    }
    
    return element;
};

// Mock document.getElementById
const mockElements = {
    'axial-canvas': createMockElement('axial-canvas', 'canvas'),
    'coronal-canvas': createMockElement('coronal-canvas', 'canvas'),
    'sagittal-canvas': createMockElement('sagittal-canvas', 'canvas'),
    'axial-slider': createMockElement('axial-slider', 'input'),
    'coronal-slider': createMockElement('coronal-slider', 'input'),
    'sagittal-slider': createMockElement('sagittal-slider', 'input'),
    'axial-slice-info': createMockElement('axial-slice-info'),
    'coronal-slice-info': createMockElement('coronal-slice-info'),
    'sagittal-slice-info': createMockElement('sagittal-slice-info'),
    'overlay-opacity': createMockElement('overlay-opacity', 'input'),
    'opacity-value': createMockElement('opacity-value'),
    'show-reference': createMockElement('show-reference', 'input'),
    'show-exclusion': createMockElement('show-exclusion', 'input'),
    'show-probability': createMockElement('show-probability', 'input')
};

document.getElementById = jest.fn((id) => mockElements[id]);

describe('NiftiVisualization', () => {
    let visualization;

    beforeEach(() => {
        jest.clearAllMocks();
        
        // Reset mock element values
        Object.values(mockElements).forEach(element => {
            if (element.addEventListener) {
                element.addEventListener.mockClear();
            }
        });
        
        // Load the visualization module
        require('../js/visualization.js');
        visualization = new window.NiftiVisualization();
    });

    describe('Initialization', () => {
        test('should initialize with correct default state', () => {
            expect(visualization.segmentationData).toBeNull();
            expect(visualization.referenceMask).toBeNull();
            expect(visualization.exclusionMask).toBeNull();
            expect(visualization.probabilityMask).toBeNull();
            expect(visualization.overlayOpacity).toBe(0.7);
            expect(visualization.showOverlays).toEqual({
                reference: true,
                exclusion: true,
                probability: true
            });
        });

        test('should initialize canvas elements', () => {
            expect(visualization.canvases.axial).toBe(mockElements['axial-canvas']);
            expect(visualization.canvases.coronal).toBe(mockElements['coronal-canvas']);
            expect(visualization.canvases.sagittal).toBe(mockElements['sagittal-canvas']);
        });

        test('should setup event listeners', () => {
            const views = ['axial', 'coronal', 'sagittal'];
            
            views.forEach(view => {
                expect(mockElements[`${view}-slider`].addEventListener).toHaveBeenCalledWith('input', expect.any(Function));
            });
            
            expect(mockElements['overlay-opacity'].addEventListener).toHaveBeenCalledWith('input', expect.any(Function));
            expect(mockElements['show-reference'].addEventListener).toHaveBeenCalledWith('change', expect.any(Function));
            expect(mockElements['show-exclusion'].addEventListener).toHaveBeenCalledWith('change', expect.any(Function));
            expect(mockElements['show-probability'].addEventListener).toHaveBeenCalledWith('change', expect.any(Function));
        });
    });

    describe('Data Loading', () => {
        test('should load segmentation data correctly', () => {
            const mockData = new Array(64).fill(new Array(64).fill(new Array(32).fill(1)));
            const mockShape = [64, 64, 32];

            visualization.loadSegmentation(mockData, mockShape);

            expect(visualization.segmentationData).toBe(mockData);
            expect(visualization.shape).toEqual(mockShape);
            expect(visualization.currentSlices).toEqual({
                x: 32, // floor(64/2)
                y: 32, // floor(64/2)  
                z: 16  // floor(32/2)
            });
        });

        test('should update slider ranges when loading data', () => {
            const mockShape = [100, 80, 60];

            visualization.loadSegmentation([], mockShape);

            expect(mockElements['sagittal-slider'].max).toBe('99');  // shape[0] - 1
            expect(mockElements['coronal-slider'].max).toBe('79');   // shape[1] - 1
            expect(mockElements['axial-slider'].max).toBe('59');     // shape[2] - 1
        });

        test('should load masks for overlay visualization', () => {
            const mockReference = new Array(10).fill(new Array(10).fill(new Array(10).fill(true)));
            const mockExclusion = new Array(10).fill(new Array(10).fill(new Array(10).fill(false)));
            const mockProbability = new Array(10).fill(new Array(10).fill(new Array(10).fill(true)));

            visualization.loadMasks(mockReference, mockExclusion, mockProbability);

            expect(visualization.referenceMask).toBe(mockReference);
            expect(visualization.exclusionMask).toBe(mockExclusion);
            expect(visualization.probabilityMask).toBe(mockProbability);
        });
    });

    describe('Slice Extraction', () => {
        beforeEach(() => {
            // Setup test data: 4x4x4 array with known values
            const testData = [];
            for (let x = 0; x < 4; x++) {
                testData[x] = [];
                for (let y = 0; y < 4; y++) {
                    testData[x][y] = [];
                    for (let z = 0; z < 4; z++) {
                        testData[x][y][z] = x * 100 + y * 10 + z;
                    }
                }
            }
            
            visualization.segmentationData = testData;
            visualization.shape = [4, 4, 4];
        });

        test('should extract axial slice correctly', () => {
            const slice = visualization.getAxialSlice(visualization.segmentationData, 2);

            expect(slice.width).toBe(4);
            expect(slice.height).toBe(4);
            expect(slice.data.length).toBe(16);
            
            // Check specific values (z=2, so all values should end in 2)
            expect(slice.data[0]).toBe(2);   // x=0, y=0, z=2
            expect(slice.data[4]).toBe(102); // x=0, y=1, z=2
            expect(slice.data[1]).toBe(102); // x=1, y=0, z=2
        });

        test('should extract coronal slice correctly', () => {
            const slice = visualization.getCoronalSlice(visualization.segmentationData, 1);

            expect(slice.width).toBe(4);
            expect(slice.height).toBe(4);
            expect(slice.data.length).toBe(16);
            
            // Check specific values (y=1, flipped Z)
            expect(slice.data[12]).toBe(10); // x=0, y=1, z=0 (bottom row after flip)
            expect(slice.data[13]).toBe(110); // x=1, y=1, z=0
        });

        test('should extract sagittal slice correctly', () => {
            const slice = visualization.getSagittalSlice(visualization.segmentationData, 2);

            expect(slice.width).toBe(4);
            expect(slice.height).toBe(4);
            expect(slice.data.length).toBe(16);
            
            // Check specific values (x=2, flipped Z)
            expect(slice.data[12]).toBe(200); // x=2, y=0, z=0 (bottom row after flip)
            expect(slice.data[13]).toBe(210); // x=2, y=1, z=0
        });

        test('should handle out-of-bounds slice requests', () => {
            expect(visualization.getAxialSlice(visualization.segmentationData, -1)).toBeNull();
            expect(visualization.getAxialSlice(visualization.segmentationData, 4)).toBeNull();
            expect(visualization.getCoronalSlice(visualization.segmentationData, 5)).toBeNull();
            expect(visualization.getSagittalSlice(visualization.segmentationData, -2)).toBeNull();
        });

        test('should handle null data gracefully', () => {
            expect(visualization.getAxialSlice(null, 0)).toBeNull();
            expect(visualization.getCoronalSlice(undefined, 0)).toBeNull();
        });
    });

    describe('Slice Navigation', () => {
        beforeEach(() => {
            visualization.shape = [100, 80, 60];
            visualization.currentSlices = { x: 50, y: 40, z: 30 };
        });

        test('should update slice position correctly', () => {
            visualization.updateSlice('axial', 45);
            expect(visualization.currentSlices.z).toBe(45);

            visualization.updateSlice('coronal', 35);
            expect(visualization.currentSlices.y).toBe(35);

            visualization.updateSlice('sagittal', 25);
            expect(visualization.currentSlices.x).toBe(25);
        });

        test('should update slice info displays', () => {
            visualization.updateSliceInfos();

            expect(mockElements['axial-slice-info'].textContent).toBe('Slice: 31/60');
            expect(mockElements['coronal-slice-info'].textContent).toBe('Slice: 41/80');
            expect(mockElements['sagittal-slice-info'].textContent).toBe('Slice: 51/100');
        });
    });

    describe('Overlay Controls', () => {
        test('should update overlay opacity', () => {
            const opacitySlider = mockElements['overlay-opacity'];
            const opacityValue = mockElements['opacity-value'];
            
            // Simulate opacity change event
            opacitySlider.value = '0.3';
            const eventCallback = opacitySlider.addEventListener.mock.calls.find(
                call => call[0] === 'input'
            )[1];
            
            eventCallback({ target: { value: '0.3' } });
            
            expect(visualization.overlayOpacity).toBe(0.3);
        });

        test('should toggle overlay visibility', () => {
            const referenceToggle = mockElements['show-reference'];
            
            // Simulate toggle event
            const eventCallback = referenceToggle.addEventListener.mock.calls.find(
                call => call[0] === 'change'
            )[1];
            
            eventCallback({ target: { checked: false } });
            
            expect(visualization.showOverlays.reference).toBe(false);
        });
    });

    describe('State Management', () => {
        test('should get current state correctly', () => {
            visualization.currentSlices = { x: 10, y: 20, z: 30 };
            visualization.overlayOpacity = 0.8;
            visualization.showOverlays = { reference: false, exclusion: true, probability: false };

            const state = visualization.getState();

            expect(state).toEqual({
                currentSlices: { x: 10, y: 20, z: 30 },
                overlayOpacity: 0.8,
                showOverlays: { reference: false, exclusion: true, probability: false }
            });
        });

        test('should set state correctly', () => {
            const newState = {
                currentSlices: { x: 5, y: 15, z: 25 },
                overlayOpacity: 0.9,
                showOverlays: { reference: true, exclusion: false, probability: true }
            };

            visualization.setState(newState);

            expect(visualization.currentSlices).toEqual(newState.currentSlices);
            expect(visualization.overlayOpacity).toBe(0.9);
            expect(visualization.showOverlays).toEqual(newState.showOverlays);
        });

        test('should handle partial state updates', () => {
            const originalSlices = { x: 10, y: 20, z: 30 };
            visualization.currentSlices = originalSlices;
            
            visualization.setState({ overlayOpacity: 0.6 });

            expect(visualization.currentSlices).toEqual(originalSlices);
            expect(visualization.overlayOpacity).toBe(0.6);
        });
    });

    describe('Reset and Cleanup', () => {
        test('should reset visualization state', () => {
            // Set some data
            visualization.segmentationData = [1, 2, 3];
            visualization.referenceMask = [true, false];
            visualization.shape = [10, 10, 10];

            visualization.reset();

            expect(visualization.segmentationData).toBeNull();
            expect(visualization.referenceMask).toBeNull();
            expect(visualization.exclusionMask).toBeNull();
            expect(visualization.probabilityMask).toBeNull();
            expect(visualization.shape).toBeNull();
        });

        test('should clear canvases on reset', () => {
            const contexts = Object.values(visualization.contexts);
            
            visualization.reset();

            contexts.forEach(ctx => {
                expect(ctx.clearRect).toHaveBeenCalledWith(0, 0, ctx.canvas.width, ctx.canvas.height);
            });
        });
    });
});