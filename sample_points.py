import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from pyproj import Transformer

# Function to sample points in a grid in a projected CRS (meters)
def generate_points(polygon, distance):
    minx, miny, maxx, maxy = polygon.bounds
    points = []
    x = minx
    while x <= maxx:
        y = miny
        while y <= maxy:
            point = Point(x, y)
            if polygon.contains(point):
                points.append(point)
            y += distance
        x += distance
    return points

# Load the shapefile (EPSG:4283)
shapefile_path = '/Users/jalwana/GIS/WA_ShapeFile/WA_Boundary.shp'  # Replace with your actual file path
gdf = gpd.read_file(shapefile_path)

# Reproject the polygon to a projected CRS (e.g., EPSG:3857 or suitable UTM zone for your area)
gdf_projected = gdf.to_crs(epsg=3857)  # EPSG:3857 is a global projected CRS in meters

# Get the projected polygon (assuming one polygon, otherwise loop over geometries)
polygon_projected = gdf_projected.geometry[0]

# Generate points 150 meters apart in the projected CRS
points_projected = generate_points(polygon_projected, 150)

# Set up a transformer for converting projected coordinates back to EPSG:4283 (lat/lon)
transformer = Transformer.from_crs("EPSG:3857", "EPSG:4283", always_xy=True)

# Transform points back to lat/lon in EPSG:4283
lat_lon_points = [Point(transformer.transform(point.x, point.y)) for point in points_projected]

# Create a GeoDataFrame with the points in EPSG:4283
points_gdf = gpd.GeoDataFrame(geometry=lat_lon_points, crs="EPSG:4283")

# Save to GeoJSON
output_geojson = 'sampled_points.geojson'
points_gdf.to_file(output_geojson, driver='GeoJSON')

print(f"Saved {len(points_projected)} points to {output_geojson}")
