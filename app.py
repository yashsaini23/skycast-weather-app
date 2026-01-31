import streamlit as st
import requests
import time  # <--- NEW: Needed for the animation delay

# --- CONFIGURATION ---
API_KEY = "266429f3bfe7a437941f7b13747d7c83"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

st.set_page_config(page_title="SkyCast AI", page_icon="🌦️", layout="centered")

# --- 1. CSS STYLING ---
def add_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* ANIMATIONS */
    @keyframes slideIn {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }

    /* GLASS CARD */
    .glass-card {
        background: rgba(0, 0, 0, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 30px;
        margin-top: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        text-align: center;
        animation: slideIn 0.8s ease-out;
    }

    /* METRIC CARDS */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        animation: slideIn 1s ease-out;
    }

    /* TEXT VISIBILITY */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: white !important;
    }
    
    /* INPUT BOX STYLING (Translucent + Dark Text) */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.6) !important;
        color: black !important;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.5);
        border-radius: 10px;
    }
    ::placeholder { 
        color: #333333 !important;
        opacity: 0.8; 
    }

    /* CUSTOM LOADING BAR COLOR */
    .stProgress > div > div > div > div {
        background-color: #FF4B2B;
    }

    /* BUTTON STYLING */
    .stButton > button {
        background: linear-gradient(45deg, #FF4B2B, #FF416C);
        color: white !important;
        border: none;
        border-radius: 10px;
        height: 45px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC & BACKGROUND ENGINE ---
def set_background(weather_condition):
    bg_images = {
        "Clear": "https://images.unsplash.com/photo-1601297183305-6df142704ea2?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80",
        "Clouds": "https://images.unsplash.com/photo-1534088568595-a066f410bcda?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80",
        "Rain": "https://images.unsplash.com/photo-1519692933481-e162a57d6721?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80",
        "Snow": "https://images.unsplash.com/photo-1517299321609-52687d1bc555?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80",
        "Thunderstorm": "https://images.unsplash.com/photo-1605727216801-e27ce1ca8728?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80",
        "Default": "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80"
    }
    image_url = bg_images.get(weather_condition, bg_images["Default"])
    
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("{image_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

def get_weather_data(city):
    try:
        url = f"{BASE_URL}appid={API_KEY}&q={city}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def calculate_ai_insight(temp, clouds):
    if temp > 30: return "🥵 High Heat", "Stay hydrated and avoid direct sun."
    elif temp < 10: return "🥶 Freezing", "Wear heavy layers."
    elif clouds > 80: return "☁️ Gloomy", "Great weather for coding inside."
    else: return "🚀 Optimal", "Go touch grass."

# --- 3. MAIN APP EXECUTION ---

# A. Load CSS
add_custom_css()

# B. Initialize Session State
if 'weather_data' not in st.session_state:
    st.session_state['weather_data'] = None
if 'bg_state' not in st.session_state:
    st.session_state['bg_state'] = "Default"

# C. Set Background
set_background(st.session_state['bg_state'])

# D. Header
st.markdown("<h1 style='text-align: center; font-size: 3.5rem; margin-bottom: 0;'>SkyCast AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.8;'>Professional Weather Intelligence</p>", unsafe_allow_html=True)

# E. Search Interface
col1, col2 = st.columns([3, 1])
with col1:
    city_input = st.text_input("", placeholder="Enter City (e.g. London)", label_visibility="collapsed")
with col2:
    search_clicked = st.button("Analyze")

# F. LOGIC HANDLING (With Loading Animation)
if search_clicked and city_input:
    
    # --- 1. THE LOADING SEQUENCE ---
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    
    # Fake steps to look cool
    steps = [
        "🛰️ Connecting to Weather Satellite...",
        "🌍 Triangulating Global Coordinates...",
        "☁️ Analyzing Cloud Density...",
        "🧠 Running AI Prediction Models..."
    ]
    
    for i, step in enumerate(steps):
        # Update progress bar and text
        my_bar.progress((i + 1) * 20, text=step)
        time.sleep(0.3)  # Fake delay for drama
        
    # --- 2. ACTUAL DATA FETCH ---
    data = get_weather_data(city_input)
    
    if data:
        # Finish the bar
        my_bar.progress(100, text="✅ Analysis Complete!")
        time.sleep(0.5) # Let user see the 100%
        my_bar.empty()  # Remove the bar
        
        # Save state and reload
        st.session_state['weather_data'] = data
        st.session_state['bg_state'] = data['weather'][0]['main']
        st.rerun()
    else:
        my_bar.empty()
        st.error("❌ City not found! Please check the spelling.")

# G. RENDER SAVED DATA
if st.session_state['weather_data']:
    data = st.session_state['weather_data']
    
    name = data['name']
    temp = round(data['main']['temp'])
    desc = data['weather'][0]['description'].title()
    humidity = data['main']['humidity']
    wind = data['wind']['speed']
    clouds = data['clouds']['all']
    mood, advice = calculate_ai_insight(temp, clouds)

    # 1. Main Glass Card
    st.markdown(f"""
    <div class="glass-card">
        <h2 style="font-weight: 300; margin: 0;">{name}</h2>
        <h1 style="font-size: 5rem; margin: 10px 0;">{temp}°</h1>
        <p style="font-size: 1.2rem; text-transform: capitalize;">{desc}</p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Metrics Grid
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='metric-card'><h3>💧 {humidity}%</h3><p>Humidity</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><h3>💨 {wind} m/s</h3><p>Wind</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><h3>☁️ {clouds}%</h3><p>Cloud Cover</p></div>", unsafe_allow_html=True)

    # 3. AI Insight
    st.markdown(f"""
    <div class="glass-card" style="margin-top: 20px; text-align: left;">
        <h3>🤖 AI Analysis: {mood}</h3>
        <p>"{advice}"</p>
    </div>
    """, unsafe_allow_html=True)