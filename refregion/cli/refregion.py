import argparse
import sys
from pathlib import Path

from refregion import config, wrappers


def _run_from_config(config_path, region_names=None):
    """Load a config file and run all defined reference regions.

    Args:
        config_path: Path to the config file.
        region_names: Optional list of region names to run. If None, run all.
    """
    cfg = config.load_config(config_path)

    if region_names is not None:
        available = [r.name for r in cfg.reference_regions]
        missing = [n for n in region_names if n not in available]
        if missing:
            print(
                f"Error: region(s) not found: {', '.join(missing)}. " f"Available regions: {', '.join(available)}",
                file=sys.stderr,
            )
            sys.exit(1)
        regions = [r for r in cfg.reference_regions if r.name in region_names]
    else:
        regions = cfg.reference_regions

    for region in regions:
        if region.mask_file is None:
            print(f"Error: region '{region.name}' is missing mask_file", file=sys.stderr)
            sys.exit(1)
        if region.output_file is None:
            print(f"Error: region '{region.name}' is missing output_file", file=sys.stderr)
            sys.exit(1)

        prob_mask = Path(region.probability_mask_file) if region.probability_mask_file else None

        result_metrics = wrappers.custom_ref_region(
            mask_file=Path(region.mask_file),
            output_file=Path(region.output_file),
            refregion_indices=region.ref_indices,
            erode_by_voxels=region.erode,
            exclude_indices=region.exclude_indices,
            dilate_by_voxels=region.dilate,
            probability_mask_file=prob_mask,
            probability_threshold=region.probability_threshold,
        )

        print(f"Region: {region.name}")
        print(f"  Voxel count:           {result_metrics['voxel_count']}")
        print(f"  Volume (mm3):          {result_metrics['volume_mm3']:.2f}")
        print(f"  Retention (%):         {result_metrics['retention_percentage']:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Create a custom reference region from a mask")
    parser.add_argument("--config", "-c", type=Path, default=None, help="Path to a YAML/JSON config file")
    parser.add_argument("--mask", "-m", type=Path, default=None, help="Path to the mask file")
    parser.add_argument(
        "--ref_indices",
        "-r",
        type=int,
        nargs="+",
        default=None,
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
        default=None,
        help="Path to the output reference region file",
    )
    parser.add_argument(
        "--region",
        nargs="+",
        default=None,
        help="Region name(s) to run from config file (requires --config)",
    )
    args = parser.parse_args()

    # --region requires --config
    if args.region is not None and args.config is None:
        parser.error("--region requires --config")

    # Mutual exclusivity: --config vs --mask/--ref_indices/--output
    if args.config is not None:
        if args.mask is not None or args.ref_indices is not None or args.output is not None:
            parser.error("--config cannot be used together with --mask, --ref_indices, or --output")
        _run_from_config(args.config, region_names=args.region)
        return

    # Without --config, require --mask, --ref_indices, --output
    if args.mask is None:
        parser.error("--mask is required when not using --config")
    if args.ref_indices is None:
        parser.error("--ref_indices is required when not using --config")
    if args.output is None:
        parser.error("--output is required when not using --config")

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
