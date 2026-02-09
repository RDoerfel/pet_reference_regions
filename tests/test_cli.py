import subprocess
import tempfile
from pathlib import Path

import nibabel as nib
import numpy as np


def test_refregion_cli_prints_morphometrics():
    """Smoke test: refregion CLI prints morphometrics to stdout."""
    with tempfile.TemporaryDirectory() as temp_dir:
        mask_file = Path(temp_dir) / "mask.nii"
        output_file = Path(temp_dir) / "output.nii"

        mask_data = np.array([[[1, 2], [1, 2]], [[1, 2], [1, 2]]], dtype=np.float32)
        nib.save(nib.Nifti1Image(mask_data, np.eye(4)), mask_file)

        result = subprocess.run(
            [
                "poetry",
                "run",
                "refregion",
                "--mask",
                str(mask_file),
                "--ref_indices",
                "1",
                "2",
                "--erode",
                "0",
                "--dilate",
                "0",
                "--output",
                str(output_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, result.stderr
        assert "Morphometrics:" in result.stdout
        assert "Voxel count:" in result.stdout
        assert "Volume (mm3):" in result.stdout
        assert "Retention (%):" in result.stdout


def test_ref_cerebellum_cli_prints_morphometrics():
    """Smoke test: ref_cerebellum CLI prints morphometrics to stdout."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cerebellum_file = Path(temp_dir) / "cerebellum.nii"
        brain_file = Path(temp_dir) / "brain.nii"
        output_file = Path(temp_dir) / "output.nii"

        cerebellum_data = np.zeros((10, 10, 10), dtype=np.float32)
        brain_data = np.zeros((10, 10, 10), dtype=np.float32)
        cerebellum_data[3:7, 3:7, 3:7] = 601

        nib.save(nib.Nifti1Image(cerebellum_data, np.eye(4)), cerebellum_file)
        nib.save(nib.Nifti1Image(brain_data, np.eye(4)), brain_file)

        result = subprocess.run(
            [
                "poetry",
                "run",
                "ref_cerebellum",
                "--cerebellum",
                str(cerebellum_file),
                "--brain",
                str(brain_file),
                "--output",
                str(output_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, result.stderr
        assert "Morphometrics:" in result.stdout
        assert "Voxel count:" in result.stdout
        assert "Volume (mm3):" in result.stdout
        assert "Retention (%):" in result.stdout
