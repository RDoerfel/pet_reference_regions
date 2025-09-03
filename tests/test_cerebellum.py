import pytest
import numpy as np
import nibabel as nib
from refregion.cerebellum import cerebellum_reference_region


def create_test_nifti_image(data, affine=None):
    """Helper to create test NIfTI images."""
    if affine is None:
        affine = np.eye(4)
    return nib.Nifti1Image(data, affine)


def test_cerebellum_reference_region_basic():
    """Test basic cerebellum reference region creation."""
    # Create test data
    cerebellum_data = np.zeros((10, 10, 10))
    brain_data = np.zeros((10, 10, 10))
    
    # Add cerebellum regions (no vermis)
    cerebellum_data[2:4, 2:4, 2:4] = 601  # Cerebellum region
    cerebellum_data[6:8, 6:8, 6:8] = 602  # Another cerebellum region
    
    # Add cortical regions in brain
    brain_data[1:3, 1:3, 1:3] = 3   # Left cortex
    brain_data[7:9, 7:9, 7:9] = 42  # Right cortex
    
    # Create NIfTI images
    cerebellum_img = create_test_nifti_image(cerebellum_data)
    brain_img = create_test_nifti_image(brain_data)
    
    result = cerebellum_reference_region(cerebellum_img, brain_img)
    
    # Result should be a NIfTI image
    assert isinstance(result, nib.Nifti1Image)
    
    # Should have some non-zero values
    result_data = result.get_fdata()
    assert result_data.sum() > 0


def test_cerebellum_reference_region_with_vermis():
    """Test cerebellum reference region with vermis exclusion."""
    cerebellum_data = np.zeros((15, 15, 15))
    brain_data = np.zeros((15, 15, 15))
    
    # Add cerebellum regions
    cerebellum_data[2:5, 2:5, 2:5] = 601  # Cerebellum region
    
    # Add vermis region
    cerebellum_data[3:4, 3:4, 3:4] = 606  # Vermis region
    
    # Add cortical regions
    brain_data[1:3, 1:3, 1:3] = 3
    
    cerebellum_img = create_test_nifti_image(cerebellum_data)
    brain_img = create_test_nifti_image(brain_data)
    
    result = cerebellum_reference_region(
        cerebellum_img, brain_img, 
        erode_cerebellum_by_voxels=1,
        dilate_vermis_by_voxels=2,
        dilate_cortex_by_voxels=2
    )
    
    result_data = result.get_fdata()
    
    # Should be binary (0 or 1)
    assert np.all((result_data == 0) | (result_data == 1))
    
    # Should have reduced volume due to vermis and cortex exclusion
    original_cerebellum = (cerebellum_data == 601).sum()
    assert result_data.sum() <= original_cerebellum


def test_cerebellum_reference_region_affine_preservation():
    """Test that affine matrix is preserved."""
    cerebellum_data = np.zeros((5, 5, 5))
    brain_data = np.zeros((5, 5, 5))
    
    cerebellum_data[2, 2, 2] = 601
    
    # Custom affine matrix
    custom_affine = np.array([
        [2, 0, 0, -10],
        [0, 2, 0, -10], 
        [0, 0, 2, -10],
        [0, 0, 0, 1]
    ])
    
    cerebellum_img = create_test_nifti_image(cerebellum_data, custom_affine)
    brain_img = create_test_nifti_image(brain_data, custom_affine)
    
    result = cerebellum_reference_region(cerebellum_img, brain_img)
    
    # Affine should be preserved
    assert np.array_equal(result.affine, custom_affine)


def test_cerebellum_reference_region_empty_input():
    """Test with empty input data."""
    cerebellum_data = np.zeros((5, 5, 5))
    brain_data = np.zeros((5, 5, 5))
    
    cerebellum_img = create_test_nifti_image(cerebellum_data)
    brain_img = create_test_nifti_image(brain_data)
    
    result = cerebellum_reference_region(cerebellum_img, brain_img)
    result_data = result.get_fdata()
    
    # Should be all zeros
    assert result_data.sum() == 0