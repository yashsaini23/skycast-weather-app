import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURATION ---
API_KEY = "266429f3bfe7a437941f7b13747d7c83"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

st.set_page_config(page_title="SkyCast | Professional Weather", page_icon="🌤️", layout="wide")

# --- 1. CSS STYLING ---
def add_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* BASE APP STYLING */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #E0E0E0;
    }
    
    /* REMOVE STREAMLIT PADDING FOR EDGE-TO-EDGE FEEL */
    .block-container {
        padding-top: 2rem !important;
        max-width: 1000px;
    }

    /* SEARCH BAR STYLING */
    .stTextInput > div > div > input {
        background-color: rgba(20, 20, 20, 0.8) !important;
        color: white !important;
        border: 1px solid #333333 !important;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 1.1rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #F5A623 !important;
        box-shadow: none !important;
    }
    
    /* BUTTON STYLING */
    .stButton > button {
        background-color: #F5A623 !important;
        color: #111 !important;
        border: none !important;
        border-radius: 8px;
        height: 52px;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #FFAE34 !important;
        transform: translateY(-1px);
    }

    /* DASHBOARD CARDS */
    .weather-panel {
        background: rgba(30, 30, 30, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    
    .metric-box {
        background: rgba(45, 45, 45, 0.6);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* TYPOGRAPHY */
    .city-name { font-size: 1.5rem; font-weight: 600; color: #fff; margin: 0; }
    .current-temp { font-size: 5.5rem; font-weight: 700; line-height: 1; color: #fff; margin: 10px 0; letter-spacing: -2px; }
    .condition-text { font-size: 1.2rem; font-weight: 400; color: #F5A623; text-transform: uppercase; letter-spacing: 1px; }
    .feels-like { font-size: 1rem; color: #AAAAAA; margin-bottom: 20px; }
    
    .metric-label { font-size: 0.85rem; color: #888; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 4px; }
    .metric-value { font-size: 1.4rem; font-weight: 600; color: #fff; }

    /* DIVIDER */
    hr { border-color: rgba(255,255,255,0.1); margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

def set_background(weather_condition):
    # Using darker, highly atmospheric Unsplash images for a premium feel
    bg_images = {
        "Clear": "https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?q=80&w=2000&auto=format&fit=crop",
        "Clouds": "https://images.unsplash.com/photo-1534088568595-a066f410bcda?q=80&w=2000&auto=format&fit=crop",
        "Rain": "https://images.unsplash.com/photo-1433863448220-78aaa064ff47?q=80&w=2000&auto=format&fit=crop",
        "Snow": "https://images.unsplash.com/photo-1483664852095-d6cc6870702d?q=80&w=2000&auto=format&fit=crop",
        "Thunderstorm": "https://images.unsplash.com/photo-1605727216801-e27ce1ca8728?q=80&w=2000&auto=format&fit=crop",
        "Default": "https://images.unsplash.com/photo-1504608524841-42ce6c20b001?q=80&w=2000&auto=format&fit=crop"
    }
    image_url = bg_images.get(weather_condition, bg_images["Default"])
    
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.8)), url("{image_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC ENGINE ---
@st.cache_data(ttl=600) # Cache API calls for 10 mins to prevent rate limiting
def get_weather_data(city):
    try:
        url = f"{BASE_URL}appid={API_KEY}&q={city}&units=metric"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_weather_icon(condition):
    icons = {
        "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️", 
        "Drizzle": "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️", 
        "Mist": "🌫️", "Fog": "🌫️", "Smoke": "💨", "Haze": "🌁"
    }
    return icons.get(condition, "🌡️")

# --- 3. MAIN APP EXECUTION ---
add_custom_css()

if 'weather_data' not in st.session_state:
    st.session_state['weather_data'] = None
if 'bg_state' not in st.session_state:
    st.session_state['bg_state'] = "Default"

set_background(st.session_state['bg_state'])

# Header
st.markdown("<h2 style='color: white; margin-bottom: 30px;'>SkyCast <span style='color: #F5A623;'>Intelligence</span></h2>", unsafe_allow_html=True)

# Search Interface
col1, col2 = st.columns([4, 1])
with col1:
    city_input = st.text_input("", placeholder="Search for a city or zip code...", label_visibility="collapsed")
with col2:
    search_clicked = st.button("Search")

if search_clicked and city_input:
    with st.spinner("Retrieving latest telemetry..."):
        data = get_weather_data(city_input)
        
    if data:
        st.session_state['weather_data'] = data
        st.session_state['bg_state'] = data['weather'][0]['main']
        st.rerun()
    else:
        st.error("⚠️ Location not found. Please verify the city name.")

# Render Dashboard
if st.session_state['weather_data']:
    data = st.session_state['weather_data']
    
    # Extract rich data
    name = data['name']
    country = data['sys'].get('country', '')
    main_weather = data['weather'][0]['main']
    desc = data['weather'][0]['description']
    icon = get_weather_icon(main_weather)
    
    temp = round(data['main']['temp'])
    feels_like = round(data['main']['feels_like'])
    temp_min = round(data['main']['temp_min'])
    temp_max = round(data['main']['temp_max'])
    
    humidity = data['main']['humidity']
    wind_speed = round(data['wind']['speed'] * 3.6, 1) # Convert m/s to km/h
    pressure = data['main']['pressure']
    visibility = round(data.get('visibility', 0) / 1000, 1) # Convert m to km
    
    local_time = datetime.now().strftime("%A, %I:%M %p")

    # DASHBOARD LAYOUT
    st.markdown('<div class="weather-panel">', unsafe_allow_html=True)
    
    left_col, right_col = st.columns([1.2, 1])
    
    with left_col:
        st.markdown(f"""
        <div style="padding-right: 20px;">
            <p class="city-name">{name}, {country}</p>
            <p style="color: #888; font-size: 0.9rem; margin-top: 5px;">As of {local_time}</p>
            <h1 class="current-temp">{temp}°<span style="font-size: 3rem; color: #888;">C</span></h1>
            <p class="condition-text">{icon} {desc}</p>
            <p class="feels-like">RealFeel® {feels_like}° &nbsp;|&nbsp; High {temp_max}° &nbsp;|&nbsp; Low {temp_min}°</p>
            <hr>
            <p style="font-size: 0.95rem; color: #ccc; line-height: 1.5;">
                <strong>SkyCast AI Summary:</strong> 
                {"Expect clear skies and optimal conditions." if main_weather == "Clear" 
                else "Precipitation expected. Consider bringing an umbrella." if main_weather in ["Rain", "Drizzle"] 
                else "Overcast conditions. Visibility may be reduced."}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with right_col:
        st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Wind Gusts</div>
                <div class="metric-value">{wind_speed} km/h</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Humidity</div>
                <div class="metric-value">{humidity}%</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Pressure</div>
                <div class="metric-value">{pressure} mb</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Visibility</div>
                <div class="metric-value">{visibility} km</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
