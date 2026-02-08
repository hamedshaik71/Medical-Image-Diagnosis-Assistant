"""
Enhanced Pseudo-3D Medical Image Visualization
- Interactive surface rendering with AI lesion overlay
- Slice-by-slice navigation
- Color-coded lesion highlighting
- Medical-grade visualization
"""

import plotly.graph_objects as go
import numpy as np
import cv2
from scipy import ndimage


def apply_lesion_overlay(image_array, heatmap, threshold=0.5):
    """
    Apply AI-predicted lesion as colored overlay on medical image
    
    Args:
        image_array: Input medical image (normalized 0-1)
        heatmap: Grad-CAM or attention heatmap
        threshold: Threshold for lesion detection (0-1)
    
    Returns:
        RGB image with lesion overlay
    """
    if image_array.ndim == 3:
        gray = np.mean(image_array, axis=2)
    else:
        gray = image_array
    
    # Normalize heatmap
    if heatmap is not None:
        heatmap_norm = heatmap / (np.max(heatmap) + 1e-8)
        lesion_mask = heatmap_norm > threshold
    else:
        lesion_mask = np.zeros_like(gray, dtype=bool)
    
    # Create RGB output
    rgb_image = np.stack([gray, gray, gray], axis=2)
    
    # Apply color overlay for lesion (bright red/orange)
    if np.any(lesion_mask):
        rgb_image[lesion_mask, 0] = np.minimum(rgb_image[lesion_mask, 0] + 0.5, 1.0)  # Red channel
        rgb_image[lesion_mask, 1] = np.maximum(rgb_image[lesion_mask, 1] - 0.2, 0)    # Green channel
        rgb_image[lesion_mask, 2] = np.maximum(rgb_image[lesion_mask, 2] - 0.3, 0)    # Blue channel
    
    return rgb_image, lesion_mask


def create_3d_surface_from_image(image_array, heatmap=None, 
                                 colorscale="Viridis", 
                                 show_lesion=True):
    """
    Creates an enhanced 3D surface visualization from 2D medical image
    
    Args:
        image_array: 2D or 3D medical image
        heatmap: Optional AI attention heatmap for lesion overlay
        colorscale: Plotly colorscale name
        show_lesion: Whether to overlay lesion prediction
    
    Returns:
        Plotly figure object
    """
    
    # Convert to grayscale if needed
    if image_array.ndim == 3:
        gray = np.mean(image_array, axis=2)
    else:
        gray = image_array
    
    # Ensure proper scaling
    if np.max(gray) > 1:
        gray = gray / np.max(gray)
    
    height, width = gray.shape
    
    # Create mesh grid
    x = np.arange(0, width)
    y = np.arange(0, height)
    X, Y = np.meshgrid(x, y)
    Z = gray
    
    # Create base surface
    surface = go.Surface(
        x=X,
        y=Y,
        z=Z,
        colorscale=colorscale,
        showscale=True,
        colorbar=dict(
            title="Intensity",
            thickness=15,
            len=0.7,
            x=1.02
        ),
        name="Medical Image"
    )
    
    traces = [surface]
    
    # Add lesion overlay if provided
    if show_lesion and heatmap is not None:
        try:
            # Ensure heatmap matches image shape
            if heatmap.shape != gray.shape:
                # Resize heatmap to match image
                heatmap_resized = cv2.resize(heatmap, (width, height))
            else:
                heatmap_resized = heatmap
            
            # Normalize heatmap
            heatmap_norm = heatmap_resized / (np.max(heatmap_resized) + 1e-8)
            
            # Ensure heatmap_norm is same shape as Z
            if heatmap_norm.shape != Z.shape:
                heatmap_norm = cv2.resize(heatmap_norm, (Z.shape[1], Z.shape[0]))
            
            # Create lesion surface (slightly above base surface)
            lesion_z = Z + 0.1 * heatmap_norm
            
            lesion_surface = go.Surface(
                x=X,
                y=Y,
                z=lesion_z,
                colorscale=[[0, "rgba(0,0,0,0)"], [0.5, "rgba(255,165,0,0.4)"], [1, "rgba(255,0,0,0.8)"]],
                showscale=False,
                name="AI Predicted Lesion",
                hovertemplate="<b>Lesion Confidence: %{z:.2%}</b><extra></extra>",
                opacity=0.8
            )
            
            traces.append(lesion_surface)
        except Exception as e:
            print(f"Warning: Could not add lesion overlay: {str(e)}")
            # Continue without lesion overlay if error occurs
    
    # Create figure
    fig = go.Figure(data=traces)
    
    # Update layout with enhanced medical styling
    fig.update_layout(
        title=dict(
            text="<b>3D Medical Image Visualization</b><br><sub>Interactive: Rotate, Zoom, Pan</sub>",
            x=0.5,
            xanchor="center"
        ),
        scene=dict(
            xaxis=dict(
                title="Width (pixels)",
                showbackground=True,
                backgroundcolor="rgba(230, 230,230, 0.5)"
            ),
            yaxis=dict(
                title="Height (pixels)",
                showbackground=True,
                backgroundcolor="rgba(230, 230, 230, 0.5)"
            ),
            zaxis=dict(
                title="Intensity",
                showbackground=True,
                backgroundcolor="rgba(230, 230, 230, 0.5)"
            ),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            ),
            aspectmode="auto"
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        height=600,
        hovermode="closest",
        font=dict(size=10)
    )
    
    return fig


