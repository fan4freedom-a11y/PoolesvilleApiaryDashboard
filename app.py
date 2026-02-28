import streamlit as st
import pandas as pd
import requests

# ----------------------------
# CONFIGURATION
# ----------------------------
LAT, LON = 39.145, -77.412
BASE_TEMP = 50
NUM_HIVES = 16
VARROA_THRESHOLD = 2.0  # %
BROODMINDER_API_URL = "https://api.broodminder.com/v1/hives/1"
API_TOKEN = "YOUR_BROODMINDER_API_TOKEN"  # Replace with your token

st.set_page_config(layout="wide")
st.title("🐝 Poolesville Apiary Dashboard 2026")

# ----------------------------
# NOAA WEATHER & GDD
# ----------------------------
st.header("Weather & GDD")
try:
    point_data = requests.get(f"https://api.weather.gov/points/{LAT},{LON}").json()
    forecast_url = point_data["properties"]["forecast"]
    forecast_data = requests.get(forecast_url).json()
    periods = forecast_data["properties"]["periods"]

    today = periods[0]
    st.subheader("Current Conditions")
    st.metric("Temperature", f"{today['temperature']}°F")
    st.write(today["shortForecast"])

    # 7-Day Forecast
    st.subheader("7-Day Forecast")
    forecast_df = pd.DataFrame([{
        "Day": p["name"],
        "Temp": p["temperature"],
        "Forecast": p["shortForecast"]
    } for p in periods[:7]])
    st.dataframe(forecast_df, use_container_width=True)

    # GDD50 Calculation
    tmax = periods[0]["temperature"]
    tmin = periods[1]["temperature"] if len(periods) > 1 else tmax
    gdd = max(((tmax + tmin)/2) - BASE_TEMP, 0)
    st.subheader("Growing Degree Days (Base 50)")
    st.metric("Today's GDD", round(gdd,1))

except:
    st.error("Weather data not available")

# ----------------------------
# Hive 1 Broodminder Data
# ----------------------------
st.header("Hive 1 - Broodminder")
hive1_weight = 0.0
hive1_temp = 0.0
hive1_humidity = 0.0
hive1_varroa = st.number_input("Hive 1 Varroa (%)", min_value=0.0, step=0.1)

try:
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.get(BROODMINDER_API_URL, headers=headers).json()
    hive1_weight = response.get("weight", 0.0)
    hive1_temp = response.get("temperature", 0.0)
    hive1_humidity = response.get("humidity", 0.0)
except:
    st.warning("Broodminder API not available. Using manual Hive 1 weight input.")
    hive1_weight = st.number_input("Hive 1 Weight (lbs) manually", min_value=0.0, step=0.1)

st.metric("Weight (lbs)", hive1_weight)
st.metric("Temp (°F)", hive1_temp)
st.metric("Humidity (%)", hive1_humidity)

# ----------------------------
# Manual Hives 2–16
# ----------------------------
st.subheader(f"Hives 2–{NUM_HIVES}: Manual Weights / Heft Test")
manual_data = []
manual_varroa = []
manual_frames_bees = []
manual_frames_brood = []

for i in range(2, NUM_HIVES+1):
    w = st.number_input(f"Hive {i} Weight (lbs)", min_value=0.0, step=0.1)
    v = st.number_input(f"Hive {i} Varroa (%)", min_value=0.0, step=0.1)
    frames_bees = st.number_input(f"Hive {i} Frames of Bees", min_value=0, max_value=20, value=8)
    frames_brood = st.number_input(f"Hive {i} Frames of Brood", min_value=0, max_value=20, value=6)
    manual_data.append({"Hive_ID": i, "Weight_lbs": w})
    manual_varroa.append({"Hive_ID": i, "Varroa": v})
    manual_frames_bees.append({"Hive_ID": i, "Frames_Bees": frames_bees})
    manual_frames_brood.append({"Hive_ID": i, "Frames_Brood": frames_brood})

manual_weights = pd.DataFrame(manual_data)
manual_varroa_df = pd.DataFrame(manual_varroa)
manual_frames_bees_df = pd.DataFrame(manual_frames_bees)
manual_frames_brood_df = pd.DataFrame(manual_frames_brood)

# ----------------------------
# Hive Cards Overview
# ----------------------------
st.header("Hive Cards Overview")
cols = st.columns(4)
for i in range(1, NUM_HIVES+1):
    with cols[i % 4]:
        st.markdown(f"### Hive {i}")
        if i == 1:
            varroa_val = hive1_varroa
            weight_val = hive1_weight
            frames_bees_val = st.number_input("Frames of Bees (Hive 1)", min_value=0, max_value=20, value=8)
            frames_brood_val = st.number_input("Frames of Brood (Hive 1)", min_value=0, max_value=20, value=6)
        else:
            varroa_val = manual_varroa_df.loc[manual_varroa_df['Hive_ID']==i, 'Varroa'].values[0]
            weight_val = manual_weights.loc[manual_weights['Hive_ID']==i, 'Weight_lbs'].values[0]
            frames_bees_val = manual_frames_bees_df.loc[manual_frames_bees_df['Hive_ID']==i, 'Frames_Bees'].values[0]
            frames_brood_val = manual_frames_brood_df.loc[manual_frames_brood_df['Hive_ID']==i, 'Frames_Brood'].values[0]

        st.write(f"Varroa: {varroa_val}%")
        st.write(f"Weight: {weight_val} lbs")
        st.write(f"Frames Bees: {frames_bees_val}")
        st.write(f"Brood: {frames_brood_val}")

# ----------------------------
# Swarm Risk (color-coded)
# ----------------------------
st.header("Swarm Risk")
swarm_risk = "Low"
color = "green"
if hive1_weight > 90 or today["temperature"] > 70:
    swarm_risk = "Moderate"
    color = "orange"
if hive1_weight > 95 and today["temperature"] > 75:
    swarm_risk = "High"
    color = "red"
st.markdown(f"<h3 style='color:{color}'>{swarm_risk}</h3>", unsafe_allow_html=True)

# ----------------------------
# Nectar Flow / Dearth (color-coded)
# ----------------------------
st.header("Nectar Flow / Dearth")
month = pd.Timestamp.today().month
nectar_status = "Unknown"
color = "gray"
if 3 <= month <= 6:
    nectar_status = "Spring Nectar Flow"
    color = "green"
elif 7 <= month <= 8:
    nectar_status = "Summer Dearth"
    color = "red"
elif 9 <= month <= 10:
    nectar_status = "Fall Nectar Flow"
    color = "orange"
else:
    nectar_status = "Winter - No Nectar"
    color = "blue"
st.markdown(f"<h3 style='color:{color}'>{nectar_status}</h3>", unsafe_allow_html=True)

# ----------------------------
# IPM Treatment Window (color-coded)
# ----------------------------
st.header("IPM Treatment Window")
ipm_status = "No Treatment Needed"
color = "green"
if hive1_varroa >= VARROA_THRESHOLD:
    ipm_status = "Treatment Recommended"
    color = "red"
st.markdown(f"<h3 style='color:{color}'>{ipm_status}</h3>", unsafe_allow_html=True)
