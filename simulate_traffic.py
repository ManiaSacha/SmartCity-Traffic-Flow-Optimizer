import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Load road segments
segments_df = pd.read_csv("warsaw_road_segments.csv")

# Define 24 hours
hours = [f"{h:02d}:00" for h in range(24)]

def simulate_speed(hour):
    """Return simulated speed (km/h) based on time of day."""
    h = int(hour.split(":")[0])
    if 7 <= h <= 9 or 16 <= h <= 18:
        return np.random.normal(18, 5)  # Rush hour
    elif 10 <= h <= 15:
        return np.random.normal(30, 7)
    elif 19 <= h <= 22:
        return np.random.normal(40, 5)
    else:
        return np.random.normal(50, 5)  # Night

# Create traffic data per road segment per hour
traffic_data = []

print(f"Generating traffic data for {len(segments_df)} road segments across 24 hours...")

for idx, row in segments_df.iterrows():
    segment_id = row["segment_id"]
    road_name = row["name"] if pd.notna(row["name"]) else "Unnamed Road"
    
    for hour in hours:
        speed = max(5, simulate_speed(hour))  # Avoid negative/very low speeds
        traffic_data.append({
            "segment_id": segment_id,
            "road_name": road_name,
            "hour": hour,
            "speed_kph": round(speed, 1)
        })
    
    # Print progress every 1000 segments
    if idx % 1000 == 0 and idx > 0:
        print(f"Processed {idx}/{len(segments_df)} segments...")

# Save to CSV
traffic_df = pd.DataFrame(traffic_data)
traffic_df.to_csv("simulated_traffic.csv", index=False)

print("\nData sample:")
print(traffic_df.head(10))

print(f"\n✅ Simulated traffic data for {len(traffic_df)} entries.")
print(f"Data saved to simulated_traffic.csv")
