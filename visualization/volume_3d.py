"""
Enhanced 3D Volumetric Medical Image Visualization
- Interactive volume rendering
- Slice-by-slice navigation (coronal, sagittal, axial)
- AI lesion overlay with confidence scores
- Medical-grade color mapping
- Lesion statistics and analysis
"""

import nibabel as nib
import plotly.graph_objects as go
import numpy as np
from scipy import ndimage
import cv2


def normalize_volume(data):
    """Safely normalize volume data to 0-1 range"""
    if np.max(data) == 0:
        return data
    return data / (np.max(data) + 1e-8)


def create_volume_slices(data, lesion_mask=None):
    """
    Extract axis-aligned slices from 3D volume
    
    Args:
        data: 3D volume
        lesion_mask: Optional binary lesion mask
    
    Returns:
        Dict with axial, sagittal, coronal slices
    """
    depth, height, width = data.shape
    
    slices = {
        "axial": {
            "data": data[depth // 2, :, :],
            "lesion": lesion_mask[depth // 2, :, :] if lesion_mask is not None else None,
            "plane": "Axial (Transverse)",
            "index": depth // 2,
            "max_index": depth
        },
        "sagittal": {
            "data": data[:, height // 2, :],
            "lesion": lesion_mask[:, height // 2, :] if lesion_mask is not None else None,
            "plane": "Sagittal",
            "index": height // 2,
            "max_index": height
        },
        "coronal": {
            "data": data[:, :, width // 2],
            "lesion": lesion_mask[:, :, width // 2] if lesion_mask is not None else None,
            "plane": "Coronal",
            "index": width // 2,
            "max_index": width
        }
    }
    
    return slices


def apply_ai_lesion_to_volume(data, heatmap_3d=None, threshold=0.5):
    """
    Apply 3D AI lesion prediction to volume
    
    Args:
        data: 3D volume data
        heatmap_3d: Optional 3D attention heatmap
        threshold: Confidence threshold for lesion
    
    Returns:
        Binary lesion mask
    """
    if heatmap_3d is None:
        return None
    
    # Normalize heatmap
    heatmap_norm = normalize_volume(heatmap_3d)
    
    # Create binary mask
    lesion_mask = heatmap_norm > threshold
    
    return lesion_mask


def create_3d_volume_figure(data, lesion_mask=None, 
                           opacity_base=0.1, 
                           opacity_lesion=0.7,
                           colorscale_volume="Gray",
                           colorscale_lesion="Reds"):
    """
    Create interactive 3D volume rendering
    
    Args:
        data: 3D volume (normalized 0-1)
        lesion_mask: Optional binary lesion mask
        opacity_base: Opacity of base volume (0-1)
        opacity_lesion: Opacity of lesion overlay (0-1)
        colorscale_volume: Plotly colorscale for volume
        colorscale_lesion: Plotly colorscale for lesion
    
    Returns:
        Plotly figure
    """
    
    depth, height, width = data.shape
    
    # Normalize data
    data_norm = normalize_volume(data)
    
    # Create coordinate arrays
    x = np.arange(width)
    y = np.arange(height)
    z = np.arange(depth)
    
    # Flatten for Volume object
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    
    # Create traces list
    traces = []
    
    # Main volume
    volume_trace = go.Volume(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=data_norm.flatten(),
        opacity=opacity_base,
        surface_count=20,
        colorscale=colorscale_volume,
        showscale=True,
        name="Medical Volume",
        colorbar=dict(
            title="Intensity",
            thickness=15,
            len=0.7,
            x=1.05
        ),
        hovertemplate="<b>Intensity: %{value:.2f}</b><extra></extra>"
    )
    traces.append(volume_trace)
    
    # Lesion overlay
    if lesion_mask is not None:
        lesion_values = lesion_mask.astype(float)
        lesion_trace = go.Volume(
            x=X.flatten(),
            y=Y.flatten(),
            z=Z.flatten(),
            value=lesion_values.flatten(),
            opacity=opacity_lesion,
            surface_count=10,
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(255,0,0,0.8)"]],
            showscale=False,
            name="AI Predicted Lesion",
            hovertemplate="<b>Lesion</b><extra></extra>"
        )
        traces.append(lesion_trace)
    
    # Create figure
    fig = go.Figure(data=traces)
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="<b>3D CT/MRI Volume Visualization</b><br><sub>Rotate, Zoom, Pan - Use Controls</sub>",
            x=0.5,
            xanchor="center",
            font=dict(size=14)
        ),
        scene=dict(
            xaxis=dict(
                title="X (Width)",
                showbackground=True,
                backgroundcolor="rgba(240, 240, 240, 0.9)",
                gridcolor="white"
            ),
            yaxis=dict(
                title="Y (Height)",
                showbackground=True,
                backgroundcolor="rgba(240, 240, 240, 0.9)",
                gridcolor="white"
            ),
            zaxis=dict(
                title="Z (Depth/Slices)",
                showbackground=True,
                backgroundcolor="rgba(240, 240, 240, 0.9)",
                gridcolor="white"
            ),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            ),
            aspectmode="data"
        ),
        margin=dict(l=0, r=0, b=0, t=50),
        height=700,
        hovermode="closest",
        font=dict(size=10)
    )
    
    return fig


def create_slice_comparison_figure(data, lesion_mask=None, plane="axial"):
    """
    Create side-by-side slice comparison: Original + Lesion Overlay
    
    Args:
        data: 3D volume
        lesion_mask: Optional lesion mask
        plane: Which plane to show ("axial", "sagittal", "coronal")
    
    Returns:
        Plotly figure
    """
    
    # Get middle slice
    if plane == "axial":
        slice_idx = data.shape[0] // 2
        original_slice = data[slice_idx, :, :]
        lesion_slice = lesion_mask[slice_idx, :, :] if lesion_mask is not None else None
        title_suffix = "Axial (Transverse)"
    elif plane == "sagittal":
        slice_idx = data.shape[1] // 2
        original_slice = data[:, slice_idx, :]
        lesion_slice = lesion_mask[:, slice_idx, :] if lesion_mask is not None else None
        title_suffix = "Sagittal"
    else:  # coronal
        slice_idx = data.shape[2] // 2
        original_slice = data[:, :, slice_idx]
        lesion_slice = lesion_mask[:, :, slice_idx] if lesion_mask is not None else None
        title_suffix = "Coronal"
    
    # Normalize
    original_norm = normalize_volume(original_slice)
    
    # Create figure
    fig = go.Figure()
    
    height, width = original_slice.shape
    
    # Original image
    fig.add_trace(go.Heatmap(
        z=original_norm,
        colorscale="Gray",
        showscale=True,
        name="Original",
        colorbar=dict(title="Intensity", x=0.46),
        hovertemplate="<b>Original</b><br>Intensity: %{z:.2f}<extra></extra>"
    ))
    
    # Lesion overlay if available
    if lesion_slice is not None:
        lesion_overlay = original_norm.copy()
        lesion_overlay[lesion_slice] = np.maximum(lesion_overlay[lesion_slice], 0.7)
        
        fig.add_trace(go.Heatmap(
            z=lesion_overlay,
            colorscale=[[0, "rgb(0,0,0)"], [0.5, "rgb(255,165,0)"], [1, "rgb(255,0,0)"]],
            showscale=True,
            name="With Lesion",
            colorbar=dict(title="Value", x=1.0),
            xaxis="x2",
            yaxis="y2",
            hovertemplate="<b>With Lesion</b><br>Value: %{z:.2f}<extra></extra>"
        ))
    
    title = f"<b>{title_suffix} Slice Comparison</b>"
    
    fig.update_layout(
        title=title,
        xaxis=dict(title="X Axis", domain=[0, 0.48]),
        xaxis2=dict(title="X Axis", domain=[0.52, 1]),
        yaxis=dict(title="Y Axis"),
        yaxis2=dict(title="Y Axis"),
        height=500,
        hovermode="closest",
        margin=dict(l=50, r=50, b=50, t=80)
    )
    
    return fig


def calculate_lesion_volume(lesion_mask, voxel_size=(1, 1, 1)):
    """
    Calculate lesion volume in mm³
    
    Args:
        lesion_mask: Binary lesion mask
        voxel_size: Size of each voxel in mm (assumed cubic if single value)
    
    Returns:
        Volume statistics dict
    """
    if lesion_mask is None:
        return None
    
    num_voxels = np.sum(lesion_mask)
    
    if isinstance(voxel_size, (int, float)):
        voxel_volume = voxel_size ** 3
    else:
        voxel_volume = np.prod(voxel_size)
    
    total_volume = num_voxels * voxel_volume
    
    # Get lesion centroid
    centroid = ndimage.center_of_mass(lesion_mask)
    
    # Get lesion bounding box
    labeled_array, num_features = ndimage.label(lesion_mask)
    
    stats = {
        "num_voxels": int(num_voxels),
        "volume_mm3": float(total_volume),
        "volume_cm3": float(total_volume / 1000),
        "centroid": centroid if centroid is not None else None,
        "num_lesions": num_features
    }
    
    return stats


def show_volume_3d(nii_file, lesion_heatmap_3d=None, 
                   lesion_threshold=0.5,
                   show_lesion_overlay=True,
                   opacity_base=0.1,
                   opacity_lesion=0.7):
    """
    Main function for enhanced 3D volumetric visualization
    
    Args:
        nii_file: Path to NIfTI file or file object
        lesion_heatmap_3d: Optional 3D attention heatmap (same shape as volume)
        lesion_threshold: Confidence threshold for lesion (0-1)
        show_lesion_overlay: Whether to show lesion prediction
        opacity_base: Base volume opacity
        opacity_lesion: Lesion overlay opacity
    
    Returns:
        Plotly figure
    """
    
    try:
        # Load NIfTI file
        if isinstance(nii_file, str):
            nii = nib.load(nii_file)
        else:
            # File-like object from Streamlit uploader
            nii = nib.load(nii_file)
        
        data = nii.get_fdata()
        
    except Exception as e:
        print(f"Error loading NIfTI file: {e}")
        # Return placeholder figure
        fig = go.Figure()
        fig.add_annotation(text=f"Error loading file: {str(e)}")
        return fig
    
    # Normalize volume
    data_norm = normalize_volume(data)
    
    # Create lesion mask if heatmap provided
    lesion_mask = None
    if show_lesion_overlay and lesion_heatmap_3d is not None:
        lesion_mask = apply_ai_lesion_to_volume(
            data_norm, 
            lesion_heatmap_3d, 
            lesion_threshold
        )
    
    # Create 3D volume figure
    fig = create_3d_volume_figure(
        data=data_norm,
        lesion_mask=lesion_mask,
        opacity_base=opacity_base,
        opacity_lesion=opacity_lesion,
        colorscale_volume="Gray",
        colorscale_lesion="Reds"
    )
    
    return fig


def create_mip_3d(data, lesion_mask=None, axis=0):
    """
    Create Maximum Intensity Projection (MIP) from 3D volume
    Medical standard for highlighting bright structures
    
    Args:
        data: 3D volume
        lesion_mask: Optional lesion mask
        axis: Projection axis (0=Z, 1=Y, 2=X)
    
    Returns:
        2D MIP image
    """
    
    # Normalize
    data_norm = normalize_volume(data)
    
    # Compute MIP
    mip = np.max(data_norm, axis=axis)
    
    # Apply lesion if available
    if lesion_mask is not None:
        mip_lesion = np.max(lesion_mask, axis=axis)
        mip_rgb = np.stack([mip, mip, mip], axis=2)
        
        # Color lesion areas red
        lesion_pixels = mip_lesion > 0
        mip_rgb[lesion_pixels, 0] = np.minimum(mip_rgb[lesion_pixels, 0] + 0.5, 1.0)
        mip_rgb[lesion_pixels, 1] = np.maximum(mip_rgb[lesion_pixels, 1] - 0.3, 0)
        mip_rgb[lesion_pixels, 2] = np.maximum(mip_rgb[lesion_pixels, 2] - 0.3, 0)
        
        return mip_rgb
    
    return mip


def create_advanced_volume_viewer(nii_file, lesion_heatmap_3d=None):
    """
    Create advanced multi-view volume viewer
    Shows: 3D Volume + Axial + Sagittal + Coronal slices
    
    Args:
        nii_file: NIfTI file path or file object
        lesion_heatmap_3d: Optional 3D lesion heatmap
    
    Returns:
        Dict with multiple figures
    """
    
    # Load data
    nii = nib.load(nii_file)
    data = nii.get_fdata()
    data_norm = normalize_volume(data)
    
    # Create lesion mask
    lesion_mask = None
    if lesion_heatmap_3d is not None:
        lesion_mask = apply_ai_lesion_to_volume(data_norm, lesion_heatmap_3d)
    
    # Create all views
    views = {
        "3d_volume": create_3d_volume_figure(data_norm, lesion_mask),
        "axial": create_slice_comparison_figure(data_norm, lesion_mask, "axial"),
        "sagittal": create_slice_comparison_figure(data_norm, lesion_mask, "sagittal"),
        "coronal": create_slice_comparison_figure(data_norm, lesion_mask, "coronal"),
        "lesion_stats": calculate_lesion_volume(lesion_mask)
    }
    
    return views


if __name__ == "__main__":
    # Test with synthetic data
    test_volume = np.random.rand(64, 128, 128)
    test_lesion = np.random.rand(64, 128, 128) > 0.8
    
    fig = create_3d_volume_figure(test_volume, test_lesion)
    fig.show()