# SmartCity Traffic Flow Optimizer

A Python application for analyzing and optimizing traffic flow in urban environments using OpenStreetMap data.

## Features

- Download and visualize street networks from OpenStreetMap
- Save and load graph data for efficient reuse
- Generate high-quality visualizations of urban road networks

## Installation

1. Clone this repository:
```bash
git clone https://github.com/ManiaSacha/SmartCity-Traffic-Flow-Optimizer.git
cd SmartCity-Traffic-Flow-Optimizer
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install osmnx matplotlib
```

## Usage

Run the map generation script:
```bash
python get_map.py
```

This will:
1. Download the road network for Warsaw, Poland (if not already cached)
2. Save the network data to `warsaw_graph.graphml`
3. Generate and save a visualization to `warsaw_map.png`
4. Display network statistics

## Contact

- GitHub: [ManiaSacha](https://github.com/ManiaSacha)
- LinkedIn: [Manya Sacha](https://www.linkedin.com/in/manya-sacha-apply-ml-engineer/)
- Email: maniasacha.dev@gmail.com
