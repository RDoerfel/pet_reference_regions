# Testing Documentation

This document provides detailed information about the comprehensive test suite for the PET Reference Regions package.

## Test Suite Overview

The project includes **75+ comprehensive tests** ensuring reliability, robustness, and prevention of regressions across all components.

## Test Structure

### Core Functionality Tests (11 tests)

**`test_morphology.py` (2 tests)**
- Morphological operations: erosion and dilation algorithms
- Binary mask processing with different structuring elements

**`test_refregion.py` (5 tests)**  
- Custom reference region creation from anatomical indices
- Integration with morphological operations
- Processing pipeline validation

**`test_cerebellum.py` (4 tests)**
- Cerebellar reference region creation
- SUIT/FastSurfer integration
- Vermis exclusion and cortical spillover prevention

### Web GUI Tests (64 tests)

**`test_webgui_app.py` (17 tests)**
- NIfTI file loading with different extensions (.nii, .nii.gz)
- Processing pipeline with intermediate results
- UI structure validation and error handling
- Base64 image conversion for web display
- Matplotlib figure management and memory cleanup
- Complex morphological operations testing

**`test_webgui_utils.py` (14 tests)**
- Multi-plane slice extraction (axial, coronal, sagittal)
- Unique anatomical indices detection and parsing
- Middle slice calculation for different dimensions
- Bounds checking and complex data structure handling
- Edge cases with floating-point and negative values

**`test_webgui_visualization.py` (16 tests)**
- Array normalization with various data types
- Single and dual overlay visualization systems
- Image rotation (90° counterclockwise) for proper display
- Multiple colormap support and custom figure sizes
- Side-by-side comparison figures
- Transparency handling and axis configuration
- Empty overlay and size mismatch robustness

**`test_webgui_file_handler.py` (17 tests)**
- FileManager initialization and upload directory management
- File saving with various array shapes and formats
- Data retrieval and result persistence
- Affine transformation preservation across operations
- Data type conversion (uint8) for binary masks
- Multi-file handling and instance isolation
- Large file support (50MB+ arrays)
- Concurrent file operations and error handling

## Key Testing Features

### Comprehensive Coverage
- **Dual Overlay Visualization**: Green overlays for final results, red for dilated exclusions
- **Multi-Plane Views**: Validation across axial, coronal, and sagittal viewing planes
- **Real-Time Processing**: Interactive parameter controls with live preview
- **File Format Handling**: NIfTI extension preservation for proper nibabel loading

### Robustness Testing
- **Error Handling**: Invalid inputs, missing files, corrupted data
- **Edge Cases**: Empty arrays, single voxels, extremely large erosion values
- **Memory Management**: Matplotlib figure cleanup, temporary file handling
- **Concurrent Operations**: Multiple file uploads and processing streams

### Performance Testing
- **Large Files**: Arrays up to 50MB+ (50×60×40 voxels)
- **Complex Operations**: Multi-step morphological processing pipelines  
- **Real-Time Updates**: Parameter changes with immediate visualization

## Running Tests

### All Tests
```bash
poetry run pytest                        # Run complete test suite (75+ tests)
poetry run pytest --cov=refregion        # With coverage reporting
poetry run pytest -v                     # Verbose output with test names
```

### Specific Test Categories
```bash
poetry run pytest tests/test_webgui_*.py        # WebGUI tests only (64 tests)
poetry run pytest tests/test_morphology.py      # Core morphology tests
poetry run pytest tests/test_refregion.py       # Reference region tests
poetry run pytest tests/test_cerebellum.py      # Cerebellar processing tests
```

### Individual Test Files
```bash
poetry run pytest tests/test_webgui_app.py::test_dual_overlay          # Specific test
poetry run pytest tests/test_webgui_visualization.py -k "colormap"     # Pattern matching
```

## Test Quality Standards

### Code Coverage
- **Target**: >90% code coverage across all modules
- **WebGUI**: Complete coverage of all new features and edge cases
- **Core**: Full coverage of mathematical operations and algorithms

### Test Patterns
- **Isolation**: Each test is independent with proper setup/teardown
- **Mocking**: External dependencies (file system, matplotlib) appropriately mocked
- **Fixtures**: Reusable test data and helper functions
- **Parameterization**: Multiple scenarios tested with single test functions

### Continuous Integration
- **Automated Testing**: All tests run on every commit via GitHub Actions
- **Multi-Python**: Tests run across Python 3.9, 3.10, 3.11
- **Platform Coverage**: Linux, macOS, Windows compatibility validation

## Contributing to Tests

When adding new features or fixing bugs:

1. **Write Tests First**: Follow TDD principles where possible
2. **Cover Edge Cases**: Include boundary conditions and error scenarios  
3. **Test Integration**: Ensure new features work with existing components
4. **Document Complex Tests**: Add docstrings explaining test purpose and setup
5. **Maintain Performance**: Large test data should be generated, not stored

### Test File Naming Convention
- `test_<module_name>.py` for core functionality tests
- `test_webgui_<component>.py` for web GUI component tests
- Test functions: `test_<functionality>_<scenario>()`

### Example Test Structure
```python
def test_new_feature_basic_functionality():
    """Test basic functionality of new feature."""
    # Arrange: Set up test data
    test_data = create_test_data()
    
    # Act: Execute the functionality
    result = new_feature(test_data)
    
    # Assert: Verify expected behavior
    assert result.shape == expected_shape
    assert np.allclose(result, expected_values)

def test_new_feature_edge_cases():
    """Test edge cases and error conditions."""
    with pytest.raises(ValueError, match="Invalid input"):
        new_feature(invalid_data)
```

This comprehensive test suite ensures that the PET Reference Regions package remains reliable, maintainable, and robust across all supported use cases.