import numpy as np


def voxel_count(mask: np.ndarray) -> int:
    """Count non-zero voxels in a mask."""
    return int(np.count_nonzero(mask))


def volume_mm3(mask: np.ndarray, voxel_dims: tuple) -> float:
    """Compute volume in mm3 from non-zero voxel count and voxel dimensions."""
    return float(voxel_count(mask) * np.prod(voxel_dims))


def retention_percentage(original_mask: np.ndarray, processed_mask: np.ndarray) -> float:
    """Compute percentage of original voxels retained in processed mask."""
    original_count = voxel_count(original_mask)
    if original_count == 0:
        return 0.0
    return float(voxel_count(processed_mask) / original_count * 100)
