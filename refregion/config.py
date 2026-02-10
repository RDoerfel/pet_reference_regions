import json
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field, model_validator

SUPPORTED_CONFIG_VERSION = 1


class ReferenceRegionConfig(BaseModel):
    name: str
    ref_indices: List[int]
    erode: int = Field(default=0, ge=0)
    exclude_indices: List[int] = Field(default_factory=list)
    dilate: int = Field(default=0, ge=0)
    probability_mask_file: Optional[str] = None
    probability_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    mask_file: Optional[str] = None
    output_file: Optional[str] = None

    @model_validator(mode="after")
    def _ref_indices_non_empty(self):
        if len(self.ref_indices) == 0:
            raise ValueError("ref_indices must not be empty")
        return self


class ConfigFile(BaseModel):
    version: int
    segmentation_type: Optional[str] = None
    reference_regions: List[ReferenceRegionConfig]

    @model_validator(mode="after")
    def _validate(self):
        if self.version != SUPPORTED_CONFIG_VERSION:
            raise ValueError(f"Unsupported config version {self.version}, expected {SUPPORTED_CONFIG_VERSION}")
        if len(self.reference_regions) == 0:
            raise ValueError("reference_regions must not be empty")
        return self


def load_config(path: Path) -> ConfigFile:
    """Load and validate a config file (YAML or JSON)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    suffix = path.suffix.lower()
    raw_text = path.read_text()

    if suffix in (".yaml", ".yml"):
        data = yaml.safe_load(raw_text)
    elif suffix == ".json":
        data = json.loads(raw_text)
    else:
        raise ValueError(f"Unsupported config file extension: {suffix} (use .yaml, .yml, or .json)")

    return ConfigFile(**data)


def save_config(config: ConfigFile, path: Path) -> None:
    """Serialize a ConfigFile to YAML or JSON, omitting None fields."""
    path = Path(path)
    data = config.model_dump(exclude_none=True)

    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
    elif suffix == ".json":
        path.write_text(json.dumps(data, indent=2))
    else:
        raise ValueError(f"Unsupported config file extension: {suffix} (use .yaml, .yml, or .json)")


def config_to_dict(config: ConfigFile) -> dict:
    """Convert a ConfigFile to a plain dict (None fields excluded)."""
    return config.model_dump(exclude_none=True)


def config_from_dict(data: dict) -> ConfigFile:
    """Create a ConfigFile from a plain dict."""
    return ConfigFile(**data)
