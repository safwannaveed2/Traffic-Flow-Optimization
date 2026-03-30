from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import networkx as nx
import osmnx as ox

app = FastAPI()

# Load ML model
model = joblib.load("Backend/scaler.pkl")
model = joblib.load("Backend/traffic_model.pkl")

G = ox.load_graphml("karachi_map.graphml")

# Pydantic model
class TrafficInput(BaseModel):
    temp: float
    rain: float
    snow: float
    clouds: float
    hour: int
    day: int
    month: int
    day_of_week: int

class RouteInput(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float

# Prediction API
@app.post("/predict")
def predict(data: TrafficInput):
    features = [[
        data.temp, data.rain, data.snow, data.clouds,
        data.hour, data.day, data.month, data.day_of_week
    ]]
    traffic_volume = model.predict(features)[0]
    if traffic_volume > 4000:
        level = "High"
    elif traffic_volume > 2000:
        level = "Medium"
    else:
        level = "Low"
    return {"traffic_volume": int(traffic_volume), "congestion_level": level}

# Route API
@app.post("/route")
def get_route(data: RouteInput):
    start_node = ox.distance.nearest_nodes(G, data.start_lon, data.start_lat)
    end_node = ox.distance.nearest_nodes(G, data.end_lon, data.end_lat)
    route_nodes = nx.shortest_path(G, start_node, end_node, weight='length')
    route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route_nodes]
    return {"route": route_coords}
