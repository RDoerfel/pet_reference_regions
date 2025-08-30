from pathlib import Path
import nibabel as nib
from refregion import cerebellum
from refregion import refregion

import numpy as np


def custom_ref_region(
    mask_file: Path,
    output_file: Path,
    refregion_indices: list,
    erode_by_voxels: int,
    exclude_indices: list,
    dialate_by_voxels: int,
    probability_mask_file: Path = None,
    probability_threshold: float = None,
):
    # load data
    mask = nib.load(mask_file).get_fdata()
    
    # load probability mask if provided
    probability_mask = None
    if probability_mask_file is not None:
        probability_mask = nib.load(probability_mask_file).get_fdata()
    
    # create custom reference region
    mask_ref = refregion.custom_ref_region(
        mask, refregion_indices, erode_by_voxels, exclude_indices, dialate_by_voxels,
        probability_mask, probability_threshold
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
    cerebellum_data = nib.load(cerebellum_segmentation_file).get_fdata()
    brain_data = nib.load(brain_segmentation).get_fdata()
    # create cerebellum reference region
    cerebellum_refregion = cerebellum.cerebellum_reference_region(cerebellum_data, brain_data)
    # save output
    nib.save(
        nib.Nifti1Image(cerebellum_refregion, nib.load(cerebellum_segmentation_file).affine),
        output_reference_region,
        dtype=np.uint8,
    )
