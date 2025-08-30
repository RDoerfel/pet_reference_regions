# Reference Regions for PET Analysis
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15496253.svg)](https://doi.org/10.5281/zenodo.15496253)
[![CI](https://github.com/RDoerfel/pet_reference_regions/actions/workflows/CI.yml/badge.svg)](https://github.com/RDoerfel/pet_reference_regions/actions/workflows/CI.yml)
[![codecov](https://codecov.io/gh/RDoerfel/pet_reference_regions/branch/main/graph/badge.svg)](https://codecov.io/gh/RDoerfel/pet_reference_regions)

This repository provides functions and command-line tools for creating various gray matter reference regions for positron emission tomography (PET) analysis. Reference regions are anatomical areas with minimal specific binding that serve as controls for quantifying tracer uptake in regions of interest.

## Overview

PET quantification often requires reference regions to normalize tracer uptake and account for non-specific binding. This toolkit provides automated methods to generate robust reference regions from anatomical segmentations, with options for morphological operations to ensure spatial specificity and avoid contamination from adjacent structures.

## How to Install

The functions are written in Python and can be used as a library or through command-line interface (CLI) tools. Currently, only Poetry is supported for installation. Pip probably works as well.

```bash
poetry add git+https://github.com/RDoerfel/pet_reference_regions.git
```

## Usage

### RefRegion

This is a general-purpose CLI to create custom reference regions from anatomical masks. It allows you to select specific anatomical indices and apply morphological operations to exclude overlapping parts with adjacent regions. To be more conservative, adjacent regions can be dilated and the overlapping parts will be removed from the reference region.

**Required Arguments:**

- `--mask`, `-m`: Path to the input mask file
- `--ref_indices`, `-r`: Indices to include in the reference region (space-separated integers)
- `--output`, `-o`: Path to the output reference region file

**Optional Arguments:**

- `--erode`, `-e`: Number of voxels to erode the selected reference region areas by (default: 0)
- `--exclude_indices`, `-x`: Indices to exclude from the reference region (space-separated integers, default: none)
- `--dilate`, `-d`: Number of voxels to dilate the excluded areas by (default: 0)
- `--probability_mask`, `-p`: Path to probability mask file (optional, for WM or GM probability)
- `--probability_threshold`, `-t`: Threshold for probability mask (values >= threshold become 1, else 0)

**Processing Pipeline:**

The tool applies the following operations in sequence:

1. Load mask file and extract specified reference indices
2. Create initial reference region from specified indices
3. Apply probability mask (optional): If a probability mask and threshold are provided, threshold the probability mask and multiply with the reference region
4. Erosion (optional): Erode the selected reference region areas by the specified number of voxels
5. Exclude indices (optional): Identify areas to exclude from the reference region
6. Dilation (optional): Dilate the excluded areas by the specified number of voxels
7. Final processing: Remove any overlap between dilated excluded areas and the reference region

#### Examples:

Basic usage (reference region creation only):
```bash
refregion \
    --mask brain_mask.nii.gz \
    --ref_indices 1 2 3 5 8 \
    --output custom_reference_region.nii.gz
```

With exclusions and dilation:
```bash
refregion \
    --mask brain_mask.nii.gz \
    --ref_indices 1 2 3 5 8 \
    --erode 1 \
    --exclude_indices 10 11 12 \
    --dilate 3 \
    --output custom_reference_region.nii.gz
```

With probability mask (e.g., for gray matter probability):
```bash
refregion \
    --mask brain_mask.nii.gz \
    --ref_indices 1 2 3 5 8 \
    --probability_mask gm_probability.nii.gz \
    --probability_threshold 0.7 \
    --erode 1 \
    --output custom_reference_region.nii.gz
```

### Ref_Cerebellum

The cerebellum is a commonly used reference region for PET analysis due to its relatively low density of many neurotransmitter receptors and transporters. The `ref_cerebellum` function creates a cerebellar mask based on cerebellar subsegmentations provided by SUIT or FastSurfer's CerebNet. Additionally, cortical segmentation from the aseg atlas (FreeSurfer/FastSurfer) is used to exclude parts of the cerebellum that are close to the cortex to avoid spillover contamination. Finally, all vermis regions are excluded from the cerebellar mask to ensure lateral cerebellar specificity.

**Required Arguments:**

- `--cerebellum`, `-c`: Path to the cerebellum segmentation file
- `--brain`, `-b`: Path to the aseg segmentation file  
- `--output`, `-o`: Path to the output cerebellar reference region file

**Processing Pipeline:**

The tool applies the following operations in sequence:

1. Erosion of the cerebellum mask by 1 voxel
2. Dilation of the cortical mask by 4 voxels
3. Dilation of all vermis regions by 4 voxels
4. Exclusion of the dilated vermis and cortical regions from the cerebellum mask

#### Example:

```bash
ref_cerebellum -c <path/to/cerebellum_seg> -b <path/to/aseg_seg> -o <output_path>
```

## Notes

### Resampling
You might need to resample the cerebellar segmentation to the same dimensions as the aseg segmentation. You can use the following command for that:

```bash
mri_vol2vol --mov <path/to/cerebellum_seg> --targ <path/to/aseg_seg> --regheader --o <path/to/resampled_cerebellum_seg> --interp nearest
ref_cerebellum -c <path/to/resampled_cerebellum_seg> -b <path/to/aseg_seg> -o <path/to/refregion>
```

### File Formats

- Input and output files are typically in NIfTI format (`.nii`, `.nii.gz`)
- Segmentation files should contain integer labels corresponding to anatomical regions
- All operations preserve the original image geometry and voxel spacing