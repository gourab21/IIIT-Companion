import pandas as pd
import requests
from icalendar import Calendar
from datetime import datetime, date
import os

# --- CONFIGURATION ---
# 🔴 PASTE YOUR SECRET GOOGLE CALENDAR LINK BELOW 🔴
ICAL_URL = "https://calendar.google.com/calendar/ical/YOUR_SECRET_ADDRESS/basic.ics"

# --- 1. STATIC DATA (Menu & Bus) ---
breakfast_data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Main": ["Uppma & Sheera / Vermicelli Upma", "Poha", "Methi Paratha / Palak Paratha", "Idli Wada", "Poori", "Masala Dosa / Uttapam", "Aloo Gobi Paratha"],
    "Sides": ["Green Chutney, Boiled Peanuts", "Sev / Namkin Tari, Boiled Sweet Corn", "Veg Korma, Matki Sprouts, Egg Bhurji", "Sambar / Chutney, Chana Sprouts, Boiled Egg", "Aloo Sabji, Green Moong Sprouts", "Sambar / Chutney, Matki Sprouts, Egg Bhurji", "Curd / Pickle, Green Moong Sprouts"],
    "Extra": ["Coffee / Tea / Bournvita"] * 7
}

lunch_data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Main": ["Onion Rice, Plain Rice", "Fried Rice / Bagara Rice, Plain Rice", "Curd Rice, Plain Rice", "Puliogre, Plain Rice", "Veg Biryani, Plain Rice", "Curd Rice, Plain Rice", "Paneer Butter Masala (Main)"],
    "Sides": ["Dal Tadka, Rasam, Jeera Aloo, Dal Panchratna", "Dal Fry, Sambhar, Tondli Chana Dry, Manchurian Gravy", "Dal Methi, Rasam, Aloo Brinjal Tomato, Paneer Kolhapuri", "Dal Fry, Sambhar, Black Chana Masala, Soyabean Sabji", "Mix Veg Raitha, Aloo Gobi Dry, Chhole Masala", "Dal Palak, Mix Veg Dry, Egg Curry", "Paneer Butter Masala"],
    "Extra": ["Jaljeera, Curd, Salad, Papad", "Rasna, Curd, Salad, Papad", "Butter Milk, Salad, Papad", "Lassi, Curd, Salad, Papad", "Lemon Juice, Salad, Papad", "Hot Badam Milk, Salad, Papad", "Kokam Sarbat, Salad, Papad"]
}

snacks_data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Main": ["Samosa", "Bread Pakoda / Veg Sandwich", "Veg Hakka Noodles / Maggi", "Vada Pav", "Pav Bhaji", "Masala Bhel", "Veg Cutlet"],
    "Sides": ["Red & Green Chutney", "Green & Red Chutney", "Tomato Sauce", "Green Chutney", "Chopped Onion & Lemon", "Red/Green Chutney, Onion", "Tomato Sauce / Green Chutney"],
    "Extra": ["Milk/Fruits, BBJ, Tea/Coffee"] * 7
}

dinner_data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Main": ["Khichadi / Bisibele Bath", "Plain Rice", "Jeera Rice", "Tomato Rice", "Onion Masala Rice", "Plain Rice", "Moong Dal Halwa / Badam Poori (Special)"],
    "Sides": ["Bhendi Sabzi, Paneer Hyderabadi, Dal Panchratna", "Veg Kadhai, Channa Dal", "Aloo Sabji, Lauki Kofta Masala, Dal Makhani", "Aloo Sabji, Paneer Butter Masala, Dal Kolhapuri", "Bhendi Sabzi, Rajma Masala, Dal Tadka", "Aloo Beans Fry, Mushroom Masala, Moong Dal", "Moong Dal Halwa / Badam Poori"],
    "Extra": ["Shevai Kheer", "Ice Cream / Kulfi", "Pineapple Sheera / Badusha", "Motichoor Ladoo", "Gulab Jamun", "Ice Cream / Kulfi", "Moong Dal Halwa / Badam Poori"]
}

bus_data = {
    "Time": ["7:30am", "7:30am", "8:00am", "8:00am", "8:25am", "8:45am", "10:00am", "10:40am", "11:20am", "12:00pm", "2:00pm", "2:40pm", "3:20pm", "4:00pm", "5:30pm", "5:30pm", "6:20pm", "7:00pm", "7:40pm", "8:20pm", "9:00pm", "10:00pm", "10:30pm", "11:15pm", "11:40pm"],
    "Pickup": ["Campus", "Campus", "Transit hostel", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel"],
    "Drop": ["Transit hostel", "Transit hostel", "Campus", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus"],
    "BusName": ["Institute Bus 1", "Institute Bus 2", "Institute Bus 1", "Institute Bus 2", "Institute Bus 1", "Institute Bus 1", "Institute Bus 2", "Institute Bus 2", "Institute Bus 2", "Institute Bus 2", "Institute Bus 2", "Institute Bus 2", "Institute Bus 2", "Institute Bus 2", "Institute Bus 2", "Institute Bus 1", "Institute Bus 1", "Institute Bus 1", "Institute Bus 1", "Institute Bus 1", "Institute Bus 1", "Institute Bus 1", "Institute Bus 1", "Institute Bus 1", "Institute Bus 1"]
}

# --- 2. DYNAMIC DATA (Google Calendar) ---
def get_calendar_events():
    events_data = []
    print("Fetching Calendar data...")
    try:
        response = requests.get(ICAL_URL)
        response.raise_for_status()
        
        cal = Calendar.from_ical(response.content)
        today = date.today()
        
        for component in cal.walk():
            if component.name == "VEVENT":
                summary = str(component.get('summary'))
                start = component.get('dtstart').dt
                
                # Handle timezone awareness
                if hasattr(start, 'date'):
                    # It's a datetime
                    event_date = start.date()
                    # Convert to simple string time for CSV
                    time_str = start.strftime("%I:%M %p")
                else:
                    # It's just a date (All day event)
                    event_date = start
                    time_str = "All Day"
                
                # Keep events from today onwards (optional: keep history? let's stick to future/today)
                if event_date >= today:
                    events_data.append({
                        "Date": event_date.strftime("%Y-%m-%d"),
                        "Day": event_date.strftime("%A"),
                        "Time": time_str,
                        "Event": summary
                    })
                    
        # Sort by date
        events_data.sort(key=lambda x: x["Date"])
        
    except Exception as e:
        print(f"⚠️ Error fetching calendar: {e}")
        # Create a dummy entry so the CSV isn't empty (prevents JS errors)
        events_data.append({"Date": datetime.now().strftime("%Y-%m-%d"), "Day": "Error", "Time": "--", "Event": "Could not sync calendar"})

    return pd.DataFrame(events_data)

# --- 3. GENERATE CSVs ---

# Menu
df_b = pd.DataFrame(breakfast_data); df_b["Type"] = "Breakfast"
df_l = pd.DataFrame(lunch_data); df_l["Type"] = "Lunch"
df_s = pd.DataFrame(snacks_data); df_s["Type"] = "Snacks"
df_d = pd.DataFrame(dinner_data); df_d["Type"] = "Dinner"
df_menu = pd.concat([df_b, df_l, df_s, df_d], ignore_index=True)
df_menu.to_csv("menu_data.csv", index=False)

# Bus
df_bus = pd.DataFrame(bus_data)
df_bus.to_csv("bus_data.csv", index=False)

# Calendar
df_events = get_calendar_events()
df_events.to_csv("events_data.csv", index=False)

print("✅ Success! Updated: menu_data.csv, bus_data.csv, events_data.csv")