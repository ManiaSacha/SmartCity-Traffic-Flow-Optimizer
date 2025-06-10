import streamlit as st
import pandas as pd
import joblib
import folium
from streamlit_folium import st_folium # Ensure this is st_folium, not folium_static
from shapely import wkt
import os

# --- Configuration & Constants ---
MODEL_PATH = "traffic_speed_model.pkl"
ENCODER_PATH = "segment_encoder.pkl"
SEGMENTS_CSV_PATH = "warsaw_road_segments.csv"

st.set_page_config(page_title="Warsaw Traffic Predictor & Map", layout="wide", initial_sidebar_state="expanded")

# --- App Title and Logo --- 
LOGO_PATH = "logo/SmartCity Traffic Flow Optimizer.png"

header_col1, header_col2 = st.columns([1, 4]) 
with header_col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=100) 
    else:
        st.warning(f"Logo not found at {LOGO_PATH}")

with header_col2:
    st.title("🚦 SmartCity Traffic Flow Predictor + Map")
    st.markdown("Select a road segment and time to predict traffic speed and visualize it on an interactive map.")

# --- Loading Data and Models (with caching) ---
@st.cache_resource
def load_model_and_encoder():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODER_PATH):
        st.error(f"Model ('{MODEL_PATH}') or encoder ('{ENCODER_PATH}') not found. Please run the training script first.")
        return None, None
    try:
        model = joblib.load(MODEL_PATH)
        segment_encoder = joblib.load(ENCODER_PATH)
        return model, segment_encoder
    except Exception as e:
        st.error(f"Error loading model/encoder: {e}")
        return None, None

@st.cache_data
def load_segment_data():
    if not os.path.exists(SEGMENTS_CSV_PATH):
        st.error(f"Road segments file ('{SEGMENTS_CSV_PATH}') not found. Please run 'extract_segments.py'.")
        return pd.DataFrame()
    try:
        segments_df = pd.read_csv(SEGMENTS_CSV_PATH)
        if "segment_id" not in segments_df.columns:
            if 'u' in segments_df.columns and 'v' in segments_df.columns:
                segments_df["segment_id"] = segments_df["u"].astype(str) + "_" + segments_df["v"].astype(str)
            else:
                st.error("Cannot create 'segment_id'. 'u' and 'v' columns are missing.")
                return pd.DataFrame()
        
        # Converting WKT geometry to Shapely objects
        segments_df["geometry_obj"] = segments_df["geometry"].apply(wkt.loads)
        
        named_segments = segments_df[segments_df["name"].notna()].copy()
        named_segments.loc[:, "display_name"] = named_segments["name"] + " (" + named_segments["segment_id"] + ")"
        return named_segments[["segment_id", "name", "display_name", "geometry_obj"]].drop_duplicates(subset=["segment_id"]).sort_values(by="name")
    except Exception as e:
        st.error(f"Error loading or processing segment data: {e}")
        return pd.DataFrame()

model, segment_encoder = load_model_and_encoder()
segments_with_geo = load_segment_data()

# --- Streamlit UI ---
if model is None or segment_encoder is None or segments_with_geo.empty:
    st.warning("Application cannot start due to missing data or model. Please check error messages above.")
else:
    col1, col2 = st.columns([1, 2]) # Sidebar-like column for inputs, main column for map/results

    with col1:
        st.header("Prediction Inputs")
        display_name_to_id = pd.Series(segments_with_geo.segment_id.values, index=segments_with_geo.display_name).to_dict()
        
        selected_display_name = st.selectbox(
            "📍 Choose a Road Segment (Name + ID)", 
            options=segments_with_geo["display_name"].unique(),
            help="Select a road segment. The ID is shown in parentheses."
        )
        selected_segment_id = display_name_to_id.get(selected_display_name)
        hour = st.slider("🕒 Select Hour of Day (0-23)", 0, 23, 8, help="0 = midnight, 12 = noon, 23 = 11 PM")

        if st.button("🔮 Predict and Show on Map", type="primary"):
            if selected_segment_id:
                try:
                    if selected_segment_id not in segment_encoder.classes_:
                        st.error(f"Segment ID '{selected_segment_id}' was not seen during model training. Cannot make a prediction.")
                    else:
                        segment_encoded_val = segment_encoder.transform([selected_segment_id])[0]
                        input_features = [[segment_encoded_val, hour]]
                        predicted_speed = model.predict(input_features)[0]
                        
                        st.metric(label=f"Predicted Speed for '{selected_display_name}' at {hour:02d}:00", 
                                  value=f"{predicted_speed:.1f} km/h")
                        
                        # Store prediction and segment info for map display in col2
                        st.session_state.predicted_speed = predicted_speed
                        st.session_state.selected_segment_id = selected_segment_id
                        st.session_state.selected_display_name = selected_display_name
                        st.session_state.hour = hour

                        if predicted_speed < 15:
                            st.error("Heavy traffic expected.")
                        elif predicted_speed < 30:
                            st.warning("Moderate traffic expected.")
                        else:
                            st.success("Light traffic / Free flow expected.")
                            
                except Exception as e:
                    st.error(f"Error during prediction: {e}")
            else:
                st.error("Please select a valid road segment.")
        else:
            st.info("Adjust inputs and click 'Predict and Show on Map'.")

        st.markdown("---")
        st.subheader("About the Data")
        st.markdown("Model trained on simulated Warsaw traffic. Road data from OpenStreetMap.")
        if st.checkbox("Show sample of available road segments (first 10)"):
            st.dataframe(segments_with_geo[['name', 'segment_id']].head(10))

    with col2:
        st.header("📍 Traffic Map")
        if 'predicted_speed' in st.session_state and 'selected_segment_id' in st.session_state:
            current_speed = st.session_state.predicted_speed
            current_segment_id = st.session_state.selected_segment_id
            current_display_name = st.session_state.selected_display_name
            current_hour = st.session_state.hour

            segment_row = segments_with_geo[segments_with_geo["segment_id"] == current_segment_id].iloc[0]
            segment_geometry = segment_row["geometry_obj"]
            
            # Ensure coords are in (lat, lon) for Folium
            if segment_geometry.geom_type == 'LineString':
                coords = [(lat, lon) for lon, lat in segment_geometry.coords]
            elif segment_geometry.geom_type == 'MultiLineString': # Handle MultiLineString if present
                all_coords = []
                for line in segment_geometry.geoms:
                    all_coords.extend([(lat, lon) for lon, lat in line.coords])
                coords = all_coords # Folium PolyLine can take a list of lists for MultiLineString parts
            else:
                st.error(f"Unsupported geometry type: {segment_geometry.geom_type}")
                coords = []

            def get_color(speed):
                if speed < 15:
                    return "red"
                elif speed < 30:
                    return "orange"
                else:
                    return "green"

            if coords:
                center_latlon = coords[len(coords)//2]
                m = folium.Map(location=center_latlon, zoom_start=15, tiles="cartodbpositron")
                folium.PolyLine(
                    locations=coords,
                    color=get_color(current_speed),
                    weight=7,
                    opacity=0.8,
                    tooltip=f"{current_display_name}<br>Hour: {current_hour:02d}:00<br>Speed: {current_speed:.1f} km/h"
                ).add_to(m)
                
                # Display map
                st_folium(m, width=700, height=500, key=f"map_{current_segment_id}_{current_hour}") # Add key to force rerender
            else:
                st.write("No coordinates to display for this segment.")
        else:
            st.info("Click 'Predict and Show on Map' to see the visualization here.")

