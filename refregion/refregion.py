import numpy as np
from refregion import morphology


def custom_ref_region(
    mask: np.array,
    refregion_indices: list,
    erode_by_voxels: int,
    exclude_indices: list,
    dilate_by_voxels: int,
    probability_mask: np.array = None,
    probability_threshold: float = None,
) -> np.array:
    """Create a custom reference region.

    First, the reference region is selected by including the indices in refregion_indices. If a probability mask
    and threshold are provided, the probability mask is thresholded and multiplied with the original mask.
    Then, the reference region is eroded by erode_by_voxels. Next, the excluded indices are dilated by
    dilate_by_voxels, and then the overlap is removed from the reference region.

    Args:
        mask (np.array): 3D binary mask
        refregion_indices (list): List of indices to include in the reference region
        erode_by_voxels (int): Number of voxels to erode the reference region by
        exclude_indices (list): List of indices to exclude from the reference region
        dilate_by_voxels (int): Number of voxels to dilate the excluded areas by
        probability_mask (np.array, optional): 3D probability mask (values between 0-1)
        probability_threshold (float, optional): Threshold for probability mask (>= threshold becomes 1, else 0)
    Returns:
        np.array: Custom reference region
    """

    refregion = np.zeros(mask.shape)
    refregion[np.isin(mask, refregion_indices)] = 1

    # Apply probability mask if provided
    if probability_mask is not None and probability_threshold is not None:
        binary_prob_mask = (probability_mask >= probability_threshold).astype(np.uint8)
        refregion = refregion * binary_prob_mask

    refregion = morphology.erode(refregion, erode_by_voxels)

    exclude_mask = np.zeros(mask.shape)
    exclude_mask[np.isin(mask, exclude_indices)] = 1
    exclude_mask = morphology.dilate(exclude_mask, dilate_by_voxels)

    refregion = refregion - exclude_mask
    return morphology._clip(refregion)
