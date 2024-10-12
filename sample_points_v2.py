import geopandas as gpd
from pyproj import Transformer
from shapely.geometry import Point
from loguru import logger

# Function to sample points in a grid in a projected CRS (meters)
def generate_points(polygon, distance):
    minx, miny, maxx, maxy = polygon.bounds
    points = []
    x = minx
    count = 1
    points_count = 0
    while x <= maxx:
        y = miny
        while y <= maxy:
            print(f"Iteration : {count}")
            count += 1
            point = Point(x, y)
            if polygon.contains(point):
                points.append(point)
                points_count += 1

            if points_count > 10:
                break

            y += distance
        x += distance
    return points

# Load the shapefile (EPSG:4283)
shapefile_path = './data/WA_ShapeFile/WA_Boundary.shp'  # Replace with your actual file path
gdf = gpd.read_file(shapefile_path)

# Reproject the polygon to a UTM zone for Western Australia (EPSG:32650)
gdf_projected = gdf.to_crs(epsg=32650)  # UTM zone 50S for WA

# Get the projected polygon (assuming one polygon, otherwise loop over geometries)
polygon_projected = gdf_projected.geometry[0]

# Generate points 150 meters apart in the projected CRS
points_projected = generate_points(polygon_projected, distance=5000)

# Set up a transformer for converting projected coordinates back to EPSG:4283 (lat/lon)
transformer = Transformer.from_crs("EPSG:32650", "EPSG:4283", always_xy=True)

# Transform points back to lat/lon in EPSG:4283
lat_lon_points = [Point(transformer.transform(point.x, point.y)) for point in points_projected]

# Create a GeoDataFrame with the points in EPSG:4283
points_gdf = gpd.GeoDataFrame(geometry=lat_lon_points, crs="EPSG:4283")

# Save to GeoJSON
output_geojson = 'sampled_points.geojson'
points_gdf.to_file(output_geojson, driver='GeoJSON')
points_gdf.to_file('sampled_points.shp')

print(f"Saved {len(points_projected)} points to {output_geojson}")
