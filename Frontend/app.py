import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="AI Traffic System", layout="wide")
st.title("🚦 AI Traffic Prediction & Route Optimization")

# -----------------------------
# Sidebar Inputs
# -----------------------------
st.sidebar.header("Enter Traffic Conditions")

temp = st.sidebar.slider("Temperature", 250, 320, 288)
rain = st.sidebar.slider("Rain", 0.0, 10.0, 0.0)
snow = st.sidebar.slider("Snow", 0.0, 5.0, 0.0)
clouds = st.sidebar.slider("Cloud %", 0, 100, 40)
hour = st.sidebar.slider("Hour", 0, 23, 8)
day = st.sidebar.slider("Day", 1, 31, 10)
month = st.sidebar.slider("Month", 1, 12, 3)
day_of_week = st.sidebar.slider("Day of Week", 0, 6, 1)

# -----------------------------
# Prediction API
# -----------------------------
if st.sidebar.button("Predict Traffic"):
    try:
        url = "http://127.0.0.1:8000/predict"

        params = {
            "temp": temp,
            "rain": rain,
            "snow": snow,
            "clouds": clouds,
            "hour": hour,
            "day": day,
            "month": month,
            "day_of_week": day_of_week
        }

        res = requests.post(url, params=params)
        data = res.json()

        st.subheader("Prediction Result")
        st.metric("Traffic Volume", data['traffic_volume'])

        if data['congestion_level'] == "High":
            st.error("🔴 Heavy Traffic")
        elif data['congestion_level'] == "Medium":
            st.warning("🟠 Medium Traffic")
        else:
            st.success("🟢 Low Traffic")

    except:
        st.error("❌ Backend not connected")

# -----------------------------
# Map UI (ONLY UI)
# -----------------------------
st.subheader("🗺 Route Selection")

m = folium.Map(location=[24.8607, 67.0011], zoom_start=12)

map_data = st_folium(m, width=1200, height=500)

# -----------------------------
# Click Handling
# -----------------------------
if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    st.write(f"Selected Point: {lat}, {lon}")

    if "points" not in st.session_state:
        st.session_state.points = []

    st.session_state.points.append((lat, lon))

# -----------------------------
# Call Route API (NEXT STEP)
# -----------------------------
if len(st.session_state.get("points", [])) >= 2:

    start = st.session_state.points[-2]
    end = st.session_state.points[-1]

    try:
        url = "http://127.0.0.1:8000/route"

        res = requests.post(url, json={
            "start_lat": start[0],
            "start_lon": start[1],
            "end_lat": end[0],
            "end_lon": end[1]
        })

        route_data = res.json()

        # Draw route
        route_map = folium.Map(location=start, zoom_start=13)

        folium.PolyLine(route_data["route"], color="blue", weight=5).add_to(route_map)

        st.subheader("🛣 Best Route")
        st_folium(route_map, width=1200, height=500)

    except:
        st.error("Route API not working ❌")