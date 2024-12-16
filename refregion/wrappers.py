from pathlib import Path
import nibabel as nib
from refregion import refregion


def custom_ref_region(
    mask_file: Path,
    output_file: Path,
    refregion_indices: list,
    erode_by_voxels: int,
    exclude_indices: list,
    dialate_by_voxels: int,
):
    # load data
    mask = nib.load(mask_file).get_fdata()
    # create custom reference region
    mask_ref = refregion.custom_ref_region(mask, refregion_indices, erode_by_voxels, exclude_indices, dialate_by_voxels)
    # save output
    nib.save(nib.Nifti1Image(mask_ref, nib.load(mask_file).affine), output_file)
