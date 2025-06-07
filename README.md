# SmartCity Traffic Flow Optimizer & Predictor 🚦🏙️

![Project Logo](logo/project_logo.png)

A Python-based application to download, analyze, simulate, and predict urban traffic flow, demonstrated with data from Warsaw, Poland. This project showcases data processing, machine learning, and interactive visualization techniques for smart city applications.

## 🌟 Key Features

- **Street Network Analysis:** Downloads and processes road network data from OpenStreetMap using OSMnx.
- **Road Segment Extraction:** Identifies and extracts individual road segments with detailed attributes (name, length, geometry).
- **Traffic Simulation:** Generates realistic hourly traffic speed data for each road segment based on typical daily patterns (rush hours, off-peak, night).
- **Machine Learning Prediction:** Trains a Random Forest Regressor model to predict traffic speed on a given road segment at a specific hour.
- **Interactive Dashboard:** A Streamlit web application allowing users to:
    - Select a road segment in Warsaw.
    - Choose an hour of the day.
    - Get a live traffic speed prediction from the trained ML model.
    - View the selected road segment on an interactive Folium map, colored by its predicted traffic speed (red/orange/green).
- **Data Visualization:**
    - Static plot of the entire city road network.
    - Static HTML heatmap of simulated traffic conditions across the city for a chosen hour.

## 📸 Visualizations & Dashboard Preview

![Project Showcase GIF](logo/Traffic%20Flow%20Optimizer.gif)

*(Consider adding screenshots here to showcase your project!)*

1.  **Warsaw Road Network Plot:**
    `[Insert screenshot of warsaw_map.png here]`

2.  **Simulated Traffic Heatmap (Folium):**
    `[Insert screenshot of traffic_heatmap.html here]`

3.  **Interactive Streamlit Dashboard:**
    `[Insert screenshot(s) of the Streamlit app (app.py) in action, showing prediction and map visualization here]`

## 🛠️ Technologies Used

- **Python 3.10+**
- **Core Libraries:**
    - **OSMnx:** For street network data acquisition and analysis from OpenStreetMap.
    - **Pandas & GeoPandas:** For data manipulation and geospatial operations.
    - **NumPy:** For numerical computations.
    - **Shapely:** For geometric operations.
- **Machine Learning:**
    - **Scikit-learn:** For training the Random Forest Regressor model and data preprocessing.
    - **Joblib:** For saving and loading the trained ML model.
- **Visualization & Dashboard:**
    - **Matplotlib:** For static plots of the road network.
    - **Folium:** For creating interactive geographic maps (heatmaps and segment visualization).
    - **Streamlit:** For building the interactive web dashboard.
    - **streamlit-folium:** For embedding Folium maps in Streamlit.
- **Development Environment:** Virtual environment (`venv`).

## 📂 Project Structure

```
SmartCity-Traffic-Flow-Optimizer/
├── .git/                     # Git repository files
├── .gitignore                # Specifies intentionally untracked files that Git should ignore
├── venv/                     # Python virtual environment (if created locally)
├── data/                     # (Implicitly created by scripts for caching OSMnx data)
├── doc/
│   └── project_documentation.md # Detailed project documentation
├── app.py                    # Main Streamlit dashboard application
├── extract_segments.py       # Extracts road segments from the downloaded graph
├── get_map.py                # Downloads and saves the city's road network graph
├── requirements.txt          # Python package dependencies
├── simulate_traffic.py       # Simulates hourly traffic data for road segments
├── train_predict_model.py    # Trains the traffic prediction ML model
├── visualize_traffic.py      # Generates a Folium heatmap of simulated traffic
├── warsaw_graph.graphml      # Saved road network graph for Warsaw
├── warsaw_road_segments.csv  # CSV of extracted road segments
├── simulated_traffic.csv     # CSV of simulated hourly traffic speeds
├── traffic_speed_model.pkl   # Saved trained ML model
├── segment_encoder.pkl       # Saved segment ID encoder for the ML model
├── warsaw_map.png            # Output image of the Warsaw road network
└── traffic_heatmap.html      # Output HTML file for the traffic heatmap
```

## ⚙️ Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/ManiaSacha/SmartCity-Traffic-Flow-Optimizer.git
    cd SmartCity-Traffic-Flow-Optimizer
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    # source venv/bin/activate
    ```

3.  **Install Dependencies:**
    Ensure your `pip` is up-to-date, then install packages from `requirements.txt`:
    ```bash
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```
    *Note: If you encounter issues with GeoPandas or its dependencies (like Fiona, GDAL, PyProj), you might need to install them using alternative methods such as Conda or by downloading pre-compiled wheels specific to your OS and Python version. Refer to the official GeoPandas installation guide.* 

## 🚀 Running the Project

### 1. Data Preparation & Model Training (One-time or when data changes)

While the Streamlit app uses pre-generated data and a pre-trained model included in this general structure, you can regenerate them by running the scripts in the following order:

1.  **Download Map Data:**
    ```bash
    python get_map.py
    ```
    This downloads the Warsaw road network and saves `warsaw_graph.graphml` and `warsaw_map.png`.

2.  **Extract Road Segments:**
    ```bash
    python extract_segments.py
    ```
    This processes `warsaw_graph.graphml` and creates `warsaw_road_segments.csv`.

3.  **Simulate Traffic Data:**
    ```bash
    python simulate_traffic.py
    ```
    This uses `warsaw_road_segments.csv` to generate `simulated_traffic.csv`.

4.  **Train the ML Model:**
    ```bash
    python train_predict_model.py
    ```
    This uses `simulated_traffic.csv` to train a model and saves `traffic_speed_model.pkl` and `segment_encoder.pkl`.

5.  **(Optional) Generate Static Heatmap:**
    ```bash
    python visualize_traffic.py
    ```
    This creates `traffic_heatmap.html` based on `warsaw_road_segments.csv` and `simulated_traffic.csv`.

### 2. Launch the Interactive Dashboard

To run the main application:

```bash
streamlit run app.py
```

This will start the Streamlit server, and you can access the dashboard in your web browser (typically at `http://localhost:8501`).

## 🔮 Future Enhancements

- Integrate real-time traffic data APIs.
- Implement more advanced time-series forecasting models (e.g., LSTM, ARIMA).
- Allow users to draw custom routes and get aggregate traffic predictions.
- Add options for historical data analysis and trend visualization.
- Deploy the Streamlit application to a cloud platform.

## 📞 Contact

- **Manya Sacha**
- GitHub: [ManiaSacha](https://github.com/ManiaSacha)
- LinkedIn: [Manya Sacha](https://www.linkedin.com/in/manya-sacha-apply-ml-engineer/)
- Email: maniasacha.dev@gmail.com
