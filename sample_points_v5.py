import geopandas as gpd
from shapely.geometry import Point
import numpy as np
from pyproj import Transformer
import pygeos

shapefile_path = './data/WA_ShapeFile/WA_Boundary.shp'  # Replace with your actual file path

# Load GeoDataFrame and reproject to UTM Zone 50S (EPSG:28350)
gdf = gpd.read_file(shapefile_path)
gdf = gdf.to_crs(epsg=28350)

# Get the first polygon geometry
polygon = gdf.geometry.iloc[0]

# Extract polygon bounds
minx, miny, maxx, maxy = polygon.bounds

# Define grid spacing (150 meters)
spacing = 150

# Generate grid points within the bounding box using numpy's meshgrid for efficiency
x_coords = np.arange(minx, maxx, spacing)
y_coords = np.arange(miny, maxy, spacing)
xv, yv = np.meshgrid(x_coords, y_coords)

# Convert the meshgrid to a flattened array of points
grid_points = np.column_stack([xv.ravel(), yv.ravel()])

# Create a GeoSeries from the grid points directly
grid_gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy(grid_points[:, 0], grid_points[:, 1]), crs=gdf.crs)

# Use spatial index to efficiently filter points within the polygon
sindex = gdf.sindex  # Spatial index for the polygon
possible_matches_index = list(sindex.intersection(polygon.bounds))
possible_matches = gdf.iloc[possible_matches_index]

# Final filtering: check if points are within the polygon
grid_within_polygon = grid_gdf[grid_gdf.geometry.within(polygon)]

# Optionally transform the result to EPSG:4283 (latitude/longitude)
grid_within_polygon = grid_within_polygon.to_crs("EPSG:4283")

# Save the result to a shapefile
grid_within_polygon.to_file('grid_points_optimized.shp')
