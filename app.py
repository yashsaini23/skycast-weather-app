import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION ---
API_KEY = "266429f3bfe7a437941f7b13747d7c83"
BASE_URL_CURRENT = "http://api.openweathermap.org/data/2.5/weather?"
BASE_URL_FORECAST = "http://api.openweathermap.org/data/2.5/forecast?"

st.set_page_config(
    page_title="SkyCast AI | Weather Intelligence",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HTML RENDER HELPER ---
def render_html(html_str):
    cleaned = "".join([line.strip() for line in html_str.split("\n") if line.strip()])
    st.markdown(cleaned, unsafe_allow_html=True)

# --- 1. RESPONSIVE MOBILE-FIRST CSS ARCHITECTURE ---
def inject_skycast_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        background-color: #0F1115;
        color: #E2E8F0;
    }
    .block-container { 
        padding-top: 0.5rem !important; 
        padding-bottom: 1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 1400px; 
    }
    header { visibility: hidden; }

    /* Header & Gradient Branding */
    .search-container {
        background-color: #161920;
        padding: 16px 20px;
        border-bottom: 1px solid #232733;
        margin-bottom: 16px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .brand-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF4B2B 0%, #FF8533 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .brand-tagline {
        color: #64748B;
        font-size: 0.8rem;
        font-weight: 500;
        letter-spacing: 0.3px;
    }

    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: #1A1D26 !important;
        color: #F8FAFC !important;
        border: 1px solid #2E3444 !important;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.95rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #FF4B2B !important;
        box-shadow: 0 0 0 1px #FF4B2B !important;
    }

    /* Weather Cards */
    .aw-card {
        background-color: #161920;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        border: 1px solid #232733;
    }
    .aw-card-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.75rem;
        text-transform: uppercase;
        color: #64748B;
        font-weight: 600;
        margin-bottom: 12px;
        letter-spacing: 1px;
        border-bottom: 1px solid #232733;
        padding-bottom: 8px;
    }

    /* Current Conditions Layout */
    .current-main-flex {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 15px;
    }
    .current-temp-block { display: flex; align-items: center; gap: 14px; }
    .current-icon { font-size: 3.8rem; line-height: 1; }
    .current-temp { 
        font-family: 'Space Grotesk', sans-serif;
        font-size: 4rem; 
        font-weight: 700; 
        line-height: 1; 
        letter-spacing: -2px;
        color: #F8FAFC;
    }
    .current-realfeel { font-size: 0.9rem; font-weight: 500; color: #FF7B54; margin-top: 4px; }
    .current-desc { font-size: 1rem; font-weight: 400; text-transform: capitalize; color: #94A3B8; margin-top: 6px; }

    /* Grid Items */
    .details-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px 20px;
        border-left: 1px solid #232733;
        padding-left: 20px;
    }
    .detail-item { 
        display: flex; 
        justify-content: space-between; 
        font-size: 0.85rem; 
        border-bottom: 1px solid #1E222D; 
        padding-bottom: 4px; 
    }
    .detail-label { color: #64748B; font-weight: 400; }
    .detail-value { font-weight: 600; color: #E2E8F0; text-align: right; }

    /* Daily Rows */
    .daily-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 9px 0;
        border-bottom: 1px solid #1E222D;
    }
    .day-date { width: 38%; font-weight: 500; font-size: 0.85rem; color: #CBD5E1; }
    .day-icon { width: 20%; font-size: 1.1rem; text-align: center; }
    .day-temps { width: 42%; text-align: right; font-weight: 600; font-size: 0.95rem; color: #F8FAFC; }
    .low-temp { color: #64748B; font-weight: 400; margin-left: 4px; }

    /* --- MOBILE RESPONSIVE OVERRIDES --- */
    @media (max-width: 768px) {
        .search-container {
            flex-direction: column;
            align-items: flex-start;
            gap: 4px;
            padding: 14px;
        }
        .brand-title { font-size: 1.6rem; }
        .brand-tagline { font-size: 0.75rem; }
        
        .current-main-flex {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
        }
        .details-grid {
            width: 100%;
            grid-template-columns: 1fr 1fr;
            border-left: none;
            padding-left: 0;
            border-top: 1px solid #232733;
            padding-top: 12px;
        }
        .current-temp { font-size: 3.2rem; }
        .current-icon { font-size: 3rem; }
        .aw-card { padding: 14px; }
    }
    </style>
    """
    render_html(css)

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
    return list(daily.values())[1:6]

def get_icon(condition):
    icons = {"Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️", "Drizzle": "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️", "Mist": "🌫️"}
    return icons.get(condition, "🌡️")

# --- 3. UI RENDERING ---
inject_skycast_css()

# Header Section
render_html("""
<div class="search-container">
    <div>
        <h1 class="brand-title">SKYCAST AI</h1>
    </div>
    <div class="brand-tagline">ATMOSPHERIC INTELLIGENCE ENGINE</div>
</div>
""")

city_input = st.text_input("", placeholder="Search city (e.g. Chía, London, New York)...", label_visibility="collapsed")

if city_input:
    curr, forecast = fetch_weather(city_input)
    
    if curr and forecast:
        temp = round(curr['main']['temp'])
        rf = round(curr['main']['feels_like'])
        desc = curr['weather'][0]['description']
        icon = get_icon(curr['weather'][0]['main'])
        
        wind = round(curr['wind']['speed'] * 3.6)
        gusts = round(curr.get('wind', {}).get('gust', 0) * 3.6)
        humidity = curr['main']['humidity']
        pressure = curr['main']['pressure']
        visibility = round(curr.get('visibility', 0) / 1000, 1)
        clouds = curr['clouds']['all']
        dew_point = round(temp - ((100 - humidity) / 5))

        main_col, side_col = st.columns([7, 3.5])

        with main_col:
            # Current Conditions Module
            render_html(f"""
            <div class="aw-card">
                <div class="aw-card-header">CURRENT CONDITIONS • {curr['name'].upper()}</div>
                <div class="current-main-flex">
                    <div style="flex: 1;">
                        <div class="current-temp-block">
                            <div class="current-icon">{icon}</div>
                            <div>
                                <div class="current-temp">{temp}°<span style="font-size: 1.8rem; color: #64748B; font-weight: 400;">C</span></div>
                                <div class="current-realfeel">RealFeel® {rf}°</div>
                            </div>
                        </div>
                        <div class="current-desc">{desc}</div>
                    </div>
                    <div style="flex: 1; width: 100%;">
                        <div class="details-grid">
                            <div class="detail-item"><span class="detail-label">Wind</span><span class="detail-value">{wind} km/h</span></div>
                            <div class="detail-item"><span class="detail-label">Wind Gusts</span><span class="detail-value">{gusts if gusts > 0 else wind} km/h</span></div>
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
            """)

            # Hourly Forecast Module
            times = [datetime.fromtimestamp(item['dt']).strftime('%-I %p') for item in forecast['list'][:10]]
            temps = [round(item['main']['temp']) for item in forecast['list'][:10]]
            precip = [round(item.get('pop', 0) * 100) for item in forecast['list'][:10]]

            render_html("""
            <div class="aw-card">
                <div class="aw-card-header">HOURLY FORECAST</div>
            </div>
            """)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times, y=temps, name="Temperature", mode='lines+markers+text',
                text=[f"{t}°" for t in temps], textposition="top center",
                line=dict(color='#FF4B2B', width=2.5),
                marker=dict(size=6, color='#FF8533')
            ))
            fig.add_trace(go.Bar(x=times, y=precip, name="Precipitation %", marker_color='rgba(255, 75, 43, 0.18)'))
            
            fig.update_layout(
                height=220, margin=dict(l=0, r=0, t=20, b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, color='#64748B'),
                yaxis=dict(showgrid=False, visible=False),
                showlegend=False, hovermode="x unified", barmode='overlay'
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        with side_col:
            # 5-Day Forecast Module
            daily_data = parse_daily_forecast(forecast)
            
            rows_html = ""
            for day in daily_data:
                day_name = datetime.fromtimestamp(day['dt']).strftime('%a, %b %d')
                high_t = round(day['temp_max'])
                low_t = round(day['temp_min'])
                d_icon = get_icon(day['icon'])
                
                rows_html += f'<div class="daily-row"><div class="day-date">{day_name.upper()}</div><div class="day-icon">{d_icon}</div><div class="day-temps">{high_t}° <span class="low-temp">/ {low_t}°</span></div></div>'
            
            render_html(f"""
            <div class="aw-card">
                <div class="aw-card-header">5-DAY FORECAST</div>
                {rows_html}
            </div>
            """)

            # Insights Module
            render_html(f"""
            <div class="aw-card" style="border-top: 2px solid #FF4B2B;">
                <div class="aw-card-header">LOOKING AHEAD</div>
                <h3 style="margin: 0 0 6px 0; font-size: 1rem; font-weight: 600; color: #F8FAFC;">Expect {daily_data[0]['icon']}</h3>
                <p style="color: #94A3B8; font-size: 0.85rem; line-height: 1.4; margin: 0;">
                    Current conditions indicate {desc} with a RealFeel of {rf}°. 
                    Winds are blowing at {wind} km/h. Tomorrow's high will reach around {round(daily_data[0]['temp_max'])}°.
                </p>
                <div style="margin-top: 10px; font-size: 0.75rem; color: #64748B;">
                    Last sync: {datetime.now().strftime('%H:%M %p')}
                </div>
            </div>
            """)

    else:
        st.error("City not found. Please verify spelling.")
else:
    render_html("""
    <div style="text-align: center; padding: 60px 0;">
        <h3 style="color: #475569; font-weight: 500;">Enter a city name above to load atmospheric telemetry.</h3>
    </div>
    """)
