import argparse
from pathlib import Path

from refregion.wrappers import cerebellum_reference_region


def main():
    parser = argparse.ArgumentParser(description="Create a cerebellum reference region")
    parser.add_argument(
        "--cerebellum",
        "-c",
        type=Path,
        required=True,
        help="Path to the cerebellum segmentation file",
    )
    parser.add_argument(
        "--brain",
        "-b",
        type=Path,
        required=True,
        help="Path to the brain segmentation file",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
        help="Path to the output reference region file",
    )
    args = parser.parse_args()

    cerebellum_reference_region(
        args.cerebellum,
        args.brain,
        args.output,
    )


if __name__ == "__main__":
    main()
