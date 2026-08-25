import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from datetime import datetime
import pytz

# --- CONFIGURATION ---
API_KEY = "266429f3bfe7a437941f7b13747d7c83" # Consider storing in st.secrets
BASE_URL_WEATHER = "http://api.openweathermap.org/data/2.5/weather?"
BASE_URL_FORECAST = "http://api.openweathermap.org/data/2.5/forecast?"

st.set_page_config(page_title="Aero | Premium Weather", page_icon="🌦️", layout="wide", initial_sidebar_state="collapsed")

# --- 1. PREMIUM CSS STYLING (CARROT / Overdrop Inspiration) ---
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #FFFFFF;
    }
    
    /* Clean up Streamlit defaults */
    .block-container { padding-top: 2rem !important; max-width: 1200px; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Modularity & Glassmorphism */
    .premium-card {
        background: rgba(30, 30, 35, 0.7);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 16px 40px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        transition: transform 0.2s ease;
    }
    .premium-card:hover { transform: translateY(-2px); }

    /* Typography Hierarchy (Apple Weather Inspiration) */
    .hero-location { font-size: 2rem; font-weight: 600; letter-spacing: -0.5px; margin: 0; }
    .hero-temp { font-size: 6rem; font-weight: 200; line-height: 1; margin: 10px 0; letter-spacing: -3px; }
    .hero-desc { font-size: 1.5rem; font-weight: 400; color: #4DA8DA; text-transform: capitalize; }
    .hero-hl { font-size: 1.1rem; color: #A0A0A5; font-weight: 500; }
    
    /* Actionable Insight Banner */
    .insight-banner {
        background: linear-gradient(90deg, rgba(77, 168, 218, 0.15), rgba(77, 168, 218, 0.05));
        border-left: 4px solid #4DA8DA;
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 24px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* Sub-metrics (AccuWeather Utility) */
    .metric-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .metric-item { background: rgba(0,0,0,0.2); padding: 16px; border-radius: 16px; }
    .m-label { font-size: 0.85rem; color: #8E8E93; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }
    .m-val { font-size: 1.5rem; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ACQUISITION & PROCESSING ---
@st.cache_data(ttl=300)
def fetch_weather_bundle(city):
    """Fetches both current weather and 5-day forecast to build a complete dashboard."""
    try:
        current = requests.get(f"{BASE_URL_WEATHER}appid={API_KEY}&q={city}&units=metric", timeout=5).json()
        if current.get('cod') != 200: return None, None
        
        forecast = requests.get(f"{BASE_URL_FORECAST}appid={API_KEY}&q={city}&units=metric", timeout=5).json()
        return current, forecast
    except:
        return None, None

def generate_actionable_insight(current_data, forecast_data):
    """Answers Rule #3: Do I need to change my plans?"""
    temp = current_data['main']['temp']
    condition = current_data['weather'][0]['main']
    
    # Check next 12 hours for rain
    upcoming_rain = any(item['weather'][0]['main'] == 'Rain' for item in forecast_data['list'][:4])
    
    if condition in ['Thunderstorm', 'Extreme']: return "🚨 Severe weather active. Alter outdoor plans immediately."
    if upcoming_rain and condition != 'Rain': return "☂️ Rain expected in the next 12 hours. Bring an umbrella."
    if condition == 'Rain': return "🌧️ Currently raining. Expect wet roads and slower transit."
    if temp > 32: return "🥵 Extreme heat. Stay indoors or hydrate if going outside."
    if temp < 0: return "❄️ Freezing temperatures. Dress in heavy layers."
    return "✅ Conditions are optimal. No need to change your plans today."

# --- 3. UI COMPONENTS ---
def draw_temperature_chart(forecast_data):
    """Creates a sleek, Apple-style temperature curve using Plotly."""
    # Extract next 24 hours (8 periods of 3 hours)
    times = [datetime.fromtimestamp(item['dt']).strftime('%I %p') for item in forecast_data['list'][:8]]
    temps = [round(item['main']['temp']) for item in forecast_data['list'][:8]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=temps,
        mode='lines+markers+text',
        text=[f"{t}°" for t in temps],
        textposition="top center",
        line=dict(color='#4DA8DA', width=4, shape='spline'),
        marker=dict(size=10, color='#FFFFFF', line=dict(color='#4DA8DA', width=2)),
        fill='tozeroy',
        fillcolor='rgba(77, 168, 218, 0.1)'
    ))
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=200,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, showline=False, zeroline=False, color='#A0A0A5'),
        yaxis=dict(showgrid=False, showline=False, zeroline=False, visible=False, range=[min(temps)-5, max(temps)+5]),
        showlegend=False,
        hovermode="x unified"
    )
    return fig

def draw_radar_map(lat, lon):
    """Creates a Windy-style interactive precipitation map using Folium."""
    # Center map on location
    m = folium.Map(location=[lat, lon], zoom_start=9, tiles='CartoDB dark_matter')
    
    # Add OpenWeatherMap Precipitation Tile Layer
    folium.TileLayer(
        tiles=f'https://tile.openweathermap.org/map/precipitation_new/{{z}}/{{x}}/{{y}}.png?appid={API_KEY}',
        attr='OpenWeatherMap',
        name='Precipitation',
        overlay=True,
        control=False,
        opacity=0.7
    ).add_to(m)
    
    # Add marker for the city
    folium.Marker([lat, lon], icon=folium.Icon(color='blue', icon='cloud')).add_to(m)
    return m

# --- 4. MAIN APPLICATION ---
inject_custom_css()

# Default city
if 'city' not in st.session_state:
    st.session_state.city = "New York"

# Background styling (Dynamic dark mode based on weather)
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top right, #1a202c, #0d1117);
}
</style>
""", unsafe_allow_html=True)

# Search Bar
search_col1, search_col2, _ = st.columns([1, 0.2, 2])
with search_col1:
    new_city = st.text_input("Search Location", placeholder="Search city...", label_visibility="collapsed")
with search_col2:
    if st.button("Search", use_container_width=True) and new_city:
        st.session_state.city = new_city
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Fetch Data
with st.spinner("Syncing global telemetry..."):
    current, forecast = fetch_weather_bundle(st.session_state.city)

if current and forecast:
    # Extract Hero Data
    name = current['name']
    temp = round(current['main']['temp'])
    high = round(current['main']['temp_max'])
    low = round(current['main']['temp_min'])
    desc = current['weather'][0]['description']
    lat, lon = current['coord']['lat'], current['coord']['lon']
    
    # 1. QUESTION 3: DO I NEED TO CHANGE PLANS?
    insight = generate_actionable_insight(current, forecast)
    st.markdown(f"""
    <div class="insight-banner">
        <span style="font-size: 1.5rem;">🤖</span>
        <div>
            <div style="font-size: 0.8rem; color: #A0A0A5; text-transform: uppercase; letter-spacing: 1px;">AI Insight</div>
            <div>{insight}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main Grid Layout
    col_hero, col_map = st.columns([1.2, 1])
    
    with col_hero:
        # 2. QUESTION 1: WHAT IS HAPPENING NOW? (Apple Weather Hero)
        st.markdown(f"""
        <div class="premium-card" style="text-align: center; padding: 40px 20px;">
            <p class="hero-location">{name}</p>
            <h1 class="hero-temp">{temp}°</h1>
            <p class="hero-desc">{desc}</p>
            <p class="hero-hl">H:{high}° &nbsp;&nbsp; L:{low}°</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. QUESTION 2: WHAT IS HAPPENING NEXT? (24h Trend)
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="m-label">🕒 24-Hour Forecast</div>', unsafe_allow_html=True)
        st.plotly_chart(draw_temperature_chart(forecast), use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_map:
        # 4. WINDY-STYLE VISUALIZATION
        st.markdown('<div class="premium-card" style="padding: 16px;">', unsafe_allow_html=True)
        st.markdown('<div class="m-label" style="margin-bottom: 12px;">🛰️ Live Precipitation Radar</div>', unsafe_allow_html=True)
        # Display Folium Map
        st_folium(draw_radar_map(lat, lon), height=325, use_container_width=True, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 5. ACCUWEATHER-STYLE UTILITY (Deep Details)
        feels = round(current['main']['feels_like'])
        humidity = current['main']['humidity']
        wind = round(current['wind']['speed'] * 3.6) # km/h
        pressure = current['main']['pressure']
        
        st.markdown(f"""
        <div class="premium-card">
            <div class="metric-grid">
                <div class="metric-item">
                    <div class="m-label">🌡️ RealFeel</div>
                    <div class="m-val">{feels}°</div>
                </div>
                <div class="metric-item">
                    <div class="m-label">💨 Wind</div>
                    <div class="m-val">{wind} <span style="font-size:0.9rem; color:#888;">km/h</span></div>
                </div>
                <div class="metric-item">
                    <div class="m-label">💧 Humidity</div>
                    <div class="m-val">{humidity}%</div>
                </div>
                <div class="metric-item">
                    <div class="m-label">⏲️ Pressure</div>
                    <div class="m-val">{pressure} <span style="font-size:0.9rem; color:#888;">hPa</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
else:
    st.error("Location not found. Please try another search.")
