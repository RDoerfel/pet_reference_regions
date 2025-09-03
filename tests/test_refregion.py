import pytest
import numpy as np
from refregion.refregion import custom_ref_region


def test_custom_ref_region_basic():
    """Test basic custom reference region creation."""
    # Create test data
    mask = np.array([[[1, 2], [3, 4]], [[1, 2], [3, 4]]])

    # Test with basic parameters
    result = custom_ref_region(mask, [1, 2], 0, [], 0)

    # Should include regions 1 and 2, exclude nothing
    expected = np.array([[[1, 1], [0, 0]], [[1, 1], [0, 0]]])
    assert np.array_equal(result, expected)


def test_custom_ref_region_with_erosion():
    """Test custom reference region with erosion."""
    # Create test data with boundaries for erosion to be effective
    mask = np.zeros((7, 7, 7))
    mask[1:6, 1:6, 1:6] = 1  # 5x5x5 inner region labeled as 1

    result = custom_ref_region(mask, [1], 1, [], 0)

    # After erosion by 1 voxel, should have smaller region due to boundary effects
    original_sum = (mask == 1).sum()
    assert result.sum() < original_sum
    assert result.sum() > 0  # But should still have some voxels


def test_custom_ref_region_with_exclusion():
    """Test custom reference region with exclusion."""
    # Create test data with multiple regions
    mask = np.array(
        [[[1, 1, 1], [1, 2, 1], [1, 1, 1]], [[1, 1, 1], [1, 2, 1], [1, 1, 1]], [[1, 1, 1], [1, 2, 1], [1, 1, 1]]]
    )

    # Include region 1, exclude region 2 with dilation
    result = custom_ref_region(mask, [1], 0, [2], 1)

    # Should have region 1 minus dilated region 2
    assert result.sum() < (mask == 1).sum()


def test_custom_ref_region_empty_result():
    """Test case where result is empty."""
    mask = np.ones((3, 3, 3))

    # Include region 2 (doesn't exist), should result in empty
    result = custom_ref_region(mask, [2], 0, [], 0)

    assert result.sum() == 0


def test_custom_ref_region_clipping():
    """Test that result is properly clipped to [0, 1]."""
    mask = np.array([[[1, 2], [1, 2]], [[1, 2], [1, 2]]])

    result = custom_ref_region(mask, [1, 2], 0, [], 0)

    # All values should be 0 or 1
    assert np.all((result == 0) | (result == 1))
    assert result.min() >= 0
    assert result.max() <= 1


def test_custom_ref_region_with_probability_mask():
    """Test custom reference region with probability mask."""
    # Create test data
    mask = np.array([[[1, 2], [1, 2]], [[1, 2], [1, 2]]])
    prob_mask = np.array([[[0.3, 0.7], [0.6, 0.4]], [[0.8, 0.2], [0.9, 0.5]]])

    # Test with probability threshold of 0.5
    result = custom_ref_region(mask, [1, 2], 0, [], 0, prob_mask, 0.5)

    # Should only include regions where probability >= 0.5
    # pos (0,0,1): mask=2, prob=0.7 -> included
    # pos (0,1,0): mask=1, prob=0.6 -> included
    # pos (1,0,0): mask=1, prob=0.8 -> included
    # pos (1,1,1): mask=2, prob=0.5 -> included (0.5 >= 0.5)
    expected = np.array([[[0, 1], [1, 0]], [[1, 0], [1, 1]]])
    assert np.array_equal(result, expected)


def test_custom_ref_region_with_probability_mask_high_threshold():
    """Test custom reference region with high probability threshold."""
    mask = np.array([[[1, 2], [1, 2]], [[1, 2], [1, 2]]])
    prob_mask = np.array([[[0.3, 0.7], [0.6, 0.4]], [[0.8, 0.2], [0.9, 0.5]]])

    # Test with high probability threshold of 0.8
    result = custom_ref_region(mask, [1, 2], 0, [], 0, prob_mask, 0.8)

    # Should only include regions where probability >= 0.8
    # pos (1,0,0): mask=1, prob=0.8 -> included
    # pos (1,1,0): mask=2, prob=0.9 -> included
    expected = np.array([[[0, 0], [0, 0]], [[1, 0], [1, 0]]])
    assert np.array_equal(result, expected)


def test_custom_ref_region_probability_mask_no_threshold():
    """Test that probability mask is ignored without threshold."""
    mask = np.array([[[1, 2], [1, 2]], [[1, 2], [1, 2]]])
    prob_mask = np.array([[[0.3, 0.7], [0.6, 0.4]], [[0.8, 0.2], [0.9, 0.5]]])

    # Test with probability mask but no threshold
    result = custom_ref_region(mask, [1, 2], 0, [], 0, prob_mask, None)

    # Should behave like normal case (no probability masking)
    expected = np.array([[[1, 1], [1, 1]], [[1, 1], [1, 1]]])
    assert np.array_equal(result, expected)


def test_custom_ref_region_no_probability_mask():
    """Test that None probability mask is handled correctly."""
    mask = np.array([[[1, 2], [1, 2]], [[1, 2], [1, 2]]])

    # Test with None probability mask
    result = custom_ref_region(mask, [1, 2], 0, [], 0, None, 0.5)

    # Should behave like normal case (no probability masking)
    expected = np.array([[[1, 1], [1, 1]], [[1, 1], [1, 1]]])
    assert np.array_equal(result, expected)
