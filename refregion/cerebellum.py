import numpy as np
import nibabel as nib

from refregion import morphology


# load cerebellum segmentation
def cerebellum_reference_region(cerebellum: nib.Nifti1Image, brain: nib.Nifti1Image) -> nib.Nifti1Image:
    """Create a cerebellum reference region from the cerebellum segmentation. Use the aseg segmentation to increase
    the area of cortex and remove the overlap with the cerebellar mask to avoid spill over. Further, increase the area
    of the vermis and remove the overlap part from the cerebellar mask as well.

    Args:
        cerebellum (nib.Nifti1Image): Cerebellum segmentation image. Should be from CerebNet (FastSurfer) or SUIT.
        brain (nib.Nifti1Image): Brain segmentation image.

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
        600,
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

    # first, dilate the cerebral cortex mask
    cerebral_cortex_dilated = morphology.dilate(cerebral_cortex, 4)

    # second dilate the vermis mask
    vermis_mask_dilated = morphology.dilate(vermis_mask, 4)

    # third erode the cerebellum mask
    cerebellum_no_vermis_mask_eroded = morphology.erode(cerebellum_no_vermis_mask, 1)

    # forth, remove the overlapping part from the eroded cerebellum mask
    cerebellum_no_vermis_mask_limited = cerebellum_no_vermis_mask_eroded - cerebral_cortex_dilated - vermis_mask_dilated
    cerebellum_no_vermis_mask_limited = np.clip(cerebellum_no_vermis_mask_limited, 0, 1)

    # plot remaining cerebellum on cerebellum segmentation
    mask_before = cerebellum_no_vermis_mask
    mask_before[cerebral_cortex == 1] = 2
    mask_before[vermis_mask == 1] = 3

    mask_after = cerebellum_no_vermis_mask_limited
    mask_after[cerebral_cortex == 1] = 2
    mask_after[vermis_mask == 1] = 3

    # create the eroded cerebellum mask
    eroded_cerebellum = cerebellum.get_fdata()
    eroded_cerebellum[cerebellum_no_vermis_mask_limited == 0] = 0

    eroded_cerebellum_img = nib.Nifti1Image(eroded_cerebellum, cerebellum.affine, cerebellum.header)
    return eroded_cerebellum_img
