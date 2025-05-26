from pathlib import Path
import nibabel as nib
from refregion import refregion
import numpy as np


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
    mask_ref = refregion.custom_ref_region(
        mask, refregion_indices, erode_by_voxels, exclude_indices, dialate_by_voxels
    )
    # cast as uint8
    mask_ref = mask_ref.astype(np.uint8)
    # save output
    nib.save(
        nib.Nifti1Image(mask_ref, nib.load(mask_file).affine),
        output_file,
        dtype=np.uint8,
    )


def cerebellum_reference_region(
    cerebellum_segmentation_file: Path,
    brain_segmentation: Path,
    output_reference_region: Path,
):
    # load data
    cerebellum = nib.load(cerebellum_segmentation_file).get_fdata()
    brain = nib.load(brain_segmentation).get_fdata()
    # create cerebellum reference region
    cerebellum_ref = refregion.cerebellum_reference_region(cerebellum, brain)
    # save output
    nib.save(
        nib.Nifti1Image(cerebellum_ref, nib.load(cerebellum_segmentation_file).affine),
        output_reference_region,
        dtype=np.uint8,
    )
