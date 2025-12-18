import numpy as np
from refregion.morphology import dilate, erode, apply_probability_mask


def test_dilate():
    # Create a simple binary 3D mask
    mask = np.array(
        [
            [
                [0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
            ],
            [
                [0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
            ],
            [
                [0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
            ],
        ]
    )

    # Expected result after dilation with size 1
    expected_result = np.array(
        [
            [
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
            ],
            [
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
            ],
            [
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
            ],
        ]
    )

    # Perform dilation
    result = dilate(mask, 1)

    # Assert the result is as expected
    assert np.array_equal(result, expected_result), "Dialate function failed"


def test_erode():
    # Create a simple binary mask
    mask = np.array(
        [
            [
                [0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
            ],
            [
                [0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
            ],
            [
                [0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
            ],
        ]
    )

    # Expected result after erosion with size 1
    expected_result = np.array(
        [
            [
                [0, 0, 1, 0, 0],
                [0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
                [0, 0, 1, 0, 0],
            ],
            [
                [0, 0, 1, 0, 0],
                [0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
                [0, 0, 1, 0, 0],
            ],
            [
                [0, 0, 1, 0, 0],
                [0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
                [0, 0, 1, 0, 0],
            ],
        ]
    )

    # Perform erosion
    result = erode(mask, 1)

    # Assert the result is as expected
    assert np.array_equal(result, expected_result), "Erode function failed"


def test_apply_probability_mask():
    # Create a simple binary 3D mask
    mask = np.array(
        [
            [
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
            ],
            [
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
            ],
            [
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
            ],
        ]
    )

    # Create a probability map with varying values
    probability_map = np.array(
        [
            [
                [0.1, 0.2, 0.3, 0.4, 0.5],
                [0.2, 0.4, 0.6, 0.8, 1.0],
                [0.3, 0.5, 0.7, 0.9, 0.9],
                [0.4, 0.6, 0.8, 0.7, 0.8],
                [0.5, 0.7, 0.9, 0.6, 0.7],
            ],
            [
                [0.2, 0.3, 0.4, 0.5, 0.6],
                [0.3, 0.5, 0.7, 0.9, 0.8],
                [0.4, 0.6, 0.8, 1.0, 0.9],
                [0.5, 0.7, 0.9, 0.8, 0.7],
                [0.6, 0.8, 1.0, 0.7, 0.6],
            ],
            [
                [0.3, 0.4, 0.5, 0.6, 0.7],
                [0.4, 0.6, 0.8, 1.0, 0.9],
                [0.5, 0.7, 0.9, 0.8, 0.7],
                [0.6, 0.8, 1.0, 0.7, 0.6],
                [0.7, 0.9, 0.8, 0.6, 0.5],
            ],
        ]
    )

    # Apply probability mask with threshold 0.7
    result = apply_probability_mask(mask, probability_map, 0.7)

    # Expected result: only voxels where probability >= 0.7 remain
    expected_result = np.array(
        [
            [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1],
                [0, 0, 1, 1, 1],
                [0, 0, 1, 1, 1],
                [0, 1, 1, 0, 1],
            ],
            [
                [0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1],
                [0, 0, 1, 1, 1],
                [0, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
            ],
            [
                [0, 0, 0, 0, 1],
                [0, 0, 1, 1, 1],
                [0, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
                [1, 1, 1, 0, 0],
            ],
        ]
    )

    # Assert the result is as expected
    assert np.array_equal(result, expected_result), "apply_probability_mask function failed"

    # Test with threshold 0.5 (more voxels should remain)
    result_low_threshold = apply_probability_mask(mask, probability_map, 0.5)
    assert result_low_threshold.sum() > result.sum(), "Lower threshold should preserve more voxels"

    # Test with threshold 1.0 (only voxels with probability exactly 1.0 remain)
    result_high_threshold = apply_probability_mask(mask, probability_map, 1.0)
    expected_high_threshold = (probability_map >= 1.0).astype(int)
    assert np.array_equal(result_high_threshold, expected_high_threshold), "Threshold 1.0 test failed"

    # Test that result is clipped to [0, 1]
    assert result.max() <= 1, "Result should be clipped to max value 1"
    assert result.min() >= 0, "Result should be clipped to min value 0"
