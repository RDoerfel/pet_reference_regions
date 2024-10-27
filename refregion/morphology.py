from skimage import morphology
import numpy as np


def _clip(mask: np.ndarray, between: tuple = (0, 1)) -> np.ndarray:
    return np.clip(mask, *between)


def dialate(mask: np.ndarray, by_radius: int) -> np.ndarray:
    """Dialate a 3D binary mask by a given radius (using a ball structuring element)
    Args:
        mask (np.ndarray): 3D binary mask
        by_radius (int): Radius to dialate the mask by
    Returns:
        np.ndarray: Dialated mask"""

    dialated_mask = morphology.binary_dilation(mask, morphology.ball(by_radius))
    return _clip(dialated_mask)


def erode(mask: np.ndarray, by_radius: int) -> np.ndarray:
    """Erode a 3D binary mask by a given radius (using a ball structuring element)
    Args:
        mask (np.ndarray): 3D binary mask
        by_radius (int): Radius to erode the mask by
    Returns:
        np.ndarray: Eroded mask"""

    eroded_mask = morphology.binary_erosion(mask, morphology.ball(by_radius))
    return _clip(eroded_mask)
