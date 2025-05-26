import argparse
from pathlib import Path

from refregion import wrappers


def main():
    parser = argparse.ArgumentParser(description="Create a custom reference region from a mask")
    parser.add_argument("--mask", "-m", type=Path, required=True, help="Path to the mask file")
    parser.add_argument(
        "--ref_indices",
        "-r",
        type=int,
        nargs="+",
        required=True,
        help="Indices to include in the reference region (space-separated integers)",
    )
    parser.add_argument(
        "--erode", "-e", type=int, required=False, default=0, help="Number of voxels to erode the reference region by"
    )
    parser.add_argument(
        "--exclude_indices",
        "-x",
        type=int,
        nargs="+",
        required=False,
        default=[],
        help="Indices to exclude from the reference region (space-separated integers)",
    )
    parser.add_argument(
        "--dialate",
        "-d",
        type=int,
        required=False,
        default=0,
        help="Number of voxels to dialate the excluded areas by. The overlap is removed from the reference region",
    )
    parser.add_argument("--output", "-o", type=Path, required=True, help="Path to the output reference region file")
    args = parser.parse_args()

    # load images
    wrappers.custom_ref_region(
        mask_file=args.mask,
        output_file=args.output,
        refregion_indices=args.ref_indices,
        erode_by_voxels=args.erode,
        exclude_indices=args.exclude_indices,
        dialate_by_voxels=args.dialate,
    )
