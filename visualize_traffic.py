import folium
import pandas as pd
import geopandas as gpd
from shapely import wkt
import os

# Define file paths
roads_csv_path = "warsaw_road_segments.csv"
traffic_csv_path = "simulated_traffic.csv"
output_html_path = "traffic_heatmap.html"

print(f"--- Traffic Visualization Script ---")

# Load road segments
print(f"Loading road segments from '{roads_csv_path}'...")
if not os.path.exists(roads_csv_path):
    print(f"Error: Road segments file not found: '{roads_csv_path}'. Please run previous steps.")
    exit()
roads_df = pd.read_csv(roads_csv_path)
print(f"Loaded {len(roads_df)} road segments.")

# Check for 'segment_id' column, with a fallback if 'u' and 'v' are present
if "segment_id" not in roads_df.columns:
    print(f"Warning: 'segment_id' column not found in '{roads_csv_path}'.")
    if 'u' in roads_df.columns and 'v' in roads_df.columns:
        print("Attempting to create 'segment_id' from 'u' and 'v' columns as a fallback...")
        # Ensure u and v are string type before concatenation
        roads_df["segment_id"] = roads_df["u"].astype(str) + "_" + roads_df["v"].astype(str)
        print("'segment_id' created from 'u' and 'v'.")
    else:
        print(f"Error: Cannot proceed without 'segment_id' or 'u'/'v' columns in '{roads_csv_path}'.")
        exit()
elif 'u' in roads_df.columns and 'v' in roads_df.columns and not roads_df.empty and str(roads_df['segment_id'].iloc[0]) != str(roads_df['u'].iloc[0]) + "_" + str(roads_df['v'].iloc[0]):
    print(f"Using existing 'segment_id' column from '{roads_csv_path}'. Note: 'u' and 'v' columns also exist but 'segment_id' format appears different.")
else:
    print(f"Using existing 'segment_id' column from '{roads_csv_path}'.")


# Load traffic data
print(f"Loading traffic data from '{traffic_csv_path}'...")
if not os.path.exists(traffic_csv_path):
    print(f"Error: Traffic data file not found: '{traffic_csv_path}'. Please run 'simulate_traffic.py'.")
    exit()
traffic_df = pd.read_csv(traffic_csv_path)
print(f"Loaded {len(traffic_df)} total traffic entries.")

# Focus on a specific hour, e.g., 08:00 (Morning Rush Hour)
TARGET_HOUR = "08:00"
print(f"Filtering traffic data for hour: {TARGET_HOUR}...")
traffic_hour_df = traffic_df[traffic_df["hour"] == TARGET_HOUR].copy()

if traffic_hour_df.empty:
    print(f"Warning: No traffic data found for hour {TARGET_HOUR}. The map might not show any colored roads.")
else:
    print(f"Found {len(traffic_hour_df)} traffic entries for hour {TARGET_HOUR}.")

# Restore geometry from WKT strings in roads_df
print("Converting road segment geometries from WKT to Shapely objects...")
if 'geometry' not in roads_df.columns:
    print(f"Error: 'geometry' column not found in '{roads_csv_path}'. This column is essential for visualization.")
    exit()
try:
    roads_df["geometry"] = roads_df["geometry"].apply(wkt.loads)
except Exception as e:
    print(f"Error converting geometry: {e}. Ensure 'geometry' column in '{roads_csv_path}' contains valid WKT strings.")
    exit()

# Create GeoDataFrame from roads_df
roads_gdf = gpd.GeoDataFrame(roads_df, geometry="geometry", crs="EPSG:4326")
print(f"Created GeoDataFrame with {len(roads_gdf)} road segments.")

# Ensure segment_id types are consistent for merging
roads_gdf["segment_id"] = roads_gdf["segment_id"].astype(str)
traffic_hour_df["segment_id"] = traffic_hour_df["segment_id"].astype(str)

# Merge road geometries with traffic data for the specific hour
print(f"Merging road segments with traffic data for {TARGET_HOUR}...")
merged_gdf = roads_gdf.merge(traffic_hour_df, on="segment_id", how="inner")

if merged_gdf.empty:
    print(f"Warning: After merging, no road segments have traffic data for hour {TARGET_HOUR}. The map will be generated but might be empty or lack colored roads.")
else:
    print(f"Successfully merged. Visualizing {len(merged_gdf)} segments with traffic data for {TARGET_HOUR}.")

    # Limit the number of segments to plot for debugging
    MAX_SEGMENTS_TO_PLOT = 500 # You can adjust this number
    if not merged_gdf.empty: # Ensure merged_gdf is not empty before trying to limit
        if len(merged_gdf) > MAX_SEGMENTS_TO_PLOT:
            print(f"        Plotting a subset of {MAX_SEGMENTS_TO_PLOT} (out of {len(merged_gdf)}) segments for performance testing.")
            merged_gdf_to_plot = merged_gdf.head(MAX_SEGMENTS_TO_PLOT).copy() # Use .copy() to avoid SettingWithCopyWarning
        else:
            merged_gdf_to_plot = merged_gdf.copy()
    else:
        merged_gdf_to_plot = merged_gdf.copy() # Still assign to merged_gdf_to_plot if empty

# Initialize a Folium map
print("Initializing Folium map...")
if not merged_gdf.empty and merged_gdf.crs:
    # Use the centroid of the merged data as the map center if data is available
    # Ensure the GeoDataFrame is not empty and has a CRS before accessing unary_union
    try:
        map_center = [merged_gdf.union_all().centroid.y, merged_gdf.union_all().centroid.x]
    except Exception as e:
        print(f"Could not calculate centroid from data ({e}), using default Warsaw center.")
        map_center = [52.2297, 21.0122] # Default Warsaw center
else:
    map_center = [52.2297, 21.0122] # Default Warsaw center

m = folium.Map(location=map_center, zoom_start=12, tiles="OpenStreetMap")

# Function to map speed to color
def get_color(speed_kph):
    if pd.isna(speed_kph):
        return 'grey' # Default color for missing speed data
    if speed_kph < 15: # Heavy traffic
        return 'red'
    elif speed_kph < 30: # Medium traffic
        return 'orange'
    else: # Free-flow or light traffic
        return 'green'

# Add road segments to the map
print("Adding road segments to the map with speed-based coloring...")
for _, row in merged_gdf_to_plot.iterrows():
    if row["geometry"] is None or row["geometry"].is_empty:
        continue
    
    coords = [(lat, lon) for lon, lat in row["geometry"].coords]
    
    road_name_display = row.get("road_name", row.get("name", "Unnamed Road")) 
    if pd.isna(road_name_display):
        road_name_display = "Unnamed Road"

    folium.PolyLine(
        locations=coords,
        color=get_color(row["speed_kph"]),
        weight=3,
        opacity=0.8,
        tooltip=f"Road: {road_name_display}<br>Segment: {row['segment_id']}<br>Speed: {row['speed_kph']:.1f} km/h"
    ).add_to(m)

# Save map to HTML
print(f"Saving map to '{output_html_path}'...")
m.save(output_html_path)
print(f"✅ Map saved as '{output_html_path}'. Open this file in your web browser to view the heatmap.")
print(f"--- Visualization script finished ---")
