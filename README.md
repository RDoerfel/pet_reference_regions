# Reference Regions for PET analysis
This repo is thought to gather functions that can be used to create various gray matter references regions for PET analysis.  

## How to Install 
The functions are written in python and can be used as library. Further, they are provdied as cli tools. So far, only poetry is supported for installation.

```bash
poetry add git+https://github.com/RDoerfel/pet_reference_regions.git
```

## Cerebellum
The cerebellum is a common reference region for PET analysis. The function `ref_cerebellum` creates a cerebellum mask based on the cerebellum subsegmentions provided by SUIT or FastSurfer's CerebNet. Addionally, the cortical segmentation from the aseg atlas (Free/FastSurfer) is used to exclude parts of the Cerebellum that are close to the Cortex to avoid spill over. Finally, all vermis regions are excluded from the cerebellum mask. 

More specifically, the following steps are performed:
1. erosion of the cerebellum mask with 1 voxel
2. dialation of the cortical mask with 4 voxels
3. dialation of all vermis regions with 4 voxels
4. exclusion of the dialated vermis regions cortical regions from the cerebellum mask

```bash
ref_cerebellum -c <path/to/cerebellum_seg> -b <path/to/aseg_seg> -o <output_path>
```

You might need to resample the cereballum segmantion to the same dimensions as the aseg segmentation. You can use the following command for that:

```bash
mri_vol2vol --mov <path/to/cerebellum_seg> --targ <path/to/aseg_seg> --regheader --o <path/to/resampled_cerebellum_seg> --interp nearest
ref_cerebellum -c <path/to/resampled_cerebellum_seg> -b <path/to/aseg_seg> -o <path/to/refregion>
```
