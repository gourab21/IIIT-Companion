import pandas as pd
import requests
from icalendar import Calendar
from datetime import datetime, date
import pytz

# ================= CONFIG =================
ICAL_URL = "https://calendar.google.com/calendar/ical/gourabdas2128%40gmail.com/private-17bc218e49cf1837918748bd4eb7282c/basic.ics"

# ================= MENU DATA =================
breakfast_data = {
    "Day": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "Main": [
        "Uppma & Sheera / Vermicelli Upma",
        "Poha",
        "Methi Paratha / Palak Paratha",
        "Idli Wada",
        "Poori",
        "Masala Dosa / Uttapam",
        "Aloo Gobi Paratha"
    ],
    "Sides": [
        "Green Chutney, Boiled Peanuts",
        "Sev / Namkin Tari, Boiled Sweet Corn",
        "Veg Korma, Matki Sprouts, Egg Bhurji",
        "Sambar / Chutney, Chana Sprouts, Boiled Egg",
        "Aloo Sabji, Green Moong Sprouts",
        "Sambar / Chutney, Matki Sprouts, Egg Bhurji",
        "Curd / Pickle, Green Moong Sprouts"
    ]
}

lunch_data = {
    "Day": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "Main": [
        "Onion Rice, Plain Rice",
        "Fried Rice / Bagara Rice",
        "Curd Rice",
        "Puliogre",
        "Veg Biryani",
        "Curd Rice",
        "Paneer Butter Masala"
    ],
    "Sides": [
        "Dal Tadka, Rasam, Jeera Aloo",
        "Dal Fry, Sambhar, Manchurian",
        "Dal Methi, Rasam, Paneer Kolhapuri",
        "Dal Fry, Sambhar, Soyabean Sabji",
        "Mix Veg Raitha, Chhole",
        "Dal Palak, Egg Curry",
        "Paneer Butter Masala"
    ]
}

snacks_data = {
    "Day": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "Main": [
        "Samosa",
        "Bread Pakoda / Veg Sandwich",
        "Veg Noodles / Maggi",
        "Vada Pav",
        "Pav Bhaji",
        "Masala Bhel",
        "Veg Cutlet"
    ],
    "Sides": [
        "Red & Green Chutney",
        "Green & Red Chutney",
        "Tomato Sauce",
        "Green Chutney",
        "Onion & Lemon",
        "Red/Green Chutney",
        "Tomato Sauce"
    ]
}

dinner_data = {
    "Day": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "Main": [
        "Khichadi / Bisibele Bath",
        "Plain Rice",
        "Jeera Rice",
        "Tomato Rice",
        "Onion Masala Rice",
        "Plain Rice",
        "Moong Dal Halwa (Special)"
    ],
    "Sides": [
        "Paneer Hyderabadi, Dal Panchratna",
        "Veg Kadhai, Channa Dal",
        "Lauki Kofta, Dal Makhani",
        "Paneer Butter Masala",
        "Rajma Masala",
        "Mushroom Masala",
        "Moong Dal Halwa"
    ]
}

bus_data = {
    "Time": [
        "7:30am","8:00am","8:25am","8:45am",
        "10:00am","11:20am","12:00pm",
        "2:00pm","3:20pm","4:00pm",
        "5:30pm","6:20pm","7:40pm",
        "9:00pm","10:30pm","11:40pm"
    ],
    "Pickup": [
        "Campus","Transit hostel","Campus","Transit hostel",
        "Campus","Campus","Transit hostel",
        "Campus","Campus","Transit hostel",
        "Campus","Transit hostel","Transit hostel",
        "Campus","Transit hostel","Campus"
    ],
    "Drop": [
        "Transit hostel","Campus","Transit hostel","Campus",
        "Transit hostel","Transit hostel","Campus",
        "Transit hostel","Transit hostel","Campus",
        "Transit hostel","Campus","Campus",
        "Transit hostel","Campus","Transit hostel"
    ],
    "BusName": ["Institute Bus"] * 16
}

# ================= CALENDAR =================
def get_calendar_events():
    events = []
    today = date.today()

    try:
        res = requests.get(ICAL_URL, timeout=20)
        res.raise_for_status()
        cal = Calendar.from_ical(res.content)

        for comp in cal.walk("VEVENT"):
            summary = str(comp.get("summary", "No Title"))
            start = comp.get("dtstart").dt

            if isinstance(start, datetime):
                start = start.astimezone(pytz.UTC)
                event_date = start.date()
                time_str = start.strftime("%I:%M %p")
            else:
                event_date = start
                time_str = "All Day"

            if event_date >= today:
                events.append({
                    "Date": event_date.strftime("%Y-%m-%d"),
                    "Day": event_date.strftime("%A"),
                    "Time": time_str,
                    "Event": summary
                })

    except Exception as e:
        events.append({
            "Date": today.strftime("%Y-%m-%d"),
            "Day": today.strftime("%A"),
            "Time": "--",
            "Event": "Calendar unavailable"
        })

    return pd.DataFrame(events)

# ================= CSV OUTPUT =================
def save_all():
    df_menu = pd.concat([
        pd.DataFrame(breakfast_data).assign(Type="Breakfast"),
        pd.DataFrame(lunch_data).assign(Type="Lunch"),
        pd.DataFrame(snacks_data).assign(Type="Snacks"),
        pd.DataFrame(dinner_data).assign(Type="Dinner")
    ])

    df_menu.to_csv("menu_data.csv", index=False)
    pd.DataFrame(bus_data).to_csv("bus_data.csv", index=False)
    get_calendar_events().to_csv("events_data.csv", index=False)

    print("✅ CSVs updated successfully")

if __name__ == "__main__":
    save_all()
