import pytest
import numpy as np
import nibabel as nib
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from refregion.wrappers import custom_ref_region


def test_custom_ref_region_wrapper_basic():
    """Test basic wrapper functionality without probability mask."""
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        mask_file = Path(temp_dir) / "mask.nii"
        output_file = Path(temp_dir) / "output.nii"

        # Create test mask data
        mask_data = np.array([[[1, 2], [1, 2]], [[1, 2], [1, 2]]], dtype=np.float32)
        affine = np.eye(4)

        # Save test mask
        nib.save(nib.Nifti1Image(mask_data, affine), mask_file)

        # Run wrapper function
        custom_ref_region(
            mask_file=mask_file,
            output_file=output_file,
            refregion_indices=[1, 2],
            erode_by_voxels=0,
            exclude_indices=[],
            dilate_by_voxels=0,
        )

        # Check output file exists and has correct data
        assert output_file.exists()
        result_img = nib.load(output_file)
        result_data = result_img.get_fdata()

        # Should include all regions 1 and 2
        expected = np.array([[[1, 1], [1, 1]], [[1, 1], [1, 1]]])
        assert np.array_equal(result_data, expected)


def test_custom_ref_region_wrapper_with_probability_mask():
    """Test wrapper functionality with probability mask."""
    with tempfile.TemporaryDirectory() as temp_dir:
        mask_file = Path(temp_dir) / "mask.nii"
        prob_mask_file = Path(temp_dir) / "prob_mask.nii"
        output_file = Path(temp_dir) / "output.nii"

        # Create test data
        mask_data = np.array([[[1, 2], [1, 2]], [[1, 2], [1, 2]]], dtype=np.float32)
        prob_data = np.array([[[0.3, 0.7], [0.6, 0.4]], [[0.8, 0.2], [0.9, 0.5]]], dtype=np.float32)
        affine = np.eye(4)

        # Save test files
        nib.save(nib.Nifti1Image(mask_data, affine), mask_file)
        nib.save(nib.Nifti1Image(prob_data, affine), prob_mask_file)

        # Run wrapper function with probability mask
        custom_ref_region(
            mask_file=mask_file,
            output_file=output_file,
            refregion_indices=[1, 2],
            erode_by_voxels=0,
            exclude_indices=[],
            dilate_by_voxels=0,
            probability_mask_file=prob_mask_file,
            probability_threshold=0.5,
        )

        # Check output
        assert output_file.exists()
        result_img = nib.load(output_file)
        result_data = result_img.get_fdata()

        # Should only include regions where probability >= 0.5
        expected = np.array([[[0, 1], [1, 0]], [[1, 0], [1, 1]]])
        assert np.array_equal(result_data, expected)


def test_custom_ref_region_wrapper_probability_mask_none():
    """Test wrapper functionality with None probability mask."""
    with tempfile.TemporaryDirectory() as temp_dir:
        mask_file = Path(temp_dir) / "mask.nii"
        output_file = Path(temp_dir) / "output.nii"

        # Create test mask data
        mask_data = np.array([[[1, 2], [1, 2]], [[1, 2], [1, 2]]], dtype=np.float32)
        affine = np.eye(4)

        # Save test mask
        nib.save(nib.Nifti1Image(mask_data, affine), mask_file)

        # Run wrapper function with None probability mask
        custom_ref_region(
            mask_file=mask_file,
            output_file=output_file,
            refregion_indices=[1, 2],
            erode_by_voxels=0,
            exclude_indices=[],
            dilate_by_voxels=0,
            probability_mask_file=None,
            probability_threshold=0.5,
        )

        # Check output - should behave like normal case
        assert output_file.exists()
        result_img = nib.load(output_file)
        result_data = result_img.get_fdata()

        expected = np.array([[[1, 1], [1, 1]], [[1, 1], [1, 1]]])
        assert np.array_equal(result_data, expected)


def test_custom_ref_region_wrapper_output_dtype():
    """Test that wrapper saves output as uint8."""
    with tempfile.TemporaryDirectory() as temp_dir:
        mask_file = Path(temp_dir) / "mask.nii"
        output_file = Path(temp_dir) / "output.nii"

        # Create test mask data
        mask_data = np.array([[[1, 2], [1, 2]], [[1, 2], [1, 2]]], dtype=np.float32)
        affine = np.eye(4)

        # Save test mask
        nib.save(nib.Nifti1Image(mask_data, affine), mask_file)

        # Run wrapper function
        custom_ref_region(
            mask_file=mask_file,
            output_file=output_file,
            refregion_indices=[1, 2],
            erode_by_voxels=0,
            exclude_indices=[],
            dilate_by_voxels=0,
        )

        # Check output dtype
        result_img = nib.load(output_file)
        assert result_img.get_data_dtype() == np.uint8
