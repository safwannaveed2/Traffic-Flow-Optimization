import osmnx as ox

# Download once
G = ox.graph_from_place("Clifton,Karachi, Pakistan", network_type='drive')

# Save locally
ox.save_graphml(G, "karachi_map.graphml")

print("Map saved successfully ✅")