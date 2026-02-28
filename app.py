import streamlit as st
import pandas as pd
import requests

# CONFIG
LAT, LON = 39.145, -77.412
BASE_TEMP = 50
NUM_HIVES = 16

st.set_page_config(layout="wide")
st.title("🐝 Poolesville Apiary Dashboard 2026")

# ----------------------------
# NOAA Weather & GDD
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

    # GDD50 Calculation (simple)
    tmax = periods[0]["temperature"]
    tmin = periods[0]["temperature"]  # fallback if next period missing
    if len(periods) > 1:
        tmin = periods[1]["temperature"]
    gdd = max(((tmax + tmin)/2) - BASE_TEMP, 0)
    st.subheader("Growing Degree Days (Base 50)")
    st.metric("Today's GDD", round(gdd,1))

except:
    st.error("Weather data not available")

# ----------------------------
# Hive Status
# ----------------------------
st.header("Hive Status")

# Hive 1 Automated Weight Placeholder
st.subheader("Hive 1 - Automated Weight (Broodminder)")
hive1_weight = st.number_input("Hive 1 Weight (lbs) manually if API not connected", min_value=0.0, step=0.1)

# Hives 2–16: Manual Weight Inputs
st.subheader(f"Hives 2–{NUM_HIVES} Manual Weights / Heft Test")
manual_data = []
for i in range(2, NUM_HIVES+1):
    w = st.number_input(f"Hive {i} Weight (lbs)", min_value=0.0, step=0.1)
    manual_data.append({"Hive_ID": i, "Weight_lbs": w})

manual_weights = pd.DataFrame(manual_data)
st.dataframe(manual_weights)

# ----------------------------
# Hive Cards
# ----------------------------
st.header("Hive Cards Overview")
cols = st.columns(4)
for i in range(1, NUM_HIVES+1):
    with cols[i % 4]:
        st.markdown(f"### Hive {i}")
        st.write("Frames Bees: 8")
        st.write("Brood: 6")
        st.write("Varroa: 1.5%")
        if i == 1:
            st.write(f"Weight: {hive1_weight} lbs")
        else:
            w = manual_weights.loc[manual_weights['Hive_ID']==i, 'Weight_lbs'].values[0]
            st.write(f"Weight: {w} lbs")

# ----------------------------
# Swarm / Dearth / IPM
# ----------------------------
st.header("Risk & IPM Indicators")
st.write("**Swarm Risk**: Placeholder — implement logic")
st.write("**Nectar Flow / Dearth**: Placeholder — implement logic")
st.write("**IPM Treatment Window**: Placeholder — implement logic")
