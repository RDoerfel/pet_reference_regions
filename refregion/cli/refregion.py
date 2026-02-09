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
        "--erode",
        "-e",
        type=int,
        required=False,
        default=0,
        help="Number of voxels to erode the reference region by",
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
        "--dilate",
        "-d",
        type=int,
        required=False,
        default=0,
        help="Number of voxels to dilate the excluded areas by. The overlap is removed from the reference region",
    )
    parser.add_argument(
        "--probability_mask",
        "-p",
        type=Path,
        required=False,
        help="Path to probability mask file (optional, for WM or GM probability)",
    )
    parser.add_argument(
        "--probability_threshold",
        "-t",
        type=float,
        required=False,
        help="Threshold for probability mask (values >= threshold become 1, else 0)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
        help="Path to the output reference region file",
    )
    args = parser.parse_args()

    # Validate probability mask arguments
    if (args.probability_mask is not None) != (args.probability_threshold is not None):
        parser.error("--probability_mask and --probability_threshold must be used together")

    # create reference region
    result_metrics = wrappers.custom_ref_region(
        mask_file=args.mask,
        output_file=args.output,
        refregion_indices=args.ref_indices,
        erode_by_voxels=args.erode,
        exclude_indices=args.exclude_indices,
        dilate_by_voxels=args.dilate,
        probability_mask_file=args.probability_mask,
        probability_threshold=args.probability_threshold,
    )

    print("Morphometrics:")
    print(f"  Voxel count:           {result_metrics['voxel_count']}")
    print(f"  Volume (mm3):          {result_metrics['volume_mm3']:.2f}")
    print(f"  Retention (%):         {result_metrics['retention_percentage']:.2f}")
