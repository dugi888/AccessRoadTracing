import laspy
import numpy as np
import pyvista as pv


# Read LAZ file (requires LASzip backend)
las = laspy.read("GK_403_39.laz")

# Get coordinates and classifications
xyz = np.vstack([las.x, las.y, las.z]).transpose()
colors = np.vstack([las.red, las.green, las.blue]).transpose()  # if RGB data exists
classification = las.classification  # ground vs vegetation




# Downsample for better performance (keep 10% of points)
downsampled = xyz[::10]

# Create point cloud
cloud = pv.PolyData(downsampled)
cloud["elevation"] = downsampled[:,2]

# Create plotter
plotter = pv.Plotter()
plotter.add_mesh(cloud, point_size=2, scalars="elevation")
plotter.show_axes()
plotter.show()