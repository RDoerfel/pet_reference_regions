from skimage import morphology
import numpy as np


def _clip(mask: np.ndarray, between: tuple = (0, 1)) -> np.ndarray:
    return np.clip(mask, *between)


def dilate(mask: np.ndarray, by_radius: int) -> np.ndarray:
    """Dialate a 3D binary mask by a given radius (using a ball structuring element)
    Args:
        mask (np.ndarray): 3D binary mask
        by_radius (int): Radius to dilate the mask by
    Returns:
        np.ndarray: Dialated mask"""

    dilated_mask = morphology.binary_dilation(mask, morphology.ball(by_radius))
    return _clip(dilated_mask)


def erode(mask: np.ndarray, by_radius: int) -> np.ndarray:
    """Erode a 3D binary mask by a given radius (using a ball structuring element)
    Args:
        mask (np.ndarray): 3D binary mask
        by_radius (int): Radius to erode the mask by
    Returns:
        np.ndarray: Eroded mask"""

    eroded_mask = morphology.binary_erosion(mask, morphology.ball(by_radius))
    return _clip(eroded_mask)


def apply_probability_mask(mask: np.ndarray, probability_map: np.ndarray, probability_threshold: float) -> np.ndarray:
    """Apply a probability mask to a binary mask.
    Args:
        mask (np.ndarray): 3D binary mask
        probability (float): Probability to keep a voxel in the mask
    Returns:
        np.ndarray: Mask after applying the probability mask
    """
    probability_map_mask = probability_map >= probability_threshold
    masked = mask * probability_map_mask
    return _clip(masked)
