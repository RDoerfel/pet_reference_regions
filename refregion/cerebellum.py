# %%
from pathlib import Path
import nibabel as nib
from skimage import morphology
import numpy as np

# %%
data_dir = Path("/proc_data1/brainage/ERAP_Project_folder/BIDS")
fastsurfer_dir = data_dir / "derivatives/fastsurfer"

subject = "101"
session = "Baseline"

cerebellum_segmentation = fastsurfer_dir / f"sub-{subject}_ses-{session}/mri/cerebellum.CerebNet.nii.gz"
brain_segmentation = fastsurfer_dir / f"sub-{subject}_ses-{session}/mri/aseg.auto.mgz"


# %% load cerebellum segmentation
def cerebellum_reference_region(cerebellum_segmentation_file: Path, aseg_segmentation_file: Path, output_reference_region: Path) -> None:
    """Create a cerebellum reference region from the cerebellum segmentation. Use the aseg segmentation to increase
    the area of cortex and remove the overlap with the cerebellar mask to avoid spill over. Further, increase the area
    of the vermis and remove the overlap part from the cerebellar mask as well.

    When using FastSurfers CerebNet, you might need to resample the cerebellum segmentation to the aseg segmentation.
    You will do so with the following command: 
    mri_vol2vol --mov {cerebellum_segmentation} --targ {brain_segmentation} --regheader --o {cerebellum_segmentation_resampled} --interp nearest

    Args:
        cerebellum_segmentation_file (Path): Path to the cerebellum segmentation file. Should be from CerebNet (FastSurfer) or SUIT.
        aseg_segmentation_file (Path): Path to the brain segmentation file
        output_reference_region (Path): Path to the output reference region file
    """

    cerebellum = nib.load(cerebellum_segmentation_file)
    brain = nib.load(brain_segmentation)

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

    # first, dialate the cerebral cortex mask
    cerebral_cortex_dilated = morphology.binary_dilation(cerebral_cortex, morphology.ball(4))
    cerebral_cortex_dilated = np.clip(cerebral_cortex_dilated, 0, 1)

    # second dialate the vermis mask
    vermis_mask_dilated = morphology.binary_dilation(vermis_mask, morphology.ball(4))
    vermis_mask_dilated = np.clip(vermis_mask_dilated, 0, 1)

    # hird erode the cerebellum mask
    cerebellum_no_vermis_mask_eroded = morphology.binary_erosion(cerebellum_no_vermis_mask, morphology.ball(1))
    cerebellum_no_vermis_mask_eroded = np.clip(cerebellum_no_vermis_mask_eroded, 0, 1)

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

    # save the eroded cerebellum mask
    eroded_cerebellum = cerebellum.get_fdata()
    eroded_cerebellum[cerebellum_no_vermis_mask_limited == 0] = 0

    eroded_cerebellum_img = nib.Nifti1Image(eroded_cerebellum, cerebellum.affine, cerebellum.header)
    nib.save(eroded_cerebellum_img, output_reference_region)
