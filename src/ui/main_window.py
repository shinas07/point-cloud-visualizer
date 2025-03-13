from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
                           QSlider, QHBoxLayout, QComboBox,
                           QSpinBox, QGroupBox, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt
import open3d as o3d
import numpy as np
from utils.point_cloud_utils import process_point_cloud, create_sample_point_cloud, downsample_point_cloud
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set window properties
        self.setWindowTitle("Point Cloud Viewer")
        self.setGeometry(100, 100, 1000, 800)  # Larger window
        
        # Create main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Status section
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("No point cloud loaded")
        self.points_label = QLabel("Points: 0")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.points_label)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # Visualization controls
        vis_group = QGroupBox("Visualization Controls")
        vis_layout = QVBoxLayout()
        
        # Point size control
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Point Size:"))
        self.point_size_spin = QSpinBox()
        self.point_size_spin.setRange(1, 10)
        self.point_size_spin.setValue(2)
        size_layout.addWidget(self.point_size_spin)
        vis_layout.addLayout(size_layout)
        
        # Color control
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Point Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(["Gold", "Red", "Green", "Blue", "White"])
        color_layout.addWidget(self.color_combo)
        vis_layout.addLayout(color_layout)
        
        vis_group.setLayout(vis_layout)
        main_layout.addWidget(vis_group)
        
        # Processing controls
        proc_group = QGroupBox("Processing")
        proc_layout = QVBoxLayout()
        
        # Downsample control
        down_layout = QHBoxLayout()
        down_layout.addWidget(QLabel("Voxel Size:"))
        self.voxel_size_spin = QSpinBox()
        self.voxel_size_spin.setRange(1, 100)
        self.voxel_size_spin.setValue(10)
        down_layout.addWidget(self.voxel_size_spin)
        proc_layout.addLayout(down_layout)
        
        proc_group.setLayout(proc_layout)
        main_layout.addWidget(proc_group)
        
        # Add measurement controls
        measure_group = QGroupBox("Measurement")
        measure_layout = QVBoxLayout()
        
        self.measure_button = QPushButton("Measure Distance")
        self.measure_button.clicked.connect(self.measure_distance)
        self.measure_button.setEnabled(False)
        
        self.distance_label = QLabel("Distance: N/A")
        
        measure_layout.addWidget(self.measure_button)
        measure_layout.addWidget(self.distance_label)
        measure_group.setLayout(measure_layout)
        main_layout.addWidget(measure_group)
        
        # Buttons section
        button_layout = QHBoxLayout()
        
        # File operations
        self.load_button = QPushButton("Load Point Cloud")
        self.load_button.clicked.connect(self.load_point_cloud)
        button_layout.addWidget(self.load_button)
        
        self.save_button = QPushButton("Save Point Cloud")
        self.save_button.clicked.connect(self.save_point_cloud)
        button_layout.addWidget(self.save_button)
        
        # View operations
        self.view_button = QPushButton("View Point Cloud")
        self.view_button.clicked.connect(self.view_point_cloud)
        button_layout.addWidget(self.view_button)
        
        # Processing operations
        self.process_button = QPushButton("Process Cloud")
        self.process_button.clicked.connect(self.process_cloud)
        button_layout.addWidget(self.process_button)
        
        main_layout.addLayout(button_layout)
        
        # Initialize point cloud
        self.point_cloud = None
        self.update_ui_state()
        
        # Initialize measurement variables
        self.selected_points = []
        self.measuring_mode = False

    def update_ui_state(self):
        """Update UI elements based on point cloud state"""
        has_cloud = self.point_cloud is not None
        self.save_button.setEnabled(has_cloud)
        self.view_button.setEnabled(has_cloud)
        self.process_button.setEnabled(has_cloud)
        self.measure_button.setEnabled(has_cloud)
        if has_cloud:
            self.points_label.setText(f"Points: {len(self.point_cloud.points)}")
        else:
            self.points_label.setText("Points: 0")

    def load_point_cloud(self):
        """Load point cloud from file"""
        try:
            # Add file size check
            if os.path.getsize(file_name) > 100_000_000:  # 100MB
                response = QMessageBox.question(
                    self, 
                    "Large File Warning",
                    "This file is large and might take time to load. Continue?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if response == QMessageBox.No:
                    return
                    
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Open Point Cloud",
                "",
                "Point Cloud Files (*.ply *.pcd);;OBJ Files (*.obj);;All Files (*)"  # Separate filter for OBJ
            )
            
            if file_name:
                try:
                    if file_name.lower().endswith('.obj'):
                        # Load as mesh
                        mesh = o3d.io.read_triangle_mesh(file_name)
                        
                        # Check if mesh is loaded properly
                        if not mesh.has_vertices():
                            raise Exception("No vertices found in OBJ file")
                        
                        # Get user input for number of points
                        num_points = 100000  # Default value
                        try:
                            num_points = QInputDialog.getInt(
                                self,
                                "Sample Points",
                                "Number of points to sample:",
                                value=100000,
                                min=1000,
                                max=1000000,
                                step=1000
                            )[0]
                        except:
                            pass  # Use default if dialog is cancelled
                        
                        # Convert mesh to point cloud
                        self.point_cloud = mesh.sample_points_uniformly(number_of_points=num_points)
                        
                        # Calculate normals for better visualization
                        self.point_cloud.estimate_normals()
                        
                        self.status_label.setText(
                            f"Loaded OBJ mesh and converted to {num_points} points"
                        )
                    else:
                        # Regular point cloud loading
                        self.point_cloud = o3d.io.read_point_cloud(file_name)
                        self.status_label.setText(f"Loaded point cloud: {file_name}")
                    
                    # Update UI
                    self.update_point_cloud_color()
                    self.update_ui_state()
                except Exception as e:
                    self.status_label.setText(f"Error loading file: {str(e)}")

        except MemoryError:
            QMessageBox.critical(
                self,
                "Error",
                "Not enough memory to load this point cloud."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load point cloud: {str(e)}"
            )

    def save_point_cloud(self):
        """Save point cloud to file"""
        if not self.point_cloud:
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Point Cloud",
            "",
            "PLY Files (*.ply);;PCD Files (*.pcd)"
        )
        
        if file_name:
            try:
                o3d.io.write_point_cloud(file_name, self.point_cloud)
                self.status_label.setText(f"Saved to: {file_name}")
            except Exception as e:
                self.status_label.setText(f"Error saving file: {str(e)}")

    def update_point_cloud_color(self):
        """Update point cloud color based on selection"""
        if not self.point_cloud:
            return
            
        color_map = {
            "Gold": [1, 0.706, 0],
            "Red": [1, 0, 0],
            "Green": [0, 1, 0],
            "Blue": [0, 0, 1],
            "White": [1, 1, 1]
        }
        color = color_map[self.color_combo.currentText()]
        self.point_cloud.paint_uniform_color(color)

    def process_cloud(self):
        """Process the point cloud"""
        if not self.point_cloud:
            return
            
        try:
            # Downsample
            voxel_size = self.voxel_size_spin.value() / 100.0  # Convert to meters
            self.point_cloud = downsample_point_cloud(self.point_cloud, voxel_size=voxel_size)
            
            # Basic processing
            self.point_cloud = process_point_cloud(self.point_cloud)
            
            self.update_point_cloud_color()
            self.update_ui_state()
            self.status_label.setText("Processing complete")
        except Exception as e:
            self.status_label.setText(f"Processing error: {str(e)}")

    def measure_distance(self):
        """Toggle measurement mode and calculate distance"""
        if not self.point_cloud:
            return
            
        self.measuring_mode = True
        self.selected_points = []
        self.distance_label.setText("Click two points to measure distance")
        
        # Create visualization window for point selection
        vis = o3d.visualization.VisualizerWithEditing()
        vis.create_window()
        vis.add_geometry(self.point_cloud)
        
        # Run the visualizer and get picked points
        vis.run()  # Wait for user to pick points
        picked_points = vis.get_picked_points()
        vis.destroy_window()
        
        if len(picked_points) >= 2:
            # Get coordinates of first two picked points
            point1 = np.asarray(self.point_cloud.points)[picked_points[0]]
            point2 = np.asarray(self.point_cloud.points)[picked_points[1]]
            
            # Calculate Euclidean distance
            distance = np.linalg.norm(point1 - point2)
            
            # Display result
            self.distance_label.setText(f"Distance: {distance:.3f} units")
        else:
            self.distance_label.setText("Distance: N/A (Need two points)")
        
        self.measuring_mode = False

    def view_point_cloud(self):
        """View the point cloud with current settings"""
        if not self.point_cloud:
            self.status_label.setText("Please load a point cloud first")
            return
            
        if self.measuring_mode:
            return  # Don't open regular viewer in measuring mode
            
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        
        vis.add_geometry(self.point_cloud)
        
        opt = vis.get_render_option()
        opt.point_size = float(self.point_size_spin.value())
        opt.background_color = np.asarray([0.1, 0.1, 0.1])
        
        vis.update_geometry(self.point_cloud)
        vis.poll_events()
        vis.update_renderer()
        
        vis.run()
        vis.destroy_window()