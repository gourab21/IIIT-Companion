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
# Rule: Main = all food (rice, dal, curry, sabzi, sprouts,
#               eggs, fruits, BBJ, sweets, drinks like milk etc.)
#        Sides = only chutney / pickle / salad / lemon /
#                beverages (Tea, Coffee, Bournvita, Ginger Tea)
# ==========================================================

breakfast_data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Main": [
        # Monday
        "Pongal, Poha Sev, Black Chana Sprouts, Egg Bhurji, Fruits / Cornflakes, BBJ",
        # Tuesday
        "Aloo Paratha, Boiled Sweet Corn, Boiled Egg, Fruits / Cornflakes, BBJ",
        # Wednesday
        "Upma / Sewaiya Upma, Sheera, Matki Sprouts, Egg Bhurji, Fruits / Cornflakes, BBJ",
        # Thursday
        "Idli, Vada, Boiled Groundnut, Boiled Egg, Fruits / Cornflakes, BBJ",
        # Friday
        "Masala Dosa, Green Moong Sprouts, Egg Bhurji, Fruits / Cornflakes, BBJ",
        # Saturday
        "Methi / Palak Paratha, Veg Korma, Matki Sprouts, Egg Bhurji, Fruits / Cornflakes, BBJ",
        # Sunday
        "Methi Poori, Chhole Masala, Green Moong Sprouts, Fruits / Cornflakes, BBJ"
    ],
    "Sides": [
        "Chutney, Tea / Coffee / Bournvita",           # Monday
        "Sambar & Chutney, Tea / Coffee / Bournvita",  # Tuesday
        "Chutney, Tea / Coffee / Bournvita",           # Wednesday
        "Sambar & Chutney, Tea / Coffee / Bournvita",  # Thursday
        "Sambar & Chutney, Tea / Coffee / Bournvita",  # Friday
        "Chutney, Tea / Coffee / Bournvita",           # Saturday
        "Chutney, Tea / Coffee / Bournvita"            # Sunday
    ]
}

lunch_data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Main": [
        # Monday
        "Onion Rice, Plain Rice, Dal Tadka, Jeera Aloo, Chawli Masala, Jaleera, Curd, Papad, Mix Salad",
        # Tuesday
        "Aloo 65, Veg Pulav, Plain Rice, Dal Fry, Puri, Lemonade, Papad, Mix Salad",
        # Wednesday
        "Curd Rice, Plain Rice, Dal Methi, Paneer Kolhapuri, Butter Milk, Papad, Mix Salad",
        # Thursday
        "Puliogare, Plain Rice, Dal Fry, Aloo Brinjal Tomato, Kadhi Pakoda, Lassi, Papad, Mix Salad",
        # Friday
        "Veg & Egg Biryani, Plain Rice, Dal Fry, Mix Veg Raitha, Black Chana Masala, Curd, Papad, Mix Salad",
        # Saturday
        "Curd Rice, Plain Rice, Dal Palak, Mix Veg Dry, Egg Curry, Hot Badam Milk, Papad, Mix Salad",
        # Sunday
        "Dal Palak, Plain Rice, Paneer Butter Masala, Egg Curry, Kadhi Sambhath, Papad, Mix Salad"
    ],
    "Sides": [
        "Green Chilli / Lemon",   # Monday
        "Green Chilli / Lemon",   # Tuesday
        "Green Chilli / Lemon",   # Wednesday
        "Green Chilli / Lemon",   # Thursday
        "Green Chilli / Lemon",   # Friday
        "Green Chilli / Lemon",   # Saturday
        "Green Chilli / Lemon"    # Sunday
    ]
}

snacks_data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Main": [
        "Samosa / Dhokla, Fruits",                     # Monday
        "Pani Puri (9 Pieces), Fruits",                # Tuesday
        "Veg Noodles, Fruits",                         # Wednesday
        "Onion / Aloo Pakoda, Fruits",                 # Thursday
        "Pav Bhaji, Chopped Onion & Lemon, Fruits",    # Friday
        "Masala Bhel, Fruits",                         # Saturday
        "Veg Cutlet, Fruits"                           # Sunday
    ],
    "Sides": [
        "Red & Green Chutney, BBJ, Ginger Tea / Milk",   # Monday
        "Red & Green Chutney, BBJ, Ginger Tea / Milk",   # Tuesday
        "Red & Green Chutney, BBJ, Ginger Tea / Milk",   # Wednesday
        "Red & Green Chutney, BBJ, Ginger Tea / Milk",   # Thursday
        "Red & Green Chutney, BBJ, Ginger Tea / Milk",   # Friday
        "Red & Green Chutney, BBJ, Ginger Tea / Milk",   # Saturday
        "Red & Green Chutney, BBJ, Ginger Tea / Milk"    # Sunday
    ]
}

dinner_data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Main": [
        # Monday
        "Plain Rice, Rasam, Paneer Hyderabadi, Dal Panchratna, Bhindi Sabzi, Chapati / Fulka, Mix Salad",
        # Tuesday
        "Plain Rice, Veg Kadai, Channa Dal, Babisha, Ice Cream (Variety of Flavours), Chapati / Fulka, Mix Salad",
        # Wednesday
        "Khichadi / Bisibele Bath, Turri Masala, Lauki Kofta Masala, Dal Makhani & Rasam, Shevak Kheer, Chapati / Fulka, Mix Salad",
        # Thursday
        "Jeera Rice, Plain Rice, Paneer Butter Masala, Dal Kolhapuri, Aloo Sabji, Mothichoor Ladoo, Chapati / Fulka, Mix Salad",
        # Friday
        "Tomato Rice, Plain Rice, Rajma Masala, Dal Tadka, Aloo 65, Gulab Jamun, Chapati / Fulka, Mix Salad",
        # Saturday
        "Onion Rice, Plain Rice, Aloo Gobi Mutter, Mushroom Masala, Moong Dal, Ice Cream (Variety of Flavours), Chapati / Fulka, Mix Salad",
        # Sunday
        "Jeera Rice, Plain Rice, Aloo Beans, Mushroom Masala, Moong Dal, Jalebi, Chapati / Fulka, Mix Salad"
    ],
    "Sides": [
        "Pickle, Green Chilli / Lemon Slice",   # Monday
        "Pickle, Green Chilli / Lemon Slice",   # Tuesday
        "Pickle, Green Chilli / Lemon Slice",   # Wednesday
        "Pickle, Green Chilli / Lemon Slice",   # Thursday
        "Pickle, Green Chilli / Lemon Slice",   # Friday
        "Pickle, Green Chilli / Lemon Slice",   # Saturday
        "Pickle, Green Chilli / Lemon Slice"    # Sunday
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
# MEAL TIMES (from board image)
# ==========================================================
meal_times_data = {
    "Day": [
        "Default","Default","Default","Default",  # Normal days
        "Sunday"                                   # Sunday / Govt holiday
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
