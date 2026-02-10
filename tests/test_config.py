import json
import subprocess
import tempfile
from pathlib import Path

import nibabel as nib
import numpy as np
import pytest
import yaml

from refregion.config import (
    SUPPORTED_CONFIG_VERSION,
    ConfigFile,
    ReferenceRegionConfig,
    config_from_dict,
    config_to_dict,
    load_config,
    save_config,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def minimal_region_dict():
    return {"name": "cerebellum", "ref_indices": [1, 2, 3]}


@pytest.fixture
def full_region_dict():
    return {
        "name": "cerebellum",
        "ref_indices": [601, 602, 603],
        "erode": 2,
        "exclude_indices": [10, 11],
        "dilate": 3,
        "probability_mask_file": "/data/prob.nii.gz",
        "probability_threshold": 0.5,
        "mask_file": "/data/mask.nii.gz",
        "output_file": "/data/output.nii.gz",
    }


@pytest.fixture
def minimal_config_dict(minimal_region_dict):
    return {
        "version": SUPPORTED_CONFIG_VERSION,
        "reference_regions": [minimal_region_dict],
    }


@pytest.fixture
def full_config_dict(full_region_dict):
    return {
        "version": SUPPORTED_CONFIG_VERSION,
        "segmentation_type": "freesurfer",
        "reference_regions": [full_region_dict],
    }


# ---------------------------------------------------------------------------
# ReferenceRegionConfig model validation
# ---------------------------------------------------------------------------


def test_reference_region_minimal(minimal_region_dict):
    """Minimal valid region: only name + ref_indices."""
    region = ReferenceRegionConfig(**minimal_region_dict)
    assert region.name == "cerebellum"
    assert region.ref_indices == [1, 2, 3]
    assert region.erode == 0
    assert region.exclude_indices == []
    assert region.dilate == 0
    assert region.probability_mask_file is None
    assert region.probability_threshold is None
    assert region.mask_file is None
    assert region.output_file is None


def test_reference_region_full(full_region_dict):
    """All fields populated."""
    region = ReferenceRegionConfig(**full_region_dict)
    assert region.name == "cerebellum"
    assert region.ref_indices == [601, 602, 603]
    assert region.erode == 2
    assert region.exclude_indices == [10, 11]
    assert region.dilate == 3
    assert region.probability_mask_file == "/data/prob.nii.gz"
    assert region.probability_threshold == 0.5
    assert region.mask_file == "/data/mask.nii.gz"
    assert region.output_file == "/data/output.nii.gz"


def test_reference_region_empty_ref_indices():
    """ref_indices must be non-empty."""
    with pytest.raises(Exception):
        ReferenceRegionConfig(name="bad", ref_indices=[])


def test_reference_region_negative_erode():
    """erode must be >= 0."""
    with pytest.raises(Exception):
        ReferenceRegionConfig(name="bad", ref_indices=[1], erode=-1)


def test_reference_region_negative_dilate():
    """dilate must be >= 0."""
    with pytest.raises(Exception):
        ReferenceRegionConfig(name="bad", ref_indices=[1], dilate=-1)


def test_reference_region_threshold_below_zero():
    """probability_threshold must be >= 0.0."""
    with pytest.raises(Exception):
        ReferenceRegionConfig(name="bad", ref_indices=[1], probability_threshold=-0.1)


def test_reference_region_threshold_above_one():
    """probability_threshold must be <= 1.0."""
    with pytest.raises(Exception):
        ReferenceRegionConfig(name="bad", ref_indices=[1], probability_threshold=1.5)


# ---------------------------------------------------------------------------
# ConfigFile model validation
# ---------------------------------------------------------------------------


def test_config_file_single_region(minimal_config_dict):
    """Valid config with one region."""
    cfg = ConfigFile(**minimal_config_dict)
    assert cfg.version == SUPPORTED_CONFIG_VERSION
    assert len(cfg.reference_regions) == 1
    assert cfg.segmentation_type is None


def test_config_file_multi_region(minimal_region_dict):
    """Config with multiple reference regions."""
    second = {**minimal_region_dict, "name": "pons"}
    data = {
        "version": SUPPORTED_CONFIG_VERSION,
        "reference_regions": [minimal_region_dict, second],
    }
    cfg = ConfigFile(**data)
    assert len(cfg.reference_regions) == 2
    assert cfg.reference_regions[1].name == "pons"


def test_config_file_with_segmentation_type(full_config_dict):
    """segmentation_type is preserved."""
    cfg = ConfigFile(**full_config_dict)
    assert cfg.segmentation_type == "freesurfer"


def test_config_file_unsupported_version(minimal_region_dict):
    """version != SUPPORTED_CONFIG_VERSION should fail."""
    data = {"version": 999, "reference_regions": [minimal_region_dict]}
    with pytest.raises(Exception):
        ConfigFile(**data)


def test_config_file_empty_regions():
    """reference_regions must be non-empty."""
    data = {"version": SUPPORTED_CONFIG_VERSION, "reference_regions": []}
    with pytest.raises(Exception):
        ConfigFile(**data)


# ---------------------------------------------------------------------------
# YAML round-trip
# ---------------------------------------------------------------------------


def test_yaml_round_trip(full_config_dict):
    """save_config → load_config with .yaml extension."""
    cfg = ConfigFile(**full_config_dict)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.yaml"
        save_config(cfg, path)
        loaded = load_config(path)
    assert loaded.version == cfg.version
    assert loaded.reference_regions[0].name == cfg.reference_regions[0].name
    assert loaded.reference_regions[0].ref_indices == cfg.reference_regions[0].ref_indices


def test_yml_extension_round_trip(minimal_config_dict):
    """load_config recognises .yml extension."""
    cfg = ConfigFile(**minimal_config_dict)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.yml"
        save_config(cfg, path)
        loaded = load_config(path)
    assert loaded.version == cfg.version
    assert len(loaded.reference_regions) == 1


def test_yaml_excludes_none(minimal_config_dict):
    """save_config omits None fields from YAML output."""
    cfg = ConfigFile(**minimal_config_dict)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.yaml"
        save_config(cfg, path)
        raw = yaml.safe_load(path.read_text())
    region = raw["reference_regions"][0]
    assert "probability_mask_file" not in region
    assert "mask_file" not in region
    assert "segmentation_type" not in raw


# ---------------------------------------------------------------------------
# JSON round-trip
# ---------------------------------------------------------------------------


def test_json_round_trip(full_config_dict):
    """save_config → load_config with .json extension."""
    cfg = ConfigFile(**full_config_dict)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.json"
        save_config(cfg, path)
        loaded = load_config(path)
    assert loaded.version == cfg.version
    assert loaded.reference_regions[0].name == cfg.reference_regions[0].name


def test_json_excludes_none(minimal_config_dict):
    """save_config omits None fields from JSON output."""
    cfg = ConfigFile(**minimal_config_dict)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.json"
        save_config(cfg, path)
        raw = json.loads(path.read_text())
    region = raw["reference_regions"][0]
    assert "probability_mask_file" not in region


# ---------------------------------------------------------------------------
# Error cases: load_config
# ---------------------------------------------------------------------------


def test_load_config_file_not_found():
    """load_config raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        load_config(Path("/nonexistent/config.yaml"))


def test_load_config_unsupported_extension():
    """load_config raises ValueError for unsupported file extension."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.toml"
        path.write_text("key = 'value'")
        with pytest.raises(ValueError):
            load_config(path)


def test_load_config_malformed_yaml():
    """load_config raises on malformed YAML."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.yaml"
        path.write_text(": : : invalid yaml [[")
        with pytest.raises(Exception):
            load_config(path)


def test_load_config_valid_yaml_invalid_schema():
    """Valid YAML that doesn't match the schema should raise."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.yaml"
        path.write_text(yaml.dump({"version": 1, "reference_regions": [{"name": "x"}]}))
        with pytest.raises(Exception):
            load_config(path)


# ---------------------------------------------------------------------------
# Dict conversion
# ---------------------------------------------------------------------------


def test_config_to_dict(full_config_dict):
    """config_to_dict returns a plain dict matching the input."""
    cfg = ConfigFile(**full_config_dict)
    d = config_to_dict(cfg)
    assert isinstance(d, dict)
    assert d["version"] == SUPPORTED_CONFIG_VERSION
    assert d["reference_regions"][0]["name"] == "cerebellum"
    # None fields should be excluded
    assert (
        "probability_mask_file" not in d["reference_regions"][0]
        or d["reference_regions"][0]["probability_mask_file"] == "/data/prob.nii.gz"
    )


def test_config_from_dict(full_config_dict):
    """config_from_dict round-trips through config_to_dict."""
    cfg = ConfigFile(**full_config_dict)
    d = config_to_dict(cfg)
    cfg2 = config_from_dict(d)
    assert cfg2.version == cfg.version
    assert cfg2.reference_regions[0].name == cfg.reference_regions[0].name
    assert cfg2.reference_regions[0].ref_indices == cfg.reference_regions[0].ref_indices


def test_config_from_dict_invalid():
    """config_from_dict raises on invalid dict."""
    with pytest.raises(Exception):
        config_from_dict({"version": 1, "reference_regions": []})


# ---------------------------------------------------------------------------
# CLI --config integration tests
# ---------------------------------------------------------------------------


def _make_mask_nifti(path, data=None):
    """Helper: write a small NIfTI mask file."""
    if data is None:
        data = np.array([[[1, 2], [1, 2]], [[1, 2], [1, 2]]], dtype=np.float32)
    nib.save(nib.Nifti1Image(data, np.eye(4)), path)


def test_cli_config_single_region():
    """CLI --config with a single region creates output and prints morphometrics."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        mask_path = tmp / "mask.nii"
        output_path = tmp / "output.nii"
        config_path = tmp / "config.yaml"

        _make_mask_nifti(mask_path)

        config_data = {
            "version": SUPPORTED_CONFIG_VERSION,
            "reference_regions": [
                {
                    "name": "test_region",
                    "ref_indices": [1, 2],
                    "erode": 0,
                    "exclude_indices": [],
                    "dilate": 0,
                    "mask_file": str(mask_path),
                    "output_file": str(output_path),
                }
            ],
        }
        config_path.write_text(yaml.dump(config_data))

        result = subprocess.run(
            ["poetry", "run", "refregion", "--config", str(config_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert output_path.exists()
        assert "test_region" in result.stdout
        assert "Voxel count" in result.stdout


def test_cli_config_multi_region():
    """CLI --config with multiple regions creates all output files."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        mask_path = tmp / "mask.nii"
        output1 = tmp / "out1.nii"
        output2 = tmp / "out2.nii"
        config_path = tmp / "config.yaml"

        _make_mask_nifti(mask_path)

        config_data = {
            "version": SUPPORTED_CONFIG_VERSION,
            "reference_regions": [
                {
                    "name": "region_a",
                    "ref_indices": [1],
                    "mask_file": str(mask_path),
                    "output_file": str(output1),
                },
                {
                    "name": "region_b",
                    "ref_indices": [2],
                    "mask_file": str(mask_path),
                    "output_file": str(output2),
                },
            ],
        }
        config_path.write_text(yaml.dump(config_data))

        result = subprocess.run(
            ["poetry", "run", "refregion", "--config", str(config_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert output1.exists()
        assert output2.exists()


def test_cli_config_mutually_exclusive_with_mask():
    """--config and --mask together should produce an error."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        config_path = tmp / "config.yaml"
        config_path.write_text(yaml.dump({"version": 1, "reference_regions": [{"name": "x", "ref_indices": [1]}]}))

        result = subprocess.run(
            ["poetry", "run", "refregion", "--config", str(config_path), "--mask", "/fake/mask.nii"],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0


def test_cli_config_region_missing_mask_file():
    """Region without mask_file in config should produce an error."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        config_path = tmp / "config.yaml"
        config_data = {
            "version": SUPPORTED_CONFIG_VERSION,
            "reference_regions": [
                {
                    "name": "no_mask",
                    "ref_indices": [1],
                    "output_file": "/tmp/out.nii",
                }
            ],
        }
        config_path.write_text(yaml.dump(config_data))

        result = subprocess.run(
            ["poetry", "run", "refregion", "--config", str(config_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
