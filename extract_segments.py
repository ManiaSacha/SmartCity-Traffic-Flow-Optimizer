import osmnx as ox
import pandas as pd
import os
import time

try:
    # Define file paths
    graph_filepath = 'warsaw_graph.graphml'
    segments_filepath = 'warsaw_road_segments.csv'
    named_segments_filepath = 'warsaw_named_road_segments.csv'
    
    start_time = time.time()
    
    # Check if the saved graph exists, otherwise download it
    if os.path.exists(graph_filepath):
        print(f"Loading graph from {graph_filepath}...")
        G = ox.load_graphml(graph_filepath)
    else:
        print(f"Downloading road network for Warsaw, Poland...")
        city = "Warsaw, Poland"
        G = ox.graph_from_place(city, network_type='drive')
        
        # Save the graph to disk for future use
        print(f"Saving graph to {graph_filepath}...")
        ox.save_graphml(G, graph_filepath)
    
    # Convert the graph into a GeoDataFrame of edges (i.e., road segments)
    print("Converting graph to GeoDataFrame...")
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
    print(f"Graph has {len(gdf_nodes)} nodes and {len(gdf_edges)} edges")
    
    # Print column names to debug
    print("Available columns in the edges GeoDataFrame:")
    print(gdf_edges.columns.tolist())
    
    # Extract useful columns (use only columns that exist)
    print("Extracting road segment data...")
    # Start with just the geometry and name columns which should always exist
    columns_to_extract = ["geometry", "name"]
    
    # Check if other desired columns exist and add them if they do
    if "length" in gdf_edges.columns:
        columns_to_extract.append("length")
    else:
        # Calculate length if not present
        print("Length column not found, calculating lengths...")
        gdf_edges["length"] = gdf_edges.geometry.length
        columns_to_extract.append("length")
    
    # Extract the columns
    segments_df = gdf_edges[columns_to_extract].copy()
    
    # Process the geometry to extract coordinates
    print("Processing coordinates...")
    segments_df["start_lat"] = segments_df.geometry.apply(lambda g: g.coords[0][1])
    segments_df["start_lon"] = segments_df.geometry.apply(lambda g: g.coords[0][0])
    segments_df["end_lat"] = segments_df.geometry.apply(lambda g: g.coords[-1][1])
    segments_df["end_lon"] = segments_df.geometry.apply(lambda g: g.coords[-1][0])
    
    # Create a unique segment ID
    segments_df["segment_id"] = segments_df.index
    
    # Extract named roads (optional filter)
    named_segments_df = segments_df[segments_df["name"].notna()]
    print(f"Found {len(named_segments_df)} named road segments out of {len(segments_df)} total segments.")
    
    # Save named segments to CSV (smaller file, more manageable)
    print(f"Saving named road segments to {named_segments_filepath}...")
    named_segments_df.to_csv(named_segments_filepath, index=False)
    
    # Save all segments to CSV
    print(f"Saving all road segments to {segments_filepath}...")
    segments_df.to_csv(segments_filepath, index=False)
    
    # Display sample data
    print("\nSample road segments:")
    sample_columns = ["name", "start_lat", "start_lon", "end_lat", "end_lon", "length"]
    print(named_segments_df[sample_columns].head())
    
    elapsed_time = time.time() - start_time
    print(f"\nExtracted {len(segments_df)} total road segments ({len(named_segments_df)} named).")
    print(f"Data saved to {segments_filepath} and {named_segments_filepath}")
    print(f"Processing completed in {elapsed_time:.2f} seconds.")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
