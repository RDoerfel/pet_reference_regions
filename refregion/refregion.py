import numpy as np
from refregion import morphology


def custom_ref_region(
    mask: np.array, refregion_indices: list, erode_by_voxels: int, exclude_indices: list, dialate_by_voxels: int
) -> np.array:
    """Create a custom reference region.

    First, the reference region is selected by including the indices in refregion_indices. Then, the reference region
    is eroded by erode_by_voxels. Next, the excluded indices are dialated by dialate_by_voxels, and than the overlap
    is removed from the reference region.

    Args:
        mask (np.array): 3D binary mask
        refregion_indices (list): List of indices to include in the reference region
        erode_by_voxels (int): Number of voxels to erode the reference region by
        exclude_indices (list): List of indices to exclude from the reference region
        dialate_by_voxels (int): Number of voxels to dialate the excluded areas by
    Returns:
        np.array: Custom reference region
    """

    refregion = np.zeros(mask.shape)
    refregion[np.isin(mask, refregion_indices)] = 1

    refregion = morphology.erode(refregion, erode_by_voxels)

    exclude_mask = np.zeros(mask.shape)
    exclude_mask[np.isin(mask, exclude_indices)] = 1
    exclude_mask = morphology.dialate(exclude_mask, dialate_by_voxels)

    refregion = refregion - exclude_mask
    return morphology._clip(refregion)
