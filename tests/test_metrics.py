import numpy as np

from refregion.metrics import voxel_count, volume_mm3, retention_percentage


def test_voxel_count_basic():
    """3D array with known non-zero count."""
    mask = np.zeros((3, 3, 3))
    mask[0, 0, 0] = 1
    mask[1, 1, 1] = 1
    mask[2, 2, 2] = 1
    assert voxel_count(mask) == 3


def test_voxel_count_empty():
    """All-zeros array returns 0."""
    mask = np.zeros((4, 4, 4))
    assert voxel_count(mask) == 0


def test_voxel_count_single_voxel():
    """One non-zero voxel returns 1."""
    mask = np.zeros((5, 5, 5))
    mask[2, 2, 2] = 1
    assert voxel_count(mask) == 1


def test_voxel_count_all_ones():
    """All-ones array returns total element count."""
    mask = np.ones((3, 4, 5))
    assert voxel_count(mask) == 60


def test_volume_mm3_isotropic():
    """1mm isotropic voxels: volume equals voxel count."""
    mask = np.zeros((5, 5, 5))
    mask[0, 0, 0] = 1
    mask[1, 1, 1] = 1
    assert volume_mm3(mask, (1.0, 1.0, 1.0)) == 2.0


def test_volume_mm3_anisotropic():
    """Anisotropic voxels (1, 2, 3): each voxel = 6 mm3."""
    mask = np.zeros((5, 5, 5))
    mask[0, 0, 0] = 1
    mask[1, 1, 1] = 1
    mask[2, 2, 2] = 1
    assert volume_mm3(mask, (1.0, 2.0, 3.0)) == 18.0


def test_volume_mm3_empty():
    """Empty mask returns 0.0 volume."""
    mask = np.zeros((3, 3, 3))
    assert volume_mm3(mask, (2.0, 2.0, 2.0)) == 0.0


def test_retention_percentage_full():
    """Identical masks yield 100% retention."""
    mask = np.zeros((3, 3, 3))
    mask[1, 1, 1] = 1
    mask[0, 0, 0] = 1
    assert retention_percentage(mask, mask) == 100.0


def test_retention_percentage_partial():
    """Half retained yields 50% retention."""
    original = np.zeros((4, 4, 4))
    original[0, 0, 0] = 1
    original[1, 1, 1] = 1
    original[2, 2, 2] = 1
    original[3, 3, 3] = 1

    processed = np.zeros((4, 4, 4))
    processed[0, 0, 0] = 1
    processed[1, 1, 1] = 1

    assert retention_percentage(original, processed) == 50.0


def test_retention_percentage_zero():
    """Empty processed mask yields 0% retention."""
    original = np.zeros((3, 3, 3))
    original[1, 1, 1] = 1

    processed = np.zeros((3, 3, 3))

    assert retention_percentage(original, processed) == 0.0


def test_retention_percentage_empty_original():
    """0/0 edge case returns 0.0."""
    original = np.zeros((3, 3, 3))
    processed = np.zeros((3, 3, 3))
    assert retention_percentage(original, processed) == 0.0
