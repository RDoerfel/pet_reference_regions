import asyncio
import numpy as np
import nibabel as nib
from js import document, Uint8Array, console, window
from pyodide.ffi import create_proxy, to_js
import io
import base64

# morphology module will be imported after package installation
morphology = None

# Debounce timer for slider changes
render_timer = None


class DataStore:
    """Global data storage for the application"""

    def __init__(self):
        self.t1_img = None
        self.t1_data = None
        self.t1_min = None
        self.t1_max = None
        self.mask_img = None
        self.mask_data = None
        self.mask_original = None
        self.processed_mask = None
        self.available_indices = []
        self.mask_indices = []
        self.exclusion_indices = []
        self.config_regions = []
        self.selected_region_index = 0


store = DataStore()


async def load_nifti_file(file_input):
    """Load a NIfTI/MGZ file from a file input element"""
    files = file_input.files
    if len(files) == 0:
        return None, None

    file = files.item(0)
    filename = file.name
    array_buffer = await file.arrayBuffer()
    bytes_data = Uint8Array.new(array_buffer).to_py().tobytes()

    # Write to Pyodide's in-memory virtual filesystem
    # Note: This filesystem only exists in browser RAM, nothing is written to disk
    temp_path = f"/tmp/{filename}"
    with open(temp_path, "wb") as f:
        f.write(bytes_data)

    # Load with nibabel from the path
    img = nib.load(temp_path)
    data = img.get_fdata()

    return img, data


async def on_t1_load(event):
    """Handle T1 image loading"""
    try:
        update_status("load-status", "Loading T1 image...", "info")
        store.t1_img, store.t1_data = await load_nifti_file(event.target)
        # Cache intensity range for faster rendering
        store.t1_min = float(store.t1_data.min())
        store.t1_max = float(store.t1_data.max())
        update_status("load-status", f"T1 loaded: {store.t1_data.shape}", "success")
        update_sliders()
        render_all_views()
    except Exception as e:
        update_status("load-status", f"Error loading T1: {str(e)}", "error")
        console.error(str(e))


async def on_mask_load(event):
    """Handle mask loading"""
    try:
        update_status("load-status", "Loading mask...", "info")
        store.mask_img, store.mask_data = await load_nifti_file(event.target)
        store.mask_original = store.mask_data.copy()
        store.processed_mask = None

        unique_indices = np.unique(store.mask_data)
        store.available_indices = [int(idx) for idx in unique_indices]

        # Display available indices
        indices_span = document.getElementById("available-indices")
        indices_span.textContent = ", ".join(str(idx) for idx in store.available_indices)

        # Pre-fill the mask input with all available indices
        mask_input = document.getElementById("mask-indices-input")
        mask_input.value = ""

        # Leave exclusion input empty by default
        exclusion_input = document.getElementById("exclusion-indices-input")
        exclusion_input.value = ""

        update_status(
            "load-status", f"Mask loaded: {store.mask_data.shape}, {len(store.available_indices)} regions", "success"
        )
        document.getElementById("apply-btn").disabled = False
        document.getElementById("reset-btn").disabled = False
        update_sliders()
        render_all_views()
    except Exception as e:
        update_status("load-status", f"Error loading mask: {str(e)}", "error")
        console.error(str(e))


def update_status(element_id, message, status_type="info"):
    """Update a status message element"""
    status_div = document.getElementById(element_id)
    status_div.innerHTML = f'<div class="status {status_type}">{message}</div>'


def update_sliders():
    """Update slider ranges based on loaded data"""
    if store.t1_data is not None:
        shape = store.t1_data.shape

        slider_x = document.getElementById("slider-x")
        slider_x.max = str(shape[0] - 1)
        slider_x.value = str(shape[0] // 2)
        document.getElementById("value-x").textContent = str(shape[0] // 2)

        slider_y = document.getElementById("slider-y")
        slider_y.max = str(shape[1] - 1)
        slider_y.value = str(shape[1] // 2)
        document.getElementById("value-y").textContent = str(shape[1] // 2)

        slider_z = document.getElementById("slider-z")
        slider_z.max = str(shape[2] - 1)
        slider_z.value = str(shape[2] // 2)
        document.getElementById("value-z").textContent = str(shape[2] // 2)


def normalize_slice(slice_data):
    """Normalize a 2D slice to 0-255 uint8 range using cached T1 min/max"""
    if slice_data.size == 0:
        return slice_data
    # Use cached global min/max for consistent windowing across slices
    if store.t1_min is not None and store.t1_max is not None:
        min_val = store.t1_min
        max_val = store.t1_max
    else:
        min_val = slice_data.min()
        max_val = slice_data.max()

    if max_val - min_val > 0:
        return ((np.clip(slice_data, min_val, max_val) - min_val) / (max_val - min_val) * 255).astype(np.uint8)
    return np.zeros_like(slice_data, dtype=np.uint8)


def render_slice(canvas_id, slice_data, mask_slice=None, rotation=1):
    """Render a 2D slice with optional mask overlay

    Args:
        canvas_id: ID of the canvas element
        slice_data: 2D numpy array of image data
        mask_slice: Optional 2D numpy array of mask data
        rotation: Number of 90-degree rotations (0-3)
    """
    canvas = document.getElementById(canvas_id)
    ctx = canvas.getContext("2d")

    # Downsample if image is too large for performance
    max_size = 512
    original_shape = slice_data.shape

    if max(original_shape) > max_size:
        # Calculate downsampling factor
        factor = max(original_shape) / max_size
        new_h = int(original_shape[0] / factor)
        new_w = int(original_shape[1] / factor)

        # Downsample using slicing (faster than interpolation)
        step_h = max(1, int(original_shape[0] / new_h))
        step_w = max(1, int(original_shape[1] / new_w))
        slice_data = slice_data[::step_h, ::step_w]

        if mask_slice is not None:
            mask_slice = mask_slice[::step_h, ::step_w]

    img_data = normalize_slice(slice_data)
    img_data = np.rot90(img_data, k=rotation)
    h, w = img_data.shape

    # Create RGBA data directly (more efficient)
    rgba_data = np.zeros((h, w, 4), dtype=np.uint8)
    rgba_data[:, :, 0] = img_data  # R
    rgba_data[:, :, 1] = img_data  # G
    rgba_data[:, :, 2] = img_data  # B
    rgba_data[:, :, 3] = 255  # A

    if mask_slice is not None:
        mask_slice = np.rot90(mask_slice, k=rotation)
        mask_overlay = mask_slice > 0
        rgba_data[mask_overlay, 1] = np.maximum(rgba_data[mask_overlay, 1] - 50, 0)

    # Set canvas to actual pixel size to avoid CSS scaling artifacts
    canvas.width = w
    canvas.height = h

    # Disable image smoothing for crisp pixels
    ctx.imageSmoothingEnabled = False

    # Create ImageData directly from flattened array - much faster
    image_data = ctx.createImageData(w, h)
    image_data.data.assign(rgba_data.flatten())

    ctx.putImageData(image_data, 0, 0)


def render_all_views():
    """Render all three orthogonal views"""
    if store.t1_data is None:
        return

    x = int(document.getElementById("slider-x").value)
    y = int(document.getElementById("slider-y").value)
    z = int(document.getElementById("slider-z").value)

    mask_to_display = store.processed_mask if store.processed_mask is not None else store.mask_data

    # Each view needs different orientation
    # Axial: transverse slice (z)
    render_slice(
        "canvas-axial",
        store.t1_data[:, :, z],
        mask_to_display[:, :, z] if mask_to_display is not None else None,
        rotation=3,
    )  # 270 degrees (90 counter-clockwise)
    # Coronal: front-to-back slice (y)
    render_slice(
        "canvas-coronal",
        store.t1_data[:, y, :],
        mask_to_display[:, y, :] if mask_to_display is not None else None,
        rotation=1,
    )  # 90 degrees counter-clockwise
    # Sagittal: left-to-right slice (x)
    render_slice(
        "canvas-sagittal",
        store.t1_data[x, :, :],
        mask_to_display[x, :, :] if mask_to_display is not None else None,
        rotation=0,
    )  # No rotation


def on_slider_change(event):
    """Handle slider value changes with debouncing"""
    global render_timer

    slider_id = event.target.id
    value = event.target.value

    if slider_id == "slider-x":
        document.getElementById("value-x").textContent = value
    elif slider_id == "slider-y":
        document.getElementById("value-y").textContent = value
    elif slider_id == "slider-z":
        document.getElementById("value-z").textContent = value

    # Debounce rendering - only render after user stops moving slider
    if render_timer is not None:
        window.clearTimeout(render_timer)

    render_timer = window.setTimeout(create_proxy(lambda: render_all_views()), 16)


def update_morphometrics(mask_indices, processed_mask):
    """Compute and display morphometrics in the UI."""
    # Original selection: all voxels matching selected mask indices
    original_mask = np.isin(store.mask_original, mask_indices).astype(np.uint8)

    original_count = int(np.count_nonzero(original_mask))
    processed_count = int(np.count_nonzero(processed_mask))

    # Compute voxel volume from header
    if store.mask_img is not None:
        zooms = store.mask_img.header.get_zooms()[:3]
        voxel_vol = float(np.prod(zooms))
    else:
        voxel_vol = 1.0

    volume = processed_count * voxel_vol
    retention = (processed_count / original_count * 100) if original_count > 0 else 0.0

    container = document.getElementById("morphometrics-container")
    container.innerHTML = (
        f'<table style="border-collapse: collapse;">'
        f'<tr><td style="padding: 4px 16px 4px 0; font-weight: 600;">Voxel count:</td>'
        f'<td style="padding: 4px 0;">{processed_count}</td></tr>'
        f'<tr><td style="padding: 4px 16px 4px 0; font-weight: 600;">Volume (mm3):</td>'
        f'<td style="padding: 4px 0;">{volume:.2f}</td></tr>'
        f'<tr><td style="padding: 4px 16px 4px 0; font-weight: 600;">Retention (%):</td>'
        f'<td style="padding: 4px 0;">{retention:.2f}</td></tr>'
        f"</table>"
    )


def update_save_filename():
    """Update the save filename based on the current region name."""
    name = document.getElementById("region-name-input").value.strip()
    filename = f"label-{name}_mask.nii.gz" if name else "processed_mask.nii.gz"
    document.getElementById("save-filename").value = filename


def sync_ui_to_current_region():
    """Read current UI field values and write them into the currently selected config region."""
    if not store.config_regions:
        return
    idx = store.selected_region_index
    if idx < 0 or idx >= len(store.config_regions):
        return

    region = store.config_regions[idx]
    region["name"] = document.getElementById("region-name-input").value.strip() or "reference_region"

    mask_text = document.getElementById("mask-indices-input").value.strip()
    ref_indices = []
    if mask_text:
        for part in mask_text.split(","):
            part = part.strip()
            if part:
                try:
                    ref_indices.append(int(part))
                except ValueError:
                    pass
    region["ref_indices"] = ref_indices

    exclusion_text = document.getElementById("exclusion-indices-input").value.strip()
    exclude_indices = []
    if exclusion_text:
        for part in exclusion_text.split(","):
            part = part.strip()
            if part:
                try:
                    exclude_indices.append(int(part))
                except ValueError:
                    pass
    region["exclude_indices"] = exclude_indices

    region["erode"] = int(document.getElementById("erosion-radius").value)
    region["dilate"] = int(document.getElementById("dilation-radius").value)


def load_region_to_ui(region_dict):
    """Populate UI fields from a region dict."""
    if "name" in region_dict:
        document.getElementById("region-name-input").value = region_dict["name"]

    if "ref_indices" in region_dict:
        document.getElementById("mask-indices-input").value = ", ".join(str(i) for i in region_dict["ref_indices"])
    else:
        document.getElementById("mask-indices-input").value = ""

    if "exclude_indices" in region_dict and region_dict["exclude_indices"]:
        document.getElementById("exclusion-indices-input").value = ", ".join(
            str(i) for i in region_dict["exclude_indices"]
        )
    else:
        document.getElementById("exclusion-indices-input").value = ""

    if "erode" in region_dict:
        document.getElementById("erosion-radius").value = str(region_dict["erode"])
    else:
        document.getElementById("erosion-radius").value = "0"

    if "dilate" in region_dict:
        document.getElementById("dilation-radius").value = str(region_dict["dilate"])
    else:
        document.getElementById("dilation-radius").value = "0"

    update_save_filename()


def populate_region_selector(regions):
    """Populate the region selector dropdown and show/hide it."""
    selector = document.getElementById("region-selector")
    group = document.getElementById("region-selector-group")

    # Clear existing options
    selector.innerHTML = ""

    for i, region in enumerate(regions):
        option = document.createElement("option")
        option.value = str(i)
        option.textContent = region.get("name", f"Region {i + 1}")
        selector.appendChild(option)

    if len(regions) > 1:
        group.style.display = "flex"
    else:
        group.style.display = "none"

    selector.value = "0"


def on_region_select(event):
    """Handle region selector change: sync current state, load new region."""
    # Save current UI state back to the previously selected region
    sync_ui_to_current_region()

    # Load the newly selected region
    new_index = int(event.target.value)
    store.selected_region_index = new_index
    load_region_to_ui(store.config_regions[new_index])


def apply_operations(event):
    """Apply morphology operations to selected mask and exclusion regions"""
    if store.mask_original is None:
        update_status("load-status", "Please load a mask first", "error")
        return

    try:
        update_status("load-status", "Applying morphology operations...", "info")

        # Parse mask indices from text input
        mask_input = document.getElementById("mask-indices-input")
        mask_text = mask_input.value.strip()

        mask_indices = []
        if mask_text:
            for part in mask_text.split(","):
                part = part.strip()
                if part:
                    try:
                        idx = int(part)
                        if idx in store.available_indices:
                            mask_indices.append(idx)
                        else:
                            update_status(
                                "load-status", f"Warning: Mask index {idx} not found in mask. Ignoring.", "error"
                            )
                    except ValueError:
                        update_status(
                            "load-status", f'Invalid mask index: "{part}". Please enter numbers only.', "error"
                        )
                        return

        # Parse exclusion indices from text input
        exclusion_input = document.getElementById("exclusion-indices-input")
        exclusion_text = exclusion_input.value.strip()

        exclusion_indices = []
        if exclusion_text:
            for part in exclusion_text.split(","):
                part = part.strip()
                if part:
                    try:
                        idx = int(part)
                        if idx in store.available_indices:
                            exclusion_indices.append(idx)
                        else:
                            update_status(
                                "load-status", f"Warning: Exclusion index {idx} not found in mask. Ignoring.", "error"
                            )
                    except ValueError:
                        update_status(
                            "load-status", f'Invalid exclusion index: "{part}". Please enter numbers only.', "error"
                        )
                        return

        if not mask_indices and not exclusion_indices:
            update_status("load-status", "Please select at least one mask or exclusion index", "error")
            return

        erosion_radius = int(document.getElementById("erosion-radius").value)
        dilation_radius = int(document.getElementById("dilation-radius").value)

        result_mask = np.zeros_like(store.mask_original)

        # Process mask indices with erosion
        for idx in mask_indices:
            region_mask = (store.mask_original == idx).astype(float)

            if erosion_radius > 0:
                region_mask = morphology.erode(region_mask, erosion_radius)

            result_mask[region_mask > 0] = idx

        # Process exclusion indices with dilation, then subtract from result
        exclusion_mask = np.zeros_like(store.mask_original)
        for idx in exclusion_indices:
            region_mask = (store.mask_original == idx).astype(float)

            if dilation_radius > 0:
                region_mask = morphology.dilate(region_mask, dilation_radius)

            exclusion_mask[region_mask > 0] = 1

        # Remove exclusion regions from result mask
        result_mask[exclusion_mask > 0] = 0

        store.processed_mask = result_mask
        document.getElementById("save-btn").disabled = False

        # Compute and display morphometrics
        update_morphometrics(mask_indices, result_mask)

        # Update download filename to reflect current region name
        update_save_filename()

        update_status(
            "load-status",
            f"Operations applied: {len(mask_indices)} mask region(s), {len(exclusion_indices)} exclusion region(s)",
            "success",
        )
        render_all_views()

    except Exception as e:
        update_status("load-status", f"Error: {str(e)}", "error")
        console.error(str(e))


def reset_mask(event):
    """Reset mask to original state"""
    store.processed_mask = None
    document.getElementById("save-btn").disabled = True
    container = document.getElementById("morphometrics-container")
    container.innerHTML = "Apply operations to see morphometrics."
    update_status("load-status", "Mask reset to original", "info")
    render_all_views()


def _build_region_from_ui():
    """Build a single region dict from current UI field values."""
    region_name = document.getElementById("region-name-input").value.strip() or "reference_region"
    mask_text = document.getElementById("mask-indices-input").value.strip()
    exclusion_text = document.getElementById("exclusion-indices-input").value.strip()
    erosion_radius = int(document.getElementById("erosion-radius").value)
    dilation_radius = int(document.getElementById("dilation-radius").value)

    mask_indices = []
    if mask_text:
        for part in mask_text.split(","):
            part = part.strip()
            if part:
                mask_indices.append(int(part))

    exclusion_indices = []
    if exclusion_text:
        for part in exclusion_text.split(","):
            part = part.strip()
            if part:
                exclusion_indices.append(int(part))

    region = {"name": region_name, "ref_indices": mask_indices, "erode": erosion_radius}
    if exclusion_indices:
        region["exclude_indices"] = exclusion_indices
    if dilation_radius > 0:
        region["dilate"] = dilation_radius

    return region


def export_config(event):
    """Export current UI parameters as a YAML config file for download."""
    try:
        import yaml

        # Sync current UI state back to stored regions
        sync_ui_to_current_region()

        if store.config_regions:
            regions = store.config_regions
        else:
            regions = [_build_region_from_ui()]

        config_data = {"version": 1, "reference_regions": regions}

        yaml_str = yaml.dump(config_data, default_flow_style=False, sort_keys=False)
        encoded = base64.b64encode(yaml_str.encode("utf-8")).decode("utf-8")
        data_url = f"data:application/x-yaml;base64,{encoded}"

        filename = regions[0].get("name", "reference_region") if regions else "reference_region"

        link = document.createElement("a")
        link.href = data_url
        link.download = f"{filename}.yaml"
        link.click()

        update_status("save-status", f"Config exported as {filename}.yaml ({len(regions)} region(s))", "success")
    except Exception as e:
        update_status("save-status", f"Error exporting config: {str(e)}", "error")
        console.error(str(e))


async def import_config(event):
    """Import a YAML/JSON config file and populate UI fields."""
    try:
        import yaml

        files = event.target.files
        if len(files) == 0:
            return

        file = files.item(0)
        filename = file.name
        text = await file.text()

        if filename.endswith(".json"):
            import json

            data = json.loads(text)
        else:
            data = yaml.safe_load(text)

        if not isinstance(data, dict) or "reference_regions" not in data:
            update_status("load-status", "Invalid config file: missing reference_regions", "error")
            return

        regions = data["reference_regions"]
        if not regions:
            update_status("load-status", "Config file has no reference regions", "error")
            return

        # Store all regions for multi-region support
        store.config_regions = regions
        store.selected_region_index = 0

        # Populate dropdown and load first region into UI
        populate_region_selector(regions)
        load_region_to_ui(regions[0])

        n_regions = len(regions)
        msg = f"Config imported from {filename} ({n_regions} region(s))"
        update_status("load-status", msg, "success")

        # Reset file input so the same file can be re-imported
        event.target.value = ""

    except Exception as e:
        update_status("load-status", f"Error importing config: {str(e)}", "error")
        console.error(str(e))


def save_mask(event):
    """Save the processed mask as a NIfTI file"""
    if store.processed_mask is None or store.mask_img is None:
        update_status("save-status", "No processed mask to save", "error")
        return

    try:
        # Get filename from input field
        filename_input = document.getElementById("save-filename")
        filename = filename_input.value.strip()

        if not filename:
            update_status("save-status", "Please enter a filename", "error")
            return

        # Ensure filename has .nii.gz extension
        if not filename.endswith(".nii.gz") and not filename.endswith(".nii"):
            filename = filename + ".nii.gz"

        update_status("save-status", "Preparing download...", "info")

        new_img = nib.Nifti1Image(store.processed_mask, store.mask_img.affine, store.mask_img.header)

        # Save to temporary file in Pyodide's virtual filesystem
        temp_path = "/tmp/processed_mask.nii.gz"
        nib.save(new_img, temp_path)

        # Read the file back as bytes
        with open(temp_path, "rb") as f:
            bytes_data = f.read()

        base64_data = base64.b64encode(bytes_data).decode("utf-8")
        data_url = f"data:application/octet-stream;base64,{base64_data}"

        link = document.createElement("a")
        link.href = data_url
        link.download = filename
        link.click()

        update_status("save-status", f"Mask downloaded successfully as {filename}", "success")

    except Exception as e:
        update_status("save-status", f"Error saving: {str(e)}", "error")
        console.error(str(e))


def setup_listeners():
    """Set up all event listeners"""
    document.getElementById("t1-file").addEventListener("change", create_proxy(on_t1_load))
    document.getElementById("mask-file").addEventListener("change", create_proxy(on_mask_load))

    document.getElementById("slider-x").addEventListener("input", create_proxy(on_slider_change))
    document.getElementById("slider-y").addEventListener("input", create_proxy(on_slider_change))
    document.getElementById("slider-z").addEventListener("input", create_proxy(on_slider_change))

    document.getElementById("apply-btn").addEventListener("click", create_proxy(apply_operations))
    document.getElementById("reset-btn").addEventListener("click", create_proxy(reset_mask))
    document.getElementById("save-btn").addEventListener("click", create_proxy(save_mask))
    document.getElementById("export-config-btn").addEventListener("click", create_proxy(export_config))
    document.getElementById("import-config-file").addEventListener("change", create_proxy(import_config))
    document.getElementById("region-selector").addEventListener("change", create_proxy(on_region_select))
    document.getElementById("region-name-input").addEventListener(
        "input", create_proxy(lambda e: update_save_filename())
    )

    console.log("Event listeners set up successfully")


async def initialize():
    """Initialize the application"""
    global morphology

    import micropip

    console.log("Installing refregion package...")
    # Install without dependencies to avoid matplotlib version conflict
    await micropip.install("./refregion-0.1.0-py3-none-any.whl", deps=False)
    console.log("refregion package installed")

    # Import morphology module after package is installed
    from refregion import morphology as morph

    morphology = morph
    console.log("morphology module imported")

    setup_listeners()

    document.getElementById("loading").style.display = "none"
    document.getElementById("main-content").style.display = "block"

    console.log("PET Reference Region Editor initialized")


# Start the application
asyncio.ensure_future(initialize())
