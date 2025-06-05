import osmnx as ox
import os
import matplotlib.pyplot as plt

# Define file paths for saving/loading data
graph_filepath = 'warsaw_graph.graphml'
image_filepath = 'warsaw_map.png'

# Check if the saved graph exists
if os.path.exists(graph_filepath):
    print(f"Loading graph from {graph_filepath}...")
    G = ox.load_graphml(graph_filepath)
else:
    print(f"Downloading road network for Warsaw, Poland...")
    # Download the drivable road network for Warsaw
    city = "Warsaw, Poland"
    G = ox.graph_from_place(city, network_type='drive')
    
    # Save the graph to disk for future use
    print(f"Saving graph to {graph_filepath}...")
    ox.save_graphml(G, graph_filepath)

# Plot the network and save to file
print("Plotting the network...")
fig, ax = ox.plot_graph(G, bgcolor='white', node_color='red', edge_color='gray', 
                       node_size=5, edge_linewidth=0.5, show=False, close=False)

# Save the figure to file
print(f"Saving visualization to {image_filepath}...")
plt.savefig(image_filepath, dpi=300, bbox_inches='tight')
print(f"Map saved to {image_filepath}")

# Display basic statistics about the network
print("\nNetwork Statistics:")
print(f"Number of nodes: {len(G.nodes)}")
print(f"Number of edges: {len(G.edges)}")

# Show the plot (optional - comment out if not needed)
plt.show()

print("Done!")
