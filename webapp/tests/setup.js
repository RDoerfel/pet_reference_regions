/**
 * Test setup file - configure global mocks and environment
 */

// Mock Pyodide globally
global.loadPyodide = jest.fn().mockResolvedValue({
    runPython: jest.fn(),
    loadPackage: jest.fn().mockResolvedValue(undefined),
    globals: {
        set: jest.fn(),
        get: jest.fn()
    }
});

// Mock browser APIs
global.File = class MockFile {
    constructor(parts, filename, options = {}) {
        this.name = filename;
        this.size = parts.reduce((sum, part) => sum + (typeof part === 'string' ? part.length : part.byteLength || 0), 0);
        this.type = options.type || '';
    }
    
    async arrayBuffer() {
        return new ArrayBuffer(this.size);
    }
};

global.Blob = jest.fn();
global.URL = {
    createObjectURL: jest.fn(() => 'mock-url'),
    revokeObjectURL: jest.fn()
};

// Mock alert
global.alert = jest.fn();

// Enhanced DOM mocking for jsdom
const mockElement = (tag, id) => {
    const element = document.createElement(tag);
    if (id) element.id = id;
    
    // Add common properties
    element.value = tag === 'input' ? '50' : '';
    element.textContent = '';
    element.innerHTML = '';
    element.checked = true;
    element.min = '0';
    element.max = '100';
    element.style = { display: 'block' };
    
    // Canvas-specific properties
    if (tag === 'canvas') {
        element.width = 256;
        element.height = 256;
        element.getContext = jest.fn(() => ({
            clearRect: jest.fn(),
            createImageData: jest.fn(() => ({
                data: new Uint8ClampedArray(256 * 256 * 4)
            })),
            putImageData: jest.fn(),
            globalCompositeOperation: 'source-over',
            canvas: element
        }));
    }
    
    return element;
};

// Mock document.getElementById to return properly configured elements
const originalGetElementById = document.getElementById;
document.getElementById = jest.fn((id) => {
    const elementMap = {
        'segmentation-upload': mockElement('div', id),
        'segmentation-input': mockElement('input', id),
        'seg-file-info': mockElement('span', id),
        'probability-upload': mockElement('div', id),
        'probability-input': mockElement('input', id),
        'prob-file-info': mockElement('span', id),
        'reference-indices': (() => { const el = mockElement('input', id); el.value = '7,8'; return el; })(),
        'exclusion-indices': mockElement('input', id),
        'prob-threshold': (() => { const el = mockElement('input', id); el.value = '0.5'; return el; })(),
        'prob-threshold-value': mockElement('span', id),
        'erosion-size': (() => { const el = mockElement('input', id); el.value = '1'; return el; })(),
        'exclusion-dilation': (() => { const el = mockElement('input', id); el.value = '2'; return el; })(),
        'process-btn': mockElement('button', id),
        'download-btn': mockElement('button', id),
        'parameters-section': mockElement('section', id),
        'visualization-section': mockElement('section', id),
        'results-section': mockElement('section', id),
        'status-overlay': mockElement('div', id),
        'status-message': mockElement('div', id),
        'progress-fill': mockElement('div', id),
        'processing-summary': mockElement('div', id),
        'axial-canvas': mockElement('canvas', id),
        'coronal-canvas': mockElement('canvas', id),
        'sagittal-canvas': mockElement('canvas', id),
        'axial-slider': mockElement('input', id),
        'coronal-slider': mockElement('input', id),
        'sagittal-slider': mockElement('input', id),
        'axial-slice-info': mockElement('span', id),
        'coronal-slice-info': mockElement('span', id),
        'sagittal-slice-info': mockElement('span', id),
        'overlay-opacity': (() => { const el = mockElement('input', id); el.value = '0.7'; return el; })(),
        'opacity-value': mockElement('span', id),
        'show-reference': (() => { const el = mockElement('input', id); el.type = 'checkbox'; return el; })(),
        'show-exclusion': (() => { const el = mockElement('input', id); el.type = 'checkbox'; return el; })(),
        'show-probability': (() => { const el = mockElement('input', id); el.type = 'checkbox'; return el; })()
    };
    
    return elementMap[id] || originalGetElementById.call(document, id);
});

// Mock document.createElement for dynamic elements
const originalCreateElement = document.createElement;
document.createElement = jest.fn((tag) => {
    const element = originalCreateElement.call(document, tag);
    
    if (tag === 'a') {
        element.click = jest.fn();
        element.href = '';
        element.download = '';
    }
    
    return element;
});

// Mock DOM methods
document.body.appendChild = jest.fn();
document.body.removeChild = jest.fn();