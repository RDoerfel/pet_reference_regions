import numpy as np
import nibabel as nib

from refregion import morphology


# load cerebellum segmentation
def cerebellum_reference_region(
    cerebellum: nib.Nifti1Image,
    brain: nib.Nifti1Image,
    erode_cerebellum_by_voxels: int = 1,
    dialate_vermis_by_voxels: int = 4,
    dialate_cortex_by_voxels: int = 4,
) -> nib.Nifti1Image:
    """Create a cerebellum reference region from the cerebellum segmentation. Use the aseg segmentation to increase
    the area of cortex and remove the overlap with the cerebellar mask to avoid spill over. Further, increase the area
    of the vermis and remove the overlap part from the cerebellar mask as well.

    Args:
        cerebellum (nib.Nifti1Image): Cerebellum segmentation image. Should be from CerebNet (FastSurfer) or SUIT.
        brain (nib.Nifti1Image): Brain segmentation image.
        erode_cerebellum_by_voxels (int, optional): Number of voxels to erode the cerebellum mask. Defaults to 1.
        dialate_vermis_by_voxels (int, optional): Number of voxels to dialate the vermis mask. Defaults to 4.
        dialate_cortex_by_voxels (int, optional): Number of voxels to dialate the cortex mask. Defaults to 4.

    Returns:
        nib.Nifti1Image: The resulting cerebellum reference region image.
    """

    # labels: 3, 42 Cerebral Cortex
    # labels > 600 are cortex of the cerebellum

    # take a mask from cerebral cortex in brain segmentation
    cerebral_cortex = np.zeros(brain.shape)
    cerebral_cortex[np.isin(brain.get_fdata(), [3, 42])] = 1

    # take a mask from cerebellum in cerebellum segmentation (labels > 600)
    cerebellum_no_vermis_ids = [
        601,
        602,
        603,
        604,
        605,
        607,
        608,
        610,
        611,
        613,
        614,
        616,
        617,
        619,
        620,
        622,
        623,
        625,
        626,
        628,
    ]
    cerebellum_no_vermis_mask = np.zeros(cerebellum.shape)
    cerebellum_no_vermis_mask[np.isin(cerebellum.get_fdata(), cerebellum_no_vermis_ids)] = 1

    # get mask for Vermis
    vermis_ids = [606, 609, 612, 615, 618, 621, 624, 627]
    vermis_mask = np.zeros(cerebellum.shape)
    vermis_mask[np.isin(cerebellum.get_fdata(), vermis_ids)] = 1

    # first, dialate the cerebral cortex mask
    cerebral_cortex_dialated = morphology.dialate(cerebral_cortex, dialate_cortex_by_voxels)

    # second dialate the vermis mask
    vermis_mask_dialated = morphology.dialate(vermis_mask, dialate_vermis_by_voxels)

    # third erode the cerebellum mask
    cerebellum_no_vermis_mask_eroded = morphology.erode(cerebellum_no_vermis_mask, erode_cerebellum_by_voxels)

    # forth, remove the overlapping part from the eroded cerebellum mask
    cerebellum_no_vermis_mask_limited = cerebellum_no_vermis_mask_eroded - vermis_mask_dialated
    cerebellum_no_vermis_mask_limited = cerebellum_no_vermis_mask_limited - cerebral_cortex_dialated

    cerebellum_no_vermis_mask_limited = np.clip(cerebellum_no_vermis_mask_limited, 0, 1)

    eroded_cerebellum_img = nib.Nifti1Image(cerebellum_no_vermis_mask_limited, cerebellum.affine, cerebellum.header)
    return eroded_cerebellum_img
