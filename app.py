import streamlit as st
import pandas as pd
import joblib
import os

# --- Configuration & Constants ---
MODEL_PATH = "traffic_speed_model.pkl"
ENCODER_PATH = "segment_encoder.pkl"
SEGMENTS_CSV_PATH = "warsaw_road_segments.csv"

st.set_page_config(page_title="Warsaw Traffic Predictor", layout="centered", initial_sidebar_state="auto")

# --- Load Data and Models (with caching) ---
@st.cache_resource # Updated from st.cache to st.cache_resource for Streamlit 1.18+
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

@st.cache_data # Updated from st.cache to st.cache_data for Streamlit 1.18+
def load_segment_data():
    if not os.path.exists(SEGMENTS_CSV_PATH):
        st.error(f"Road segments file ('{SEGMENTS_CSV_PATH}') not found. Please run 'extract_segments.py'.")
        return pd.DataFrame()
    try:
        segments_df = pd.read_csv(SEGMENTS_CSV_PATH)
        # Ensure segment_id exists, create if necessary (fallback)
        if "segment_id" not in segments_df.columns:
            if 'u' in segments_df.columns and 'v' in segments_df.columns:
                segments_df["segment_id"] = segments_df["u"].astype(str) + "_" + segments_df["v"].astype(str)
            else:
                st.error("Cannot create 'segment_id'. 'u' and 'v' columns are missing.")
                return pd.DataFrame()
        
        # Filter for named segments and create a display name if needed
        named_segments = segments_df[segments_df["name"].notna()].copy() # Use .copy() to avoid SettingWithCopyWarning
        named_segments.loc[:, "display_name"] = named_segments["name"] + " (" + named_segments["segment_id"] + ")"
        return named_segments[["segment_id", "name", "display_name"]].drop_duplicates().sort_values(by="name")
    except Exception as e:
        st.error(f"Error loading or processing segment data: {e}")
        return pd.DataFrame()

model, segment_encoder = load_model_and_encoder()
segments = load_segment_data()

# --- Streamlit UI ---
st.title("🚦 SmartCity Traffic Flow Predictor")
st.markdown("Predict traffic speed (km/h) for a selected road segment in Warsaw at a specific time of day.")

if model is None or segment_encoder is None or segments.empty:
    st.warning("Application cannot start due to missing data or model. Please check error messages above.")
else:
    st.sidebar.header("Prediction Inputs")
    
    # Dropdown for road name - use display_name for better UX
    # Create a mapping from display_name to segment_id for easier lookup
    display_name_to_id = pd.Series(segments.segment_id.values, index=segments.display_name).to_dict()
    
    selected_display_name = st.sidebar.selectbox(
        "📍 Choose a Road Segment (Name + ID)", 
        options=segments["display_name"].unique(),
        help="Select a road segment. The ID is shown in parentheses."
    )
    
    selected_segment_id = display_name_to_id.get(selected_display_name)

    # Time selector
    hour = st.sidebar.slider("🕒 Select Hour of Day (0-23)", 0, 23, 8, help="0 = midnight, 12 = noon, 23 = 11 PM")

    # Prediction button
    if st.sidebar.button("🔮 Predict Traffic Speed", type="primary"):
        if selected_segment_id:
            try:
                # Ensure the segment_id is known to the encoder
                if selected_segment_id not in segment_encoder.classes_:
                    st.error(f"Segment ID '{selected_segment_id}' was not seen during model training. Cannot make a prediction.")
                else:
                    segment_encoded = segment_encoder.transform([selected_segment_id])[0]
                    input_features = [[segment_encoded, hour]]
                    
                    predicted_speed = model.predict(input_features)[0]
                    
                    st.metric(label=f"Predicted Speed for '{selected_display_name}' at {hour:02d}:00", 
                              value=f"{predicted_speed:.1f} km/h")
                    
                    # Simple interpretation
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
        st.info("Adjust the inputs in the sidebar and click 'Predict Traffic Speed'.")

st.sidebar.markdown("---")
st.sidebar.markdown("**Project Steps:**")
st.sidebar.markdown("1. Get Map Data ✅\n2. Extract Segments ✅\n3. Simulate Traffic ✅\n4. Visualize Heatmap ✅\n5. Train ML Model ✅\n6. **Prediction Dashboard (You are here!)**")

# Add a small section about the data
st.markdown("---")
st.subheader("About the Data")
st.markdown("The model was trained on simulated traffic data for Warsaw. Road segment data is from OpenStreetMap.")

if st.checkbox("Show sample of available road segments (first 100)"):
    st.dataframe(segments[['name', 'segment_id']].head(100))
