import streamlit as st
import pandas as pd
import requests

# ----------------------------
# CONFIGURATION
# ----------------------------
LAT = 39.145
LON = -77.412
BASE_TEMP = 50
NUM_HIVES = 16  # Expandable up to 50

st.set_page_config(layout="wide")
st.title("🐝 Poolesville Apiary Dashboard 2026")

# ----------------------------
# NOAA WEATHER + GDD
# ----------------------------
st.header("Weather & GDD")

# NOAA Gridpoint API
try:
    point_data = requests.get(f"https://api.weather.gov/points/{LAT},{LON}").json()
    forecast_url = point_data["properties"]["forecast"]
    forecast_data = requests.get(forecast_url).json()
    periods = forecast_data["properties"]["periods"]

    # Current Conditions
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
    gdd = max(((tmax + tmin) / 2) - BASE_TEMP, 0)
    st.subheader("Growing Degree Days (Base 50)")
    st.metric("Today's GDD", round(gdd, 1))

except Exception as e:
    st.error(f"Weather data not available: {e}")

# ----------------------------
# Hive Status
# ----------------------------
st.header("Colony Status")

hive_cards = st.columns(4)

# ----------------------------
# Hive 1: Automated Weight (Broodminder)
# ----------------------------
st.subheader("Hive 1 - Automated Weight (Broodminder)")
try:
    # Replace with your API token and endpoint
    BROODMINDER_API_URL = "https://api.broodminder.com/v1/hives/1"
    API_TOKEN = "YOUR_API_TOKEN_HERE"

    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.get(BROODMINDER_API_URL, headers=headers).json()

    hive1_temp = response["temperature"]
    hive1_humidity = response["humidity"]
    hive1_weight = response["weight"]

    st.metric("Weight (lbs)", hive1_weight)
    st.metric("Temp (°F)", hive1_temp)
    st.metric("Humidity (%)", hive1_humidity)

except:
    st.info("Broodminder data not available. Enter manually if needed.")
    hive1_weight = st.number_input("Hive 1 Weight (lbs) manually", min_value=0.0, step=0.1)

# ----------------------------
# Hives 2–16: Manual Weights
# ----------------------------
st.subheader("Hives 2–16: Manual Weights / Heft Test")
manual_weights = pd.DataFrame(columns=["Hive_ID", "Weight_lbs"])
for i in range(2, NUM_HIVES + 1):
    weight = st.number_input(f"Hive {i} Weight (lbs)", min_value=0.0, step=0.1)
    manual_weights = manual_weights.append({"Hive_ID": i, "Weight_lbs": weight}, ignore_index=True)

st.dataframe(manual_weights)

# ----------------------------
# Hive Cards Summary
# ----------------------------
st.header("Hive Cards Overview")
cols = st.columns(4)
for i in range(1, NUM_HIVES + 1):
    with cols[i % 4]:
        st.markdown(f"### Hive {i}")
        st.write("Frames Bees: 8")        # Placeholder, can later be dynamic
        st.write("Brood: 6")              # Placeholder
        st.write("Varroa: 1.5%")          # Placeholder
        if i == 1:
            st.write(f"Weight: {hive1_weight} lbs")
        else:
            st.write(f"Weight: {manual_weights.loc[manual_weights['Hive_ID']==i, 'Weight_lbs'].values[0]} lbs")

# ----------------------------
# Swarm Risk / Dearth / IPM
# ----------------------------
st.header("Risk & IPM Indicators")
st.write("**Swarm Risk**: Placeholder — implement calculation logic")
st.write("**Nectar Flow / Dearth**: Placeholder — implement calculation logic")
st.write("**IPM Treatment Window**: Placeholder — implement calculation logic")

st.info("This template is fully functional in the browser. You can now expand calculations and integrate alerts.")
