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
        self.prob_img = None
        self.prob_data = None
        self.processed_mask = None
        self.available_indices = []


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
    temp_path = f'/tmp/{filename}'
    with open(temp_path, 'wb') as f:
        f.write(bytes_data)

    # Load with nibabel from the path
    img = nib.load(temp_path)
    data = img.get_fdata()

    return img, data


async def on_t1_load(event):
    """Handle T1 image loading"""
    try:
        update_status('load-status', 'Loading T1 image...', 'info')
        store.t1_img, store.t1_data = await load_nifti_file(event.target)
        # Cache intensity range for faster rendering
        store.t1_min = float(store.t1_data.min())
        store.t1_max = float(store.t1_data.max())
        update_status('load-status', f'T1 loaded: {store.t1_data.shape}', 'success')
        update_sliders()
        render_all_views()
    except Exception as e:
        update_status('load-status', f'Error loading T1: {str(e)}', 'error')
        console.error(str(e))


async def on_mask_load(event):
    """Handle mask loading"""
    try:
        update_status('load-status', 'Loading mask...', 'info')
        store.mask_img, store.mask_data = await load_nifti_file(event.target)
        store.mask_original = store.mask_data.copy()
        store.processed_mask = None

        unique_indices = np.unique(store.mask_data)
        unique_indices = unique_indices[unique_indices > 0]
        store.available_indices = [int(idx) for idx in unique_indices]

        # Display available indices
        indices_span = document.getElementById('available-indices')
        indices_span.textContent = ', '.join(str(idx) for idx in store.available_indices)

        # Pre-fill the input with all available indices
        input_field = document.getElementById('selected-indices-input')
        input_field.value = ', '.join(str(idx) for idx in store.available_indices)

        update_status('load-status', f'Mask loaded: {store.mask_data.shape}, {len(store.available_indices)} regions', 'success')
        document.getElementById('apply-btn').disabled = False
        document.getElementById('reset-btn').disabled = False
        update_sliders()
        render_all_views()
    except Exception as e:
        update_status('load-status', f'Error loading mask: {str(e)}', 'error')
        console.error(str(e))


async def on_prob_load(event):
    """Handle probability mask loading"""
    try:
        update_status('load-status', 'Loading probability mask...', 'info')
        store.prob_img, store.prob_data = await load_nifti_file(event.target)
        update_status('load-status', f'Probability mask loaded: {store.prob_data.shape}', 'success')
    except Exception as e:
        update_status('load-status', f'Error loading probability: {str(e)}', 'error')
        console.error(str(e))


def update_status(element_id, message, status_type='info'):
    """Update a status message element"""
    status_div = document.getElementById(element_id)
    status_div.innerHTML = f'<div class="status {status_type}">{message}</div>'


