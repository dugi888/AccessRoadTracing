import laspy

def laz_to_las_laspy(input_laz: str, output_las: str):
    """
    Convert LAZ to LAS using laspy
    Requires: pip install laspy[lazrs]
    """
    # Read LAZ with specified backend
    las = laspy.read(input_laz, laz_backend=laspy.LazBackend.Lazrs)
    
    # Write LAS (uncompressed)
    las.write(output_las)

# Usage
laz_to_las_laspy("GK_465_135.laz", "lasData/GK_465_135.las")