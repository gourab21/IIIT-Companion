"""
Campus App – Unified Data Generator
Runs via GitHub Actions every hour (cron @ 59)
Generates ALL CSVs consumed by frontend
"""

import pandas as pd
import requests
from icalendar import Calendar
from datetime import datetime, date
import pytz

# ==========================================================
# CONFIG
# ==========================================================
ICAL_URL = (
    "https://calendar.google.com/calendar/ical/"
    "gourabdas2128%40gmail.com/"
    "private-17bc218e49cf1837918748bd4eb7282c/basic.ics"
)

# ==========================================================
# MENU DATA
# ==========================================================
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
        "Fried Rice / Bagara Rice, Plain Rice",
        "Curd Rice, Plain Rice",
        "Puliogre, Plain Rice",
        "Veg Biryani, Plain Rice",
        "Curd Rice, Plain Rice",
        "Paneer Butter Masala (Main)"
    ],
    "Sides": [
        "Dal Tadka, Rasam, Jeera Aloo, Dal Panchratna",
        "Dal Fry, Sambhar, Tondli Chana Dry, Manchurian Gravy",
        "Dal Methi, Rasam, Aloo Brinjal Tomato, Paneer Kolhapuri",
        "Dal Fry, Sambhar, Black Chana Masala, Soyabean Sabji",
        "Mix Veg Raitha, Aloo Gobi Dry, Chhole Masala",
        "Dal Palak, Mix Veg Dry, Egg Curry",
        "Paneer Butter Masala"
    ]
}

snacks_data = {
    "Day": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "Main": [
        "Samosa",
        "Bread Pakoda / Veg Sandwich",
        "Veg Hakka Noodles / Maggi",
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
        "Chopped Onion & Lemon",
        "Red/Green Chutney, Onion",
        "Tomato Sauce / Green Chutney"
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
        "Moong Dal Halwa / Badam Poori (Special)"
    ],
    "Sides": [
        "Bhendi Sabzi, Paneer Hyderabadi, Dal Panchratna",
        "Veg Kadhai, Channa Dal",
        "Aloo Sabji, Lauki Kofta Masala, Dal Makhani",
        "Aloo Sabji, Paneer Butter Masala, Dal Kolhapuri",
        "Bhendi Sabzi, Rajma Masala, Dal Tadka",
        "Aloo Beans Fry, Mushroom Masala, Moong Dal",
        "Moong Dal Halwa / Badam Poori"
    ]
}

# ==========================================================
# BUS DATA
# ==========================================================
bus_data = {
    "Time": [
        "7:30am","7:30am","8:00am","8:00am","8:25am","8:45am",
        "10:00am","10:40am","11:20am","12:00pm","2:00pm",
        "2:40pm","3:20pm","4:00pm","5:30pm","5:30pm",
        "6:20pm","7:00pm","7:40pm","8:20pm","9:00pm",
        "10:00pm","10:30pm","11:15pm","11:40pm"
    ],
    "Pickup": [
        "Campus","Campus","Transit hostel","Transit hostel","Campus","Transit hostel",
        "Campus","Transit hostel","Campus","Transit hostel","Campus",
        "Transit hostel","Campus","Transit hostel","Campus","Campus",
        "Transit hostel","Campus","Transit hostel","Campus","Transit hostel",
        "Campus","Transit hostel","Campus","Transit hostel"
    ],
    "Drop": [
        "Transit hostel","Transit hostel","Campus","Campus","Transit hostel","Campus",
        "Transit hostel","Campus","Transit hostel","Campus","Transit hostel",
        "Campus","Transit hostel","Campus","Transit hostel","Transit hostel",
        "Campus","Transit hostel","Campus","Transit hostel","Campus",
        "Transit hostel","Campus","Transit hostel","Campus"
    ],
    "BusName": [
        "Institute Bus 1","Institute Bus 2","Institute Bus 1","Institute Bus 2",
        "Institute Bus 1","Institute Bus 1","Institute Bus 2","Institute Bus 2",
        "Institute Bus 2","Institute Bus 2","Institute Bus 2","Institute Bus 2",
        "Institute Bus 2","Institute Bus 2","Institute Bus 2","Institute Bus 1",
        "Institute Bus 1","Institute Bus 1","Institute Bus 1","Institute Bus 1",
        "Institute Bus 1","Institute Bus 1","Institute Bus 1","Institute Bus 1",
        "Institute Bus 1"
    ]
}

# ==========================================================
# MEAL TIMES (FINAL LOGIC)
# ==========================================================
meal_times_data = {
    "Day": [
        "Default","Default","Default","Default",  # Normal days
        "Sunday"                                 # Sunday / Govt holiday
    ],
    "Type": [
        "Breakfast","Lunch","Snacks","Dinner",
        "Breakfast"
    ],
    "StartTime": [
        "07:45","12:30","16:30","19:30",
        "08:00"
    ],
    "EndTime": [
        "09:15","14:00","17:30","21:00",
        "09:30"
    ]
}

# ==========================================================
# CALENDAR
# ==========================================================
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

    except Exception:
        events.append({
            "Date": today.strftime("%Y-%m-%d"),
            "Day": today.strftime("%A"),
            "Time": "--",
            "Event": "Calendar unavailable"
        })

    return pd.DataFrame(events)

# ==========================================================
# CSV GENERATION
# ==========================================================
def generate_csvs():
    df_menu = pd.concat([
        pd.DataFrame(breakfast_data).assign(Type="Breakfast"),
        pd.DataFrame(lunch_data).assign(Type="Lunch"),
        pd.DataFrame(snacks_data).assign(Type="Snacks"),
        pd.DataFrame(dinner_data).assign(Type="Dinner")
    ], ignore_index=True)

    df_menu.to_csv("menu_data.csv", index=False)
    pd.DataFrame(bus_data).to_csv("bus_data.csv", index=False)
    pd.DataFrame(meal_times_data).to_csv("meal_times.csv", index=False)
    get_calendar_events().to_csv("events_data.csv", index=False)

    print("✅ All CSVs generated successfully")

if __name__ == "__main__":
    generate_csvs()
