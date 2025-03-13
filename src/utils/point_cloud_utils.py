import open3d as o3d
import numpy as np
import os

def process_point_cloud(point_cloud):
    """
    Basic point cloud processing - just estimates normals for better visualization
    
    Args:
        point_cloud: Input point cloud
    
    Returns:
        Processed point cloud
    """
    try:
        # Estimate normals for better visualization
        point_cloud.estimate_normals()
        return point_cloud
    except Exception as e:
        print(f"Error processing point cloud: {str(e)}")
        return point_cloud

def create_sample_point_cloud(shape="sphere", num_points=2000, color=[1, 0.706, 0]):
    """
    Create a sample point cloud for testing
    
    Args:
        shape: Shape of sample ("sphere" or "cube")
        num_points: Number of points to generate
        color: RGB color for points [r, g, b]
    
    Returns:
        Sample point cloud
    """
    try:
        if shape == "sphere":
            mesh = o3d.geometry.TriangleMesh.create_sphere(radius=1.0)
        else:  # cube
            mesh = o3d.geometry.TriangleMesh.create_box(width=1.0, height=1.0, depth=1.0)
            
        point_cloud = mesh.sample_points_uniformly(number_of_points=num_points)
        point_cloud.paint_uniform_color(color)
        
        return point_cloud
    except Exception as e:
        print(f"Error creating sample: {str(e)}")
        return None

def visualize_point_cloud(point_cloud, point_size=2.0, background_color=[0.1, 0.1, 0.1]):
    """
    Visualize point cloud with custom settings
    
    Args:
        point_cloud: Point cloud to visualize
        point_size: Size of points in visualization
        background_color: RGB color for background
    """
    if point_cloud is None:
        print("No point cloud to visualize")
        return
        
    try:
        # Create visualizer
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        
        # Add point cloud and configure view
        vis.add_geometry(point_cloud)
        
        # Get render options and modify them
        opt = vis.get_render_option()
        opt.point_size = float(point_size)
        opt.background_color = np.asarray(background_color)
        
        # Update view
        vis.update_geometry(point_cloud)
        vis.poll_events()
        vis.update_renderer()
        
        # Run visualizer
        vis.run()
        vis.destroy_window()
    except Exception as e:
        print(f"Error in visualization: {str(e)}")

def downsample_point_cloud(point_cloud, voxel_size=0.05):
    """
    Downsample point cloud using voxel grid
    
    Args:
        point_cloud: Input point cloud
        voxel_size: Size of voxel grid for downsampling
    
    Returns:
        Downsampled point cloud
    """
    try:
        return point_cloud.voxel_down_sample(voxel_size=voxel_size)
    except Exception as e:
        print(f"Error in downsampling: {str(e)}")
        return point_cloud

def load_3d_file(file_path):
    """
    Load 3D file (OBJ, PLY, PCD) and convert to point cloud if needed
    
    Args:
        file_path: Path to 3D file
    Returns:
        point_cloud: Open3D point cloud object
    """
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.obj':
            # Load as mesh and convert to point cloud
            mesh = o3d.io.read_triangle_mesh(file_path)
            point_cloud = mesh.sample_points_uniformly(number_of_points=10000)
        elif file_extension in ['.ply', '.pcd']:
                # Direct point cloud loading
            point_cloud = o3d.io.read_point_cloud(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
            
        # Add default color if none exists
        if not point_cloud.has_colors():
            point_cloud.paint_uniform_color([1, 0.706, 0])  # Default gold color
            
        return point_cloud
        
    except Exception as e:
        print(f"Error loading file: {str(e)}")
        return None

def save_3d_file(point_cloud, file_path):
    """
    Save point cloud to file
    
    Args:
        point_cloud: Open3D point cloud object
        file_path: Path to save file
    """
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.obj':
            # Convert point cloud to mesh for OBJ saving
            mesh = o3d.geometry.TriangleMesh()
            mesh.vertices = o3d.utility.Vector3dVector(np.asarray(point_cloud.points))
            o3d.io.write_triangle_mesh(file_path, mesh)
        else:
            # Direct point cloud saving
            o3d.io.write_point_cloud(file_path, point_cloud)
            
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        raise e