def update_sliders():
    """Update slider ranges based on loaded data"""
    if store.t1_data is not None:
        shape = store.t1_data.shape

        slider_x = document.getElementById('slider-x')
        slider_x.max = str(shape[0] - 1)
        slider_x.value = str(shape[0] // 2)
        document.getElementById('value-x').textContent = str(shape[0] // 2)

        slider_y = document.getElementById('slider-y')
        slider_y.max = str(shape[1] - 1)
        slider_y.value = str(shape[1] // 2)
        document.getElementById('value-y').textContent = str(shape[1] // 2)

        slider_z = document.getElementById('slider-z')
        slider_z.max = str(shape[2] - 1)
        slider_z.value = str(shape[2] // 2)
        document.getElementById('value-z').textContent = str(shape[2] // 2)


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
    ctx = canvas.getContext('2d')

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
    rgba_data[:, :, 3] = 255       # A

    if mask_slice is not None:
        mask_slice = np.rot90(mask_slice, k=rotation)
        mask_overlay = mask_slice > 0
        rgba_data[mask_overlay, 0] = np.minimum(rgba_data[mask_overlay, 0] + 100, 255)
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

    x = int(document.getElementById('slider-x').value)
    y = int(document.getElementById('slider-y').value)
    z = int(document.getElementById('slider-z').value)

    mask_to_display = store.processed_mask if store.processed_mask is not None else store.mask_data

    # Each view needs different orientation
    # Axial: transverse slice (z)
    render_slice('canvas-axial', store.t1_data[:, :, z],
               mask_to_display[:, :, z] if mask_to_display is not None else None,
               rotation=3)  # 270 degrees (90 counter-clockwise)
    # Coronal: front-to-back slice (y)
    render_slice('canvas-coronal', store.t1_data[:, y, :],
               mask_to_display[:, y, :] if mask_to_display is not None else None,
               rotation=1)  # 90 degrees counter-clockwise
    # Sagittal: left-to-right slice (x)
    render_slice('canvas-sagittal', store.t1_data[x, :, :],
               mask_to_display[x, :, :] if mask_to_display is not None else None,
               rotation=0)  # No rotation


def on_slider_change(event):
    """Handle slider value changes with debouncing"""
    global render_timer

    slider_id = event.target.id
    value = event.target.value

    if slider_id == 'slider-x':
        document.getElementById('value-x').textContent = value
    elif slider_id == 'slider-y':
        document.getElementById('value-y').textContent = value
    elif slider_id == 'slider-z':
        document.getElementById('value-z').textContent = value

    # Debounce rendering - only render after user stops moving slider
    if render_timer is not None:
        window.clearTimeout(render_timer)

    render_timer = window.setTimeout(create_proxy(lambda: render_all_views()), 16)


def apply_operations(event):
    """Apply morphology operations to selected mask regions"""
    if store.mask_original is None:
        update_status('load-status', 'Please load a mask first', 'error')
        return

    try:
        update_status('load-status', 'Applying morphology operations...', 'info')

        # Parse selected indices from text input
        input_field = document.getElementById('selected-indices-input')
        input_text = input_field.value.strip()

        if input_text:
            # Parse comma-separated values
            selected_indices = []
            for part in input_text.split(','):
                part = part.strip()
                if part:
                    try:
                        idx = int(part)
                        if idx in store.available_indices:
                            selected_indices.append(idx)
                        else:
                            update_status('load-status', f'Warning: Index {idx} not found in mask. Ignoring.', 'error')
                    except ValueError:
                        update_status('load-status', f'Invalid index: "{part}". Please enter numbers only.', 'error')
                        return
        else:
            # If empty, use all available indices
            selected_indices = store.available_indices

        if not selected_indices:
            update_status('load-status', 'No valid indices selected', 'error')
            return

        erosion_radius = int(document.getElementById('erosion-radius').value)
        dilation_radius = int(document.getElementById('dilation-radius').value)
        prob_threshold = float(document.getElementById('prob-threshold').value)

        result_mask = np.zeros_like(store.mask_original)

        for idx in selected_indices:
            region_mask = (store.mask_original == idx).astype(float)

            if erosion_radius > 0:
                region_mask = morphology.erode(region_mask, erosion_radius)

            if dilation_radius > 0:
                region_mask = morphology.dilate(region_mask, dilation_radius)

            if store.prob_data is not None:
                region_mask = morphology.apply_probability_mask(region_mask, store.prob_data, prob_threshold)

            result_mask[region_mask > 0] = idx

        store.processed_mask = result_mask
        document.getElementById('save-btn').disabled = False

        update_status('load-status', f'Operations applied successfully to {len(selected_indices)} region(s)', 'success')
        render_all_views()

    except Exception as e:
        update_status('load-status', f'Error: {str(e)}', 'error')
        console.error(str(e))


def reset_mask(event):
    """Reset mask to original state"""
    store.processed_mask = None
    document.getElementById('save-btn').disabled = True
    update_status('load-status', 'Mask reset to original', 'info')
    render_all_views()


def save_mask(event):
    """Save the processed mask as a NIfTI file"""
    if store.processed_mask is None or store.mask_img is None:
        update_status('save-status', 'No processed mask to save', 'error')
        return

    try:
        update_status('save-status', 'Preparing download...', 'info')

        new_img = nib.Nifti1Image(store.processed_mask, store.mask_img.affine, store.mask_img.header)

        bytes_io = io.BytesIO()
        nib.save(new_img, bytes_io)
        bytes_data = bytes_io.getvalue()

        base64_data = base64.b64encode(bytes_data).decode('utf-8')
        data_url = f'data:application/octet-stream;base64,{base64_data}'

        link = document.createElement('a')
        link.href = data_url
        link.download = 'processed_mask.nii.gz'
        link.click()

        update_status('save-status', 'Mask downloaded successfully', 'success')

    except Exception as e:
        update_status('save-status', f'Error saving: {str(e)}', 'error')
        console.error(str(e))


def setup_listeners():
    """Set up all event listeners"""
    document.getElementById('t1-file').addEventListener('change', create_proxy(on_t1_load))
    document.getElementById('mask-file').addEventListener('change', create_proxy(on_mask_load))
    document.getElementById('prob-file').addEventListener('change', create_proxy(on_prob_load))

    document.getElementById('slider-x').addEventListener('input', create_proxy(on_slider_change))
    document.getElementById('slider-y').addEventListener('input', create_proxy(on_slider_change))
    document.getElementById('slider-z').addEventListener('input', create_proxy(on_slider_change))

    document.getElementById('apply-btn').addEventListener('click', create_proxy(apply_operations))
    document.getElementById('reset-btn').addEventListener('click', create_proxy(reset_mask))
    document.getElementById('save-btn').addEventListener('click', create_proxy(save_mask))

    console.log('Event listeners set up successfully')


async def initialize():
    """Initialize the application"""
    global morphology

    import micropip

    console.log("Installing refregion package...")
    # Install without dependencies to avoid matplotlib version conflict
    await micropip.install('./refregion-0.1.0-py3-none-any.whl', deps=False)
    console.log("refregion package installed")

    # Import morphology module after package is installed
    from refregion import morphology as morph
    morphology = morph
    console.log("morphology module imported")

    setup_listeners()

    document.getElementById('loading').style.display = 'none'
    document.getElementById('main-content').style.display = 'block'

    console.log('PET Reference Region Editor initialized')


# Start the application
asyncio.ensure_future(initialize())
