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
    dilate_by_voxels: int,
    probability_mask_file: Path = None,
    probability_threshold: float = None,
):
    # Input validation
    if not mask_file.exists():
        raise FileNotFoundError(f"Mask file does not exist: {mask_file}")
    if probability_mask_file is not None and not probability_mask_file.exists():
        raise FileNotFoundError(f"Probability mask file does not exist: {probability_mask_file}")
    if erode_by_voxels < 0:
        raise ValueError(f"erode_by_voxels must be >= 0, got {erode_by_voxels}")
    if dilate_by_voxels < 0:
        raise ValueError(f"dilate_by_voxels must be >= 0, got {dilate_by_voxels}")
    if probability_threshold is not None and (probability_threshold < 0 or probability_threshold > 1):
        raise ValueError(f"probability_threshold must be between 0 and 1, got {probability_threshold}")
    
    # load data
    try:
        mask_img = nib.load(mask_file)
        mask = mask_img.get_fdata()
    except Exception as e:
        raise RuntimeError(f"Failed to load mask file {mask_file}: {e}")

    # load probability mask if provided
    probability_mask = None
    if probability_mask_file is not None:
        try:
            probability_mask = nib.load(probability_mask_file).get_fdata()
            if probability_mask.shape != mask.shape:
                raise ValueError(f"Probability mask shape {probability_mask.shape} does not match mask shape {mask.shape}")
        except Exception as e:
            raise RuntimeError(f"Failed to load probability mask file {probability_mask_file}: {e}")

    # create custom reference region
    mask_ref = refregion.custom_ref_region(
        mask,
        refregion_indices,
        erode_by_voxels,
        exclude_indices,
        dilate_by_voxels,
        probability_mask,
        probability_threshold,
    )
    # cast as uint8
    mask_ref = mask_ref.astype(np.uint8)
    # save output
    try:
        # Create output directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)
        nib.save(
            nib.Nifti1Image(mask_ref, mask_img.affine),
            output_file,
            dtype=np.uint8,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to save output file {output_file}: {e}")


def cerebellum_reference_region(
    cerebellum_segmentation_file: Path,
    brain_segmentation: Path,
    output_reference_region: Path,
):
    # Input validation
    if not cerebellum_segmentation_file.exists():
        raise FileNotFoundError(f"Cerebellum segmentation file does not exist: {cerebellum_segmentation_file}")
    if not brain_segmentation.exists():
        raise FileNotFoundError(f"Brain segmentation file does not exist: {brain_segmentation}")
    
    # load data
    try:
        cerebellum_img = nib.load(cerebellum_segmentation_file)
        cerebellum_data = cerebellum_img.get_fdata()
        brain_data = nib.load(brain_segmentation).get_fdata()
        
        if cerebellum_data.shape != brain_data.shape:
            raise ValueError(f"Cerebellum shape {cerebellum_data.shape} does not match brain shape {brain_data.shape}")
    except Exception as e:
        raise RuntimeError(f"Failed to load segmentation files: {e}")
    # create cerebellum reference region
    cerebellum_refregion = cerebellum.cerebellum_reference_region(cerebellum_data, brain_data)
    # save output
    try:
        # Create output directory if it doesn't exist
        output_reference_region.parent.mkdir(parents=True, exist_ok=True)
        nib.save(
            nib.Nifti1Image(cerebellum_refregion, cerebellum_img.affine),
            output_reference_region,
            dtype=np.uint8,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to save output file {output_reference_region}: {e}")
