import streamlit as st
import requests
import math
import time
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="Disneyland Pro Master", page_icon="v", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.2em; font-size: 16px; font-weight: bold; background-color: #1E3A8A; color: white; }
    .ride-card { padding: 15px; border-radius: 12px; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 12px; border-right: 6px solid #3B82F6; text-align: right; direction: rtl; }
    .combo-card { padding: 15px; border-radius: 12px; background-color: #ECFDF5; border-right: 6px solid #10B981; margin-bottom: 15px; text-align: right; direction: rtl; }
    .alert-card { padding: 15px; border-radius: 12px; background-color: #FEF3C7; border-right: 6px solid #D97706; margin-bottom: 15px; text-align: right; direction: rtl; }
    </style>
""", unsafe_allow_html=True)

st.title("Disneyland VIP Router")
st.caption("מנווט אסטרטגי עוקף תורים")

RIDE_LOCATIONS = {
    "big_thunder_mountain": {"name": "Big Thunder Mountain", "lat": 48.8712, "lon": 2.7752, "park": "Disneyland Park", "best_hours": "ערב או בוקר מוקדם"},
    "hyperspace_mountain": {"name": "Space Mountain", "lat": 48.8745, "lon": 2.7798, "park": "Disneyland Park", "best_hours": "זמן תהלוכה או ערב"},
    "peter_pan": {"name": "Peter Pan's Flight", "lat": 48.8743, "lon": 2.7761, "park": "Disneyland Park", "best_hours": "שעה ראשונה או אחרונה"},
    "pirates": {"name": "Pirates of the Caribbean", "lat": 48.8748, "lon": 2.7735, "park": "Disneyland Park", "best_hours": "צהריים או כל היום"},
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

live_wait_times = get_all_live_data()

st.markdown("### התראות בזק חמות")
alert_triggered = False
for entity_name, minutes in live_wait_times.items():
    if minutes <= 5:
        st.markdown(f'<div class="alert-card"><b>הזדמנות חטופה!</b> המתקן <b>{entity_name.title()}</b> פנוי לחלוטין: <b>{minutes}</b> דקות המתנה בלבד!</div>', unsafe_allow_html=True)
        alert_triggered = True

if not alert_triggered:
    st.caption("אין כרגע מתקנים מתחת ל-5 דקות. המנוע סורק ברקע...")

st.write("---")
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
            
            distance = calculate_distance(user_lat, user_lon, ride["lat"], ride["lon"])
            walk_time = (distance / 1.2) / 60
            total_score = wait_time + walk_time
            
            processed_rides.append({
                "key": key, "name": ride["name"], "park": ride["park"],
                "wait": wait_time, "walk": round(walk_time), "score": total_score,
                "tip": ride["best_hours"], "lat": ride["lat"], "lon": ride["lon"]
            })
            
        if processed_rides:
            sorted_rides = sorted(processed_rides, key=lambda x: x["score"])
            best_ride = sorted_rides[0]
            
            st.markdown("### המסלול המשולב הכי משתלם (ה-Combo):")
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
                st.markdown(f'<div class="combo-card"><b>תוכנית פעולה מנצחת לשעה הקרובה:</b><br>1. לכו עכשיו ל-<b>{best_ride["name"]}</b> ({best_ride["wait"]} דקות תור).<br>2. מיד כשאתם יוצאים, המשיכו ישירות ל-<b>{best_combo_partner["name"]}</b> שנמצא ממש צמוד אליו!</div>', unsafe_allow_html=True)
            
            st.markdown("### מדד כדאיות שאר המתקנים:")
            for res in sorted_rides:
                st.markdown(f'<div class="ride-card"><b>{res["name"]}</b> ({res["park"]})<br>זמן המתנה משוער: <b>{res["wait"]} דקות</b><br>זמן הליכה משוער: <b>{res["walk"]} דקות</b><br>שעות מומלצות בדרך כלל: {res["tip"]}</div>', unsafe_allow_html=True)
else:
    st.info("אנא אשר גישת GPS בנייד כדי שהמערכת תחשב ותבנה לך את מסלולי ה-Combo החכמים.")
