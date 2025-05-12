import laspy
import numpy as np

# Read input files
las1 = laspy.read("GK_465_135.laz", laz_backend=laspy.LazBackend.Lazrs)
las2 = laspy.read("GK_465_136.laz", laz_backend=laspy.LazBackend.Lazrs)

# Verify compatibility (critical for Slovenian data)
# assert las1.header.point_format == las2.header.point_format, "Point formats differ!"
# assert las1.header.scales == las2.header.scales, "Scaling factors differ!"
# assert las1.header.offsets == las2.header.offsets, "Offsets differ!"

# Combine points
merged_points = np.concatenate([las1.points, las2.points])

# Create new header
merged_header = las1.header.copy()
merged_header.point_count = len(merged_points)

# Write merged file
merged_las = laspy.LasData(merged_header, points=merged_points)
merged_las.write("merged_output.laz", laz_backend=laspy.LazBackend.Lazrs)