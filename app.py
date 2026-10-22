import streamlit as st
import requests
import math
import time
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="Disneyland Pro Master", page_icon="v", layout="centered")

# עיצוב מתקדם לנייד
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.2em; font-size: 16px; font-weight: bold; background-color: #1E3A8A; color: white; }
    .ride-card { padding: 15px; border-radius: 12px; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 12px; border-right: 6px solid #3B82F6; }
    .combo-card { padding: 15px; border-radius: 12px; background-color: #ECFDF5; border-right: 6px solid #10B981; margin-bottom: 15px; }
    .alert-card { padding: 15px; border-radius: 12px; background-color: #FEF3C7; border-right: 6px solid #D97706; margin-bottom: 15px; }
    </style>
""", unsafe_allow_index=True)

st.title("Disneyland VIP Router")
st.caption("גרסה אסטרטגית מורחבת למניעת תורים ומקסום זמן")

# שמירת היסטוריית תורים קצרה בזיכרון האפליקציה לצורך חיזוי מגמה
if "history" not in st.session_state:
    st.session_state.history = {}

# מאגר המתקנים והמיקומים
RIDE_LOCATIONS = {
    "big_thunder_mountain": {"name": "Big Thunder Mountain", "lat": 48.8712, "lon": 2.7752, "park": "Disneyland Park", "best_hours": "ערב/בוקר מוקדם"},
    "hyperspace_mountain": {"name": "Space Mountain", "lat": 48.8745, "lon": 2.7798, "park": "Disneyland Park", "best_hours": "זמן תהלוכה/ערב"},
    "peter_pan": {"name": "Peter Pan's Flight", "lat": 48.8743, "lon": 2.7761, "park": "Disneyland Park", "best_hours": "שעה ראשונה/אחרונה"},
    "pirates": {"name": "Pirates of the Caribbean", "lat": 48.8748, "lon": 2.7735, "park": "Disneyland Park", "best_hours": "צהריים/כל היום"},
    "buzz": {"name": "Buzz Lightyear Laser", "lat": 48.8740, "lon": 2.7792, "park": "Disneyland Park", "best_hours": "אחר הצהריים"},
    "ratatouille": {"name": "Ratatouille: The Adventure", "lat": 48.8668, "lon": 2.7778, "park": "Walt Disney Studios", "best_hours": "בוקר מוקדם"},
    "tower_of_terror": {"name": "Tower of Terror", "lat": 48.8681, "lon": 2.7790, "park": "Walt Disney Studios", "best_hours": "ערב"},
    "rc_racer": {"name": "RC Racer", "lat": 48.8660, "lon": 2.7795, "park": "Walt Disney Studios", "best_hours": "זמן ארוחת צהריים"}
}

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    p = math.pi / 180
    a = 0.5 - math.cos((lat2 - lat1) * p)/2 + math.cos(lat1 * p) * math.cos(lat2 * p) * (1 - math.cos((lon2 - lon1) * p)) / 2
    return R * 2 * math.asin(math.sqrt(a))

def get_all_live_data():
    urls = {
        "Disneyland Park": "https://themeparks.wiki",
        "Walt Disney Studios": "https://themeparks.wiki"
    }
    wait_times = {}
    for park_name, url in urls.items():
        try:
            data = requests.get(url, timeout=5).json().get('liveData', [])
            for entity in data:
                if entity.get('status') == 'OPERATING':
                    name_key = entity.get('name', '').lower()
                    wait_times[name_key] = entity.get('queue', {}).get('STANDBY', {}).get('waitTime', 999)
        except:
            pass
    return wait_times

# עדכון היסטוריה לצורך זיהוי מגמות
live_wait_times = get_all_live_data()
current_time = time.time()
for k, v in live_wait_times.items():
    if k not in st.session_state.history:
        st.session_state.history[k] = []
    st.session_state.history[k].append((current_time, v))
    st.session_state.history[k] = [item for item in st.session_state.history[k] if current_time - item 
            <b>הזדמנות חטופה!</b> המתקן <b>{entity_name.title()}</b> פנוי לחלוטין: <b>{minutes} דקות המתנה בלבד!</b>
        </div>
        """, unsafe_allow_index=True)
        alert_triggered = True

if alert_triggered:
    st.components.v1.html('<audio autoplay><source src="https://mixkit.co" type="audio/wav"></audio>', height=0)
else:
    st.caption("אין כרגע מתקנים מתחת ל-5 דקות. המנוע סורק ברקע...")

st.write("---")

# --- 2. מנוע הניווט והאופטימיזציה ---
st.subheader("מנוע החישוב האסטרטגי")
loc = get_geolocation()

if loc:
    user_lat = loc['coords']['latitude']
    user_lon = loc['coords']['longitude']
    
    selected_keys = []
    with st.expander("בחר אילו מתקנים ברשימה שלך היום", expanded=False):
        for key, data in RIDE_LOCATIONS.items():
            if st.checkbox(f"{data['name']} ({data['park']})", value=True, key=f"v2_{key}"):
                selected_keys.append(key)

    if st.button("חשב מסלול עוקף תורים", type="primary"):
        processed_rides = []
        
        for key in selected_keys:
            ride = RIDE_LOCATIONS[key]
            
            wait_time = 15
            for api_name, minutes in live_wait_times.items():
                if key in api_name or ride["name"].lower()[:6] in api_name:
                    wait_time = minutes
                    break
            
            trend_icon = "Stable"
            history_list = st.session_state.history.get(key, [])
            if len(history_list) > 1:
                old_wait = history_list[0][1]
                if wait_time < old_wait:
                    trend_icon = "התור בירידה!"
                    wait_time -= 3
                elif wait_time > old_wait:
                    trend_icon = "התור בעלייה"
                    wait_time += 3
            
            distance = calculate_distance(user_lat, user_lon, ride["lat"], ride["lon"])
            walk_time = (distance / 1.2) / 60
            total_score = wait_time + walk_time
            
            processed_rides.append({
                "key": key, "name": ride["name"], "park": ride["park"],
                "wait": wait_time, "walk": round(walk_time), "score": total_score,
                "trend": trend_icon, "tip": ride["best_hours"], "lat": ride["lat"], "lon": ride["lon"]
            })
            
        if processed_rides:
            sorted_rides = sorted(processed_rides, key=lambda x: x["score"])
            
            st.markdown("### המסלול המשולב הכי משתלם (ה-Combo):")
            best_ride = sorted_rides[0]
            
            best_combo_partner = None
            min_combo_score = float('inf')
            
            for other in sorted_rides[1:]:
                dist_between = calculate_distance(best_ride["lat"], best_ride["lon"], other["lat"], other["lon"])
                walk_between = (dist_between / 1.2) / 60
                combo_score = other["wait"] + walk_between
                
                if combo_score < min_combo_score:
                    min_combo_score = combo_score
                    best_combo_partner = other
            
            if best_combo_partner:
                st.markdown(f"""
                <div class="combo-card">
                    <b>תוכנית פעולה מנצחת לשעה הקרובה:</b><br>
                    1. לכו עכשיו ל-<b>{best_ride['name']}</b> ({best_ride['wait']} דק' תור + {best_ride['walk']} דק' הליכה ממכם).<br>
                    2. מיד כשאתם יוצאים, המשיכו ישירות ל-<b>{best_combo_partner['name']}</b> שנמצא ממש צמוד אליו!
                </div>
                """, unsafe_allow_index=True)
            
            st.markdown("### מדד כדאיות שאר המתקנים:")
            for res in sorted_rides:
                st.markdown(f"""
                <div class="ride-card">
                    <b>{res['name']}</b> ({res['park']})<br>
                    זמן המתנה: <b>{res['wait']} דק'</b> ({res['trend']})<br>
                    הליכה אליו: <b>{res['walk']} דק'</b><br>
                    שעות הכי פחות עמוסות בדרך כלל: <u>{res['tip']}</u>
                </div>
                """, unsafe_allow_index=True)
else:
    st.info("אנא אשר גישת GPS בנייד כדי שהמערכת תחשב ותבנה לך את מסלולי ה-Combo החכמים.")
