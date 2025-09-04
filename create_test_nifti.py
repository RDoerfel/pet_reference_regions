#!/usr/bin/env python3
"""
Create a small test NIfTI file for webapp testing
"""

import numpy as np
import nibabel as nib

def create_test_segmentation():
    """Create a small test segmentation mask"""
    # Create a small 32x32x32 volume
    data = np.zeros((32, 32, 32), dtype=np.int16)
    
    # Create some simple regions
    data[8:24, 8:24, 8:24] = 7  # Large central region (index 7)
    data[10:14, 10:14, 10:14] = 8  # Smaller region inside (index 8)
    data[20:28, 4:12, 4:12] = 2   # Side region to exclude (index 2)
    
    # Create NIfTI image with standard affine
    affine = np.eye(4)
    img = nib.Nifti1Image(data, affine)
    
    # Save as compressed NIfTI
    nib.save(img, 'test_segmentation.nii.gz')
    print("✅ Created test_segmentation.nii.gz (32x32x32, ~4KB)")
    
    return data.shape, np.unique(data)

def create_test_probability():
    """Create a test probability mask"""
    # Create probability map
    prob_data = np.random.rand(32, 32, 32).astype(np.float32)
    
    # Make central region high probability
    prob_data[8:24, 8:24, 8:24] = np.random.uniform(0.7, 1.0, (16, 16, 16))
    
    # Create NIfTI image
    affine = np.eye(4)
    img = nib.Nifti1Image(prob_data, affine)
    
    # Save
    nib.save(img, 'test_probability.nii.gz')
    print("✅ Created test_probability.nii.gz (32x32x32, ~32KB)")
    
    return prob_data.shape, (prob_data.min(), prob_data.max())

if __name__ == "__main__":
    print("Creating test NIfTI files for webapp testing...")
    
    # Create test files
    seg_shape, seg_labels = create_test_segmentation()
    prob_shape, prob_range = create_test_probability()
    
    print(f"\n📊 Test Files Summary:")
    print(f"Segmentation: {seg_shape}, labels: {seg_labels}")
    print(f"Probability: {prob_shape}, range: {prob_range[0]:.3f}-{prob_range[1]:.3f}")
    
    print(f"\n🧪 Webapp Test Parameters:")
    print(f"Reference Indices: 7,8")
    print(f"Exclusion Indices: 2")
    print(f"Probability Threshold: 0.5")
    print(f"Expected: ~3000-4000 reference voxels")
    
    print(f"\n🌐 Upload these files to test the webapp:")
    print(f"1. Upload test_segmentation.nii.gz as segmentation")
    print(f"2. Upload test_probability.nii.gz as probability (optional)")
    print(f"3. Use parameters above and process")