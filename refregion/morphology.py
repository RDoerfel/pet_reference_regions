from skimage import morphology
import numpy as np


def _clip(mask: np.ndarray, between: tuple = (0, 1)) -> np.ndarray:
    return np.clip(mask, *between)


def dialate(mask: np.ndarray, by_radius: int) -> np.ndarray:
    dialated_mask = morphology.binary_dilation(mask, morphology.ball(by_radius))
    return _clip(dialated_mask)


def erode(mask: np.ndarray, by_radius: int) -> np.ndarray:
    eroded_mask = morphology.binary_erosion(mask, morphology.ball(by_radius))
    return _clip(eroded_mask)
