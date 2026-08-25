import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION ---
API_KEY = "266429f3bfe7a437941f7b13747d7c83"
BASE_URL_CURRENT = "http://api.openweathermap.org/data/2.5/weather?"
BASE_URL_FORECAST = "http://api.openweathermap.org/data/2.5/forecast?"

st.set_page_config(page_title="AccuWeather Clone | Data Dense", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

# --- 1. ACCUWEATHER-STYLE CSS ARCHITECTURE ---
def inject_accuweather_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');

    /* BASE TYPOGRAPHY & PORTAL RESET */
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background-color: #121212;
        color: #FFFFFF;
    }
    
    /* REMOVE STREAMLIT PADDING */
    .block-container { padding-top: 1rem !important; max-width: 1400px; }
    header { visibility: hidden; }

    /* SEARCH BAR (TOP NAV) */
    .search-container {
        background-color: #1F1F1F;
        padding: 15px 20px;
        border-bottom: 2px solid #F05514; /* AccuWeather Orange */
        margin-bottom: 20px;
        border-radius: 8px;
    }
    .stTextInput > div > div > input {
        background-color: #2D2D2D !important;
        color: white !important;
        border: 1px solid #404040 !important;
        border-radius: 4px;
        padding: 10px 15px;
        font-size: 1rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #F05514 !important;
        box-shadow: none !important;
    }

    /* CARD SYSTEM */
    .aw-card {
        background-color: #1F1F1F;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #2D2D2D;
    }
    
    .aw-card-header {
        font-size: 0.9rem;
        text-transform: uppercase;
        color: #999999;
        font-weight: 700;
        margin-bottom: 15px;
        letter-spacing: 0.5px;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
    }

    /* CURRENT WEATHER HERO */
    .current-layout { display: flex; justify-content: space-between; align-items: center; }
    .current-temp-block { display: flex; align-items: center; gap: 20px; }
    .current-icon { font-size: 5rem; line-height: 1; }
    .current-temp { font-size: 6rem; font-weight: 700; line-height: 1; letter-spacing: -2px; }
    .current-realfeel { font-size: 1.2rem; font-weight: 700; color: #F05514; margin-top: 5px; }
    .current-desc { font-size: 1.5rem; font-weight: 500; text-transform: capitalize; }

    /* DENSE DATA GRID (RIGHT SIDE OF CURRENT CARD) */
    .details-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px 30px;
        border-left: 1px solid #333;
        padding-left: 30px;
    }
    .detail-item { display: flex; justify-content: space-between; font-size: 0.95rem; border-bottom: 1px solid #2D2D2D; padding-bottom: 4px;}
    .detail-label { color: #999999; }
    .detail-value { font-weight: 700; text-align: right; }

    /* FORECAST LISTS */
    .daily-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #2D2D2D;
    }
    .daily-row:last-child { border-bottom: none; }
    .day-date { width: 30%; font-weight: 700; font-size: 1.1rem; }
    .day-icon { width: 20%; font-size: 1.5rem; text-align: center; }
    .day-temps { width: 50%; text-align: right; font-weight: 700; font-size: 1.2rem;}
    .low-temp { color: #888; font-weight: 400; margin-left: 10px;}

    </style>
    """, unsafe_allow_html=True)

# --- 2. API & DATA PARSING ---
@st.cache_data(ttl=300)
def fetch_weather(city):
    try:
        curr = requests.get(f"{BASE_URL_CURRENT}appid={API_KEY}&q={city}&units=metric", timeout=5).json()
        if curr.get("cod") != 200: return None, None
        
        forecast = requests.get(f"{BASE_URL_FORECAST}appid={API_KEY}&q={city}&units=metric", timeout=5).json()
        return curr, forecast
    except:
        return None, None

def parse_daily_forecast(forecast_data):
    # Group the 3-hour chunks into daily high/lows
    daily = {}
    for item in forecast_data['list']:
        date_str = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
        if date_str not in daily:
            daily[date_str] = {
                'temp_max': item['main']['temp_max'],
                'temp_min': item['main']['temp_min'],
                'icon': item['weather'][0]['main'],
                'dt': item['dt']
            }
        else:
            daily[date_str]['temp_max'] = max(daily[date_str]['temp_max'], item['main']['temp_max'])
            daily[date_str]['temp_min'] = min(daily[date_str]['temp_min'], item['main']['temp_min'])
    return list(daily.values())[1:6] # Return next 5 days

def get_icon(condition):
    icons = {"Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️", "Drizzle": "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️", "Mist": "🌫️"}
    return icons.get(condition, "🌡️")

# --- 3. UI RENDERING ---
inject_accuweather_css()

# Top Search Bar Nav
st.markdown('<div class="search-container">', unsafe_allow_html=True)
col_logo, col_search, col_space = st.columns([1, 2, 5])
with col_logo:
    st.markdown("<h2 style='color: #F05514; margin:0; font-weight: 900;'>AW PRO</h2>", unsafe_allow_html=True)
with col_search:
    city_input = st.text_input("", placeholder="Search city, zip code...", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if city_input:
    curr, forecast = fetch_weather(city_input)
    
    if curr and forecast:
        # Core Current Data
        temp = round(curr['main']['temp'])
        rf = round(curr['main']['feels_like'])
        desc = curr['weather'][0]['description']
        icon = get_icon(curr['weather'][0]['main'])
        
        # Grid Data
        wind = round(curr['wind']['speed'] * 3.6)
        gusts = round(curr.get('wind', {}).get('gust', 0) * 3.6)
        humidity = curr['main']['humidity']
        pressure = curr['main']['pressure']
        visibility = round(curr.get('visibility', 0) / 1000, 1)
        clouds = curr['clouds']['all']
        
        # Calculate Dew Point (Approximation)
        dew_point = round(temp - ((100 - humidity) / 5))

        # --- LAYOUT: 70% MAIN / 30% SIDEBAR ---
        main_col, side_col = st.columns([7, 3.5])

        with main_col:
            # 1. CURRENT WEATHER CARD (Information Dense)
            st.markdown(f"""
            <div class="aw-card">
                <div class="aw-card-header">CURRENT WEATHER • {curr['name'].upper()}</div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    
                    <!-- Left Side: Hero Temp -->
                    <div style="flex: 1;">
                        <div class="current-temp-block">
                            <div class="current-icon">{icon}</div>
                            <div>
                                <div class="current-temp">{temp}°<span style="font-size: 3rem; color: #888;">C</span></div>
                                <div class="current-realfeel">RealFeel® {rf}°</div>
                            </div>
                        </div>
                        <div class="current-desc">{desc}</div>
                    </div>
                    
                    <!-- Right Side: Data Grid -->
                    <div style="flex: 1;">
                        <div class="details-grid">
                            <div class="detail-item"><span class="detail-label">Wind</span><span class="detail-value">{wind} km/h</span></div>
                            <div class="detail-item"><span class="detail-label">Wind Gusts</span><span class="detail-value">{gusts if gusts > 0 else '--'} km/h</span></div>
                            <div class="detail-item"><span class="detail-label">Humidity</span><span class="detail-value">{humidity}%</span></div>
                            <div class="detail-item"><span class="detail-label">Dew Point</span><span class="detail-value">{dew_point}° C</span></div>
                            <div class="detail-item"><span class="detail-label">Pressure</span><span class="detail-value">{pressure} mb</span></div>
                            <div class="detail-item"><span class="detail-label">Cloud Cover</span><span class="detail-value">{clouds}%</span></div>
                            <div class="detail-item"><span class="detail-label">Visibility</span><span class="detail-value">{visibility} km</span></div>
                            <div class="detail-item"><span class="detail-label">Max UV Index</span><span class="detail-value">3 (Moderate)</span></div>
                        </div>
                    </div>
                    
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 2. HOURLY FORECAST CHART (Utility visualization)
            times = [datetime.fromtimestamp(item['dt']).strftime('%-I %p') for item in forecast['list'][:10]]
            temps = [round(item['main']['temp']) for item in forecast['list'][:10]]
            precip = [round(item.get('pop', 0) * 100) for item in forecast['list'][:10]]

            st.markdown('<div class="aw-card"><div class="aw-card-header">HOURLY FORECAST</div>', unsafe_allow_html=True)
            
            fig = go.Figure()
            # Temperature Line
            fig.add_trace(go.Scatter(x=times, y=temps, name="Temperature", mode='lines+markers+text',
                                     text=[f"{t}°" for t in temps], textposition="top center",
                                     line=dict(color='#F05514', width=3),
                                     marker=dict(size=8, color='#F05514')))
            # Precipitation Bars (Secondary axis style, handled via scale)
            fig.add_trace(go.Bar(x=times, y=precip, name="Precipitation %", marker_color='rgba(0, 150, 255, 0.2)'))
            
            fig.update_layout(
                height=250, margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, color='#999'),
                yaxis=dict(showgrid=True, gridcolor='#333', visible=False),
                showlegend=False, hovermode="x unified", barmode='overlay'
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

        with side_col:
            # 3. RIGHT SIDEBAR: 5-DAY ADVANCE
            daily_data = parse_daily_forecast(forecast)
            
            list_html = '<div class="aw-card"><div class="aw-card-header">5-DAY FORECAST</div>'
            for day in daily_data:
                day_name = datetime.fromtimestamp(day['dt']).strftime('%a, %b %d')
                high_t = round(day['temp_max'])
                low_t = round(day['temp_min'])
                d_icon = get_icon(day['icon'])
                
                list_html += f"""
                <div class="daily-row">
                    <div class="day-date">{day_name.upper()}</div>
                    <div class="day-icon">{d_icon}</div>
                    <div class="day-temps">{high_t}° <span class="low-temp">/ {low_t}°</span></div>
                </div>
                """
            list_html += "</div>"
            st.markdown(list_html, unsafe_allow_html=True)

            # 4. RIGHT SIDEBAR: QUICK INSIGHTS
            st.markdown(f"""
            <div class="aw-card" style="border-top: 3px solid #F05514;">
                <div class="aw-card-header">LOOKING AHEAD</div>
                <h3 style="margin: 0 0 10px 0; font-size: 1.4rem;">Expect {daily_data[0]['icon']}</h3>
                <p style="color: #CCC; font-size: 0.95rem; line-height: 1.5;">
                    Current conditions indicate {desc} with a RealFeel of {rf}°. 
                    Winds are blowing at {wind} km/h. Moving into tomorrow, expect highs around {round(daily_data[0]['temp_max'])}°.
                </p>
                <div style="margin-top: 15px; font-size: 0.85rem; color: #999;">
                    Last updated: {datetime.now().strftime('%H:%M %p')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.error("Data retrieval failed. Please check the city name.")
else:
    # Empty State Dashboard
    st.markdown("""
    <div style="text-align: center; padding: 100px 0;">
        <h2 style="color: #555;">Enter a location above to view detailed meteorological data.</h2>
    </div>
    """, unsafe_allow_html=True)