def create_slice_viewer(image_array, heatmap=None, 
                       initial_slice=None):
    """
    Creates interactive slice viewer showing all 2D slices
    
    Args:
        image_array: Medical image
        heatmap: Optional attention heatmap
        initial_slice: Initial slice number to display
    
    Returns:
        Dict with slices and metadata
    """
    
    if image_array.ndim == 3:
        gray = np.mean(image_array, axis=2)
    else:
        gray = image_array
    
    # Ensure 0-1 range
    if np.max(gray) > 1:
        gray = gray / np.max(gray)
    
    height, width = gray.shape
    
    if initial_slice is None:
        initial_slice = height // 2
    
    # Prepare slices
    slices_data = {
        "current_slice": initial_slice,
        "total_slices": height,
        "width": width,
        "height": height,
        "images": []
    }
    
    # Create overlaid slices
    for slice_idx in range(height):
        slice_data = gray[slice_idx, :]
        
        # Apply heatmap overlay if available
        if heatmap is not None:
            heatmap_slice = heatmap[slice_idx, :]
            heatmap_norm = heatmap_slice / (np.max(heatmap_slice) + 1e-8)
            
            # Create RGB with overlay
            rgb_slice = np.stack([slice_data, slice_data, slice_data], axis=1)
            
            # Red channel for lesion
            lesion_mask = heatmap_norm > 0.5
            if np.any(lesion_mask):
                rgb_slice[lesion_mask, 0] = np.minimum(rgb_slice[lesion_mask, 0] + 0.5, 1.0)
                rgb_slice[lesion_mask, 1] = np.maximum(rgb_slice[lesion_mask, 1] - 0.2, 0)
                rgb_slice[lesion_mask, 2] = np.maximum(rgb_slice[lesion_mask, 2] - 0.3, 0)
            
            slices_data["images"].append({
                "slice": rgb_slice,
                "heatmap": heatmap_norm,
                "index": slice_idx
            })
        else:
            slices_data["images"].append({
                "slice": np.stack([slice_data, slice_data, slice_data], axis=1),
                "heatmap": None,
                "index": slice_idx
            })
    
    return slices_data


def create_mip_projection(image_array, heatmap=None, 
                          axis=0):
    """
    Maximum Intensity Projection - Shows brightest voxels along projection axis
    Common in medical imaging for lesion detection
    
    Args:
        image_array: Medical image (2D or 3D)
        heatmap: Optional attention heatmap
        axis: Axis along which to project (0=Z, 1=Y, 2=X)
    
    Returns:
        MIP image
    """
    
    if image_array.ndim == 3:
        gray = np.mean(image_array, axis=2)
    else:
        gray = image_array
    
    # Normalize
    if np.max(gray) > 1:
        gray = gray / np.max(gray)
    
    # Create MIP by taking max along axis
    mip_image = np.max(gray, axis=axis)
    
    # Apply heatmap if available
    if heatmap is not None:
        heatmap_mip = np.max(heatmap, axis=axis)
        heatmap_norm = heatmap_mip / (np.max(heatmap_mip) + 1e-8)
        
        # Create RGB with lesion overlay
        rgb_mip = np.stack([mip_image, mip_image, mip_image], axis=2)
        lesion_mask = heatmap_norm > 0.5
        if np.any(lesion_mask):
            rgb_mip[lesion_mask, 0] = np.minimum(rgb_mip[lesion_mask, 0] + 0.5, 1.0)
            rgb_mip[lesion_mask, 1] = np.maximum(rgb_mip[lesion_mask, 1] - 0.2, 0)
            rgb_mip[lesion_mask, 2] = np.maximum(rgb_mip[lesion_mask, 2] - 0.3, 0)
        
        return rgb_mip, heatmap_norm
    else:
        return mip_image, None


def show_pseudo_3d(image_array, heatmap=None, 
                   colorscale="Viridis",
                   show_lesion_overlay=True):
    """
    Main function for enhanced pseudo-3D visualization
    
    Args:
        image_array: 2D or 3D medical image (normalized 0-1)
        heatmap: Optional Grad-CAM or attention heatmap
        colorscale: Plotly colorscale
        show_lesion_overlay: Whether to show AI lesion prediction
    
    Returns:
        Plotly figure
    """
    
    # Ensure proper shape
    if image_array.ndim == 3:
        gray = np.mean(image_array, axis=2)
    else:
        gray = image_array
    
    # Resize heatmap to match image if provided
    heatmap_resized = None
    if heatmap is not None and show_lesion_overlay:
        try:
            height, width = gray.shape
            if heatmap.shape != gray.shape:
                # Resize heatmap to match image dimensions
                heatmap_resized = cv2.resize(heatmap, (width, height))
            else:
                heatmap_resized = heatmap
        except Exception as e:
            print(f"Warning: Could not resize heatmap: {str(e)}")
            heatmap_resized = None
    
    # Create 3D surface with optional lesion overlay
    fig = create_3d_surface_from_image(
        image_array=gray,
        heatmap=heatmap_resized,
        colorscale=colorscale,
        show_lesion=show_lesion_overlay and heatmap_resized is not None
    )
    
    return fig


# Advanced visualization helpers

def create_lesion_statistics(heatmap, lesion_threshold=0.5):
    """
    Calculate lesion statistics from heatmap
    """
    if heatmap is None:
        return None
    
    heatmap_norm = heatmap / (np.max(heatmap) + 1e-8)
    lesion_mask = heatmap_norm > lesion_threshold
    
    stats = {
        "total_pixels": heatmap.size,
        "lesion_pixels": np.sum(lesion_mask),
        "lesion_percentage": (np.sum(lesion_mask) / heatmap.size) * 100,
        "max_intensity": np.max(heatmap_norm),
        "mean_intensity": np.mean(heatmap_norm),
        "std_intensity": np.std(heatmap_norm),
        "centroid": ndimage.center_of_mass(lesion_mask) if np.any(lesion_mask) else None
    }
    
    return stats


def get_lesion_contours(heatmap, threshold=0.5):
    """
    Extract lesion contours using OpenCV
    Useful for clinical annotation
    """
    heatmap_norm = heatmap / (np.max(heatmap) + 1e-8)
    lesion_mask = np.uint8(heatmap_norm > threshold) * 255
    
    contours, _ = cv2.findContours(
        lesion_mask, 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    return contours


def create_lesion_heatmap_figure(image_array, heatmap, 
                                colorscale_heat="RdYlBu_r"):
    """
    Create side-by-side comparison: Original vs Heatmap
    """
    if image_array.ndim == 3:
        gray = np.mean(image_array, axis=2)
    else:
        gray = image_array
    
    if np.max(gray) > 1:
        gray = gray / np.max(gray)
    
    # Normalize heatmap
    heatmap_norm = heatmap / (np.max(heatmap) + 1e-8)
    
    # Create subplots equivalent using multiple traces
    fig = go.Figure()
    
    height, width = gray.shape
    x = np.arange(width)
    y = np.arange(height)
    
    # Original image (left side)
    fig.add_trace(go.Heatmap(
        z=gray,
        x=x,
        y=y,
        colorscale="Gray",
        showscale=False,
        name="Original Image",
        xaxis="x1",
        yaxis="y1",
        hovertemplate="<b>Original</b><br>Intensity: %{z:.2f}<extra></extra>"
    ))
    
    # AI Heatmap (right side)
    fig.add_trace(go.Heatmap(
        z=heatmap_norm,
        x=x + width + 10,
        y=y,
        colorscale=colorscale_heat,
        showscale=True,
        name="AI Prediction",
        xaxis="x2",
        yaxis="y2",
        colorbar=dict(title="Confidence"),
        hovertemplate="<b>AI Prediction</b><br>Confidence: %{z:.2%}<extra></extra>"
    ))
    
    fig.update_layout(
        title="<b>Original Image vs AI Lesion Prediction</b>",
        xaxis=dict(title="Original Image", domain=[0, 0.48]),
        xaxis2=dict(title="AI Prediction", domain=[0.52, 1]),
        yaxis=dict(title=""),
        yaxis2=dict(title=""),
        height=500,
        hovermode="closest",
        margin=dict(l=50, r=50, b=50, t=50)
    )
    
    return fig


if __name__ == "__main__":
    # Test with random data
    test_image = np.random.rand(224, 224)
    test_heatmap = np.random.rand(224, 224)
    
    fig = show_pseudo_3d(test_image, test_heatmap)
    fig.show()