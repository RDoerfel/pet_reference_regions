import subprocess
import tempfile
from pathlib import Path

import nibabel as nib
import numpy as np
import yaml

from refregion.config import SUPPORTED_CONFIG_VERSION


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


# ---------------------------------------------------------------------------
# --region flag tests
# ---------------------------------------------------------------------------


def _make_mask(path):
    """Helper: write a small NIfTI mask with indices 1 and 2."""
    data = np.array([[[1, 2], [1, 2]], [[1, 2], [1, 2]]], dtype=np.float32)
    nib.save(nib.Nifti1Image(data, np.eye(4)), path)


def test_refregion_cli_config_region_filter():
    """--region selects a single region from a multi-region config."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        mask_path = tmp / "mask.nii"
        out_a = tmp / "out_a.nii"
        out_b = tmp / "out_b.nii"
        config_path = tmp / "config.yaml"

        _make_mask(mask_path)

        config_data = {
            "version": SUPPORTED_CONFIG_VERSION,
            "reference_regions": [
                {
                    "name": "region_a",
                    "ref_indices": [1],
                    "mask_file": str(mask_path),
                    "output_file": str(out_a),
                },
                {
                    "name": "region_b",
                    "ref_indices": [2],
                    "mask_file": str(mask_path),
                    "output_file": str(out_b),
                },
            ],
        }
        config_path.write_text(yaml.dump(config_data))

        result = subprocess.run(
            ["poetry", "run", "refregion", "--config", str(config_path), "--region", "region_a"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert out_a.exists()
        assert not out_b.exists()
        assert "region_a" in result.stdout


def test_refregion_cli_config_region_multiple():
    """--region with two names runs both regions."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        mask_path = tmp / "mask.nii"
        out_a = tmp / "out_a.nii"
        out_b = tmp / "out_b.nii"
        config_path = tmp / "config.yaml"

        _make_mask(mask_path)

        config_data = {
            "version": SUPPORTED_CONFIG_VERSION,
            "reference_regions": [
                {
                    "name": "region_a",
                    "ref_indices": [1],
                    "mask_file": str(mask_path),
                    "output_file": str(out_a),
                },
                {
                    "name": "region_b",
                    "ref_indices": [2],
                    "mask_file": str(mask_path),
                    "output_file": str(out_b),
                },
            ],
        }
        config_path.write_text(yaml.dump(config_data))

        result = subprocess.run(
            [
                "poetry",
                "run",
                "refregion",
                "--config",
                str(config_path),
                "--region",
                "region_a",
                "region_b",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert out_a.exists()
        assert out_b.exists()


def test_refregion_cli_config_region_missing():
    """--region with unknown name errors and lists available names."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        mask_path = tmp / "mask.nii"
        config_path = tmp / "config.yaml"

        _make_mask(mask_path)

        config_data = {
            "version": SUPPORTED_CONFIG_VERSION,
            "reference_regions": [
                {
                    "name": "region_a",
                    "ref_indices": [1],
                    "mask_file": str(mask_path),
                    "output_file": str(tmp / "out.nii"),
                },
            ],
        }
        config_path.write_text(yaml.dump(config_data))

        result = subprocess.run(
            [
                "poetry",
                "run",
                "refregion",
                "--config",
                str(config_path),
                "--region",
                "nonexistent",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "nonexistent" in result.stderr
        assert "region_a" in result.stderr


def test_refregion_cli_region_without_config():
    """--region without --config should produce an error."""
    result = subprocess.run(
        [
            "poetry",
            "run",
            "refregion",
            "--region",
            "something",
            "--mask",
            "/fake.nii",
            "--ref_indices",
            "1",
            "--output",
            "/fake_out.nii",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "region" in result.stderr.lower()
