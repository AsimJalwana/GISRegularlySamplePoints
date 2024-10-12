import geopandas as gpd
from shapely.geometry import Point, Polygon
import numpy as np
from pyproj import Transformer

shapefile_path = './data/WA_ShapeFile/WA_Boundary.shp'  # Replace with your actual file path

# Load your GeoDataFrame (assuming it contains a polygon)
gdf = gpd.read_file(shapefile_path)
gdf = gdf.to_crs(epsg=28350)  # UTM zone 50S for WA

# Get the bounds of the geometry (assuming a single polygon)
polygon = gdf.geometry.iloc[0]
minx, miny, maxx, maxy = polygon.bounds

# Define your grid spacing (150 meters)
spacing = 150

# Generate grid points within the bounding box
x_coords = np.arange(minx, maxx, spacing)
y_coords = np.arange(miny, maxy, spacing)

# Set up a transformer for converting projected coordinates back to EPSG:4283 (lat/lon)
transformer = Transformer.from_crs("EPSG:32650", "EPSG:4283", always_xy=True)

grid_points = [Point(x, y) for x in x_coords for y in y_coords]

# Create a GeoDataFrame from the grid points
grid_gdf = gpd.GeoDataFrame(geometry=grid_points, crs=gdf.crs)
grid_gdf.to_crs("EPSG:4283")

# Filter points that are within the polygon
# grid_within_polygon = grid_gdf[grid_gdf.geometry.within(polygon)]

grid_within_polygon = grid_gdf
# Save or plot the points
grid_within_polygon.to_file('grid_points.shp')