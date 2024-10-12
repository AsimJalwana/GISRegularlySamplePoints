import geopandas as gpd
from pyproj import Transformer
from shapely.geometry import Point
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# Function to sample points in a grid in a projected CRS (meters)
def generate_points_chunk(x_range, polygon, distance):
    print(f"{x_range}")
    points = []
    for x in x_range:
        y = polygon.bounds[1]  # miny
        while y <= polygon.bounds[3]:  # maxy
            point = Point(x, y)
            if polygon.contains(point):
                points.append(point)
            y += distance
    return points

# Function to generate points in parallel
def generate_points_parallel(polygon, distance, num_workers=4):
    minx, miny, maxx, maxy = polygon.bounds
    x_values = np.arange(minx, maxx, distance)

    # Split the x-axis range into chunks for parallel processing
    chunk_size = len(x_values) // num_workers
    x_chunks = [x_values[i:i + chunk_size] for i in range(0, len(x_values), chunk_size)]

    points = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit tasks to process each chunk of x-values
        results = executor.map(lambda chunk: generate_points_chunk(chunk, polygon, distance), x_chunks)

        # Combine results from all workers
        for result in results:
            points.extend(result)

    return points

# Load the shapefile (EPSG:4283)
shapefile_path = './data/WA_ShapeFile/WA_Boundary.shp'  # Replace with your actual file path
gdf = gpd.read_file(shapefile_path)

# Reproject the polygon to a projected CRS (e.g., EPSG:3857 or suitable UTM zone for your area)
gdf_projected = gdf.to_crs(epsg=32650)  # UTM zone 50S for WA

# Get the projected polygon (assuming one polygon, otherwise loop over geometries)
polygon_projected = gdf_projected.geometry[0]

# Generate points 5000 meters apart in the projected CRS using parallel processing
points_projected = generate_points_parallel(polygon_projected, distance=5000, num_workers=10)

# Set up a transformer for converting projected coordinates back to EPSG:4283 (lat/lon)
transformer = Transformer.from_crs("EPSG:32650", "EPSG:4283", always_xy=True)

# Transform points back to lat/lon in EPSG:4283
lat_lon_points = [Point(transformer.transform(point.x, point.y)) for point in points_projected]

# Create a GeoDataFrame with the points in EPSG:4283
points_gdf = gpd.GeoDataFrame(geometry=lat_lon_points, crs="EPSG:4283")

# Save to GeoJSON
output_geojson = 'sampled_points_parallel.geojson'
points_gdf.to_file(output_geojson, driver='GeoJSON')
points_gdf.to_file('sampled_points_parallel.shp')

print(f"Saved {len(points_projected)} points to {output_geojson}")
