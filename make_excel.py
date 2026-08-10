import pandas as pd

# --- 1. DEFINE DATA (CLEANED) ---

breakfast_data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Main": [
        "Poha / Sev",
        "Aloo Paratha",
        "Upma / Sewai Upma",
        "Idli / Vada",
        "Masala Dosa",
        "Methi/Palak Paratha",
        "Methi Poori"
    ],
    "Sides": [
        "Chutney, Black Chana Sprouts",
        "Sambar & Chutney, Boiled Sweet Corn",
        "Sheera, Chutney",
        "Sambar & Chutney, Boiled Corn",
        "Sambar & Chutney, Green Moong Sprouts",
        "Veg Korma",
        "Chole Masala, Green Moong Sprouts"
    ]
}

lunch_data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Main": [
        "Onion Rice, Plain Rice",
        "Veg Pulav, Lemon Rice",
        "Curd Rice, Plain Rice",
        "Pulav, Plain Rice",
        "Veg & Egg Biryani, Plain Rice",
        "Dal Palak, Plain Rice",
        "Dal Palak, Plain Rice"
    ],
    "Sides": [
        "Dal Tadka, Jeera Aloo, Chawal Masala, Curd",
        "Aloo 65, Dal Tadka, Puri, Curd",
        "Dal Methi, Paneer Kofta, Butter Milk",
        "Dal Fry, Aloo Bhindi Tomato, Kadhi Pakoda, Lassi",
        "Mix Veg Raita, Black Chana Masala, Lemon Juice",
        "Mix Veg Dry, Chole Bhature, Hot Badam Milk",
        "Paneer Butter Masala, Egg Curry"
    ]
}

snacks_data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Main": [
        "Samosa/Dhokla",
        "Pani Puri",
        "Veg Noodles",
        "Onion Aloo Pakoda",
        "Pav Bhaji",
        "Masala Bhel",
        "Veg Cutlet / Aloo Pakoda"
    ],
    "Sides": [
        "Fruits, Ginger Tea",
        "Fruits",
        "Fruits",
        "Fruits",
        "Fruits, Onion & Lemon",
        "Fruits",
        "Fruits"
    ]
}

dinner_data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Main": [
        "Paneer Hyderabadi",
        "Khichdi/Bisibele Bath",
        "Tawa Masala",
        "Jeera Rice",
        "Tomato Rice",
        "Onion Rice",
        "Aloo Beans"
    ],
    "Sides": [
        "Dal Panchratan, Lauki Bharta, Chapati/Fulka",
        "Veg Kadhi, Chana Dal, Chapati/Fulka",
        "Lauki Kofta Masala, Malvani Rasam, Shevai Kheer, Chapati/Fulka",
        "Paneer Butter Masala, Dal Kolhapuri, Gulab Jamun, Chapati/Fulka",
        "Rajma Masala, Dal Tadka, Gulab Jamun, Chapati/Fulka",
        "Aloo Gobi Mutter, Ice Cream, Chapati/Fulka",
        "Mushroom Masala, Moong Dal, Jalebi, Chapati/Fulka"
    ]
}

# --- 2. CREATE DATAFRAMES ---

df_b = pd.DataFrame(breakfast_data)
df_b["Type"] = "Breakfast"

df_l = pd.DataFrame(lunch_data)
df_l["Type"] = "Lunch"

df_s = pd.DataFrame(snacks_data)
df_s["Type"] = "Snacks"

df_d = pd.DataFrame(dinner_data)
df_d["Type"] = "Dinner"

# Combine all meals
df_menu = pd.concat([df_b, df_l, df_s, df_d], ignore_index=True)

# --- 3. BUS DATA (UNCHANGED) ---

bus_data = {
    "Time": ["7:30am", "7:30am", "8:00am", "8:00am", "8:25am", "8:45am", "10:00am", "10:40am", "11:20am", "12:00pm",
             "2:00pm", "2:40pm", "3:20pm", "4:00pm", "5:30pm", "5:30pm", "6:20pm", "7:00pm", "7:40pm", "8:20pm",
             "9:00pm", "10:00pm", "10:30pm", "11:15pm", "11:40pm"],
    "Pickup": ["Campus", "Campus", "Transit hostel", "Transit hostel", "Campus", "Transit hostel", "Campus",
               "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel",
               "Campus", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel",
               "Campus", "Transit hostel", "Campus", "Transit hostel"],
    "Drop": ["Transit hostel", "Transit hostel", "Campus", "Campus", "Transit hostel", "Campus", "Transit hostel",
             "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus",
             "Transit hostel", "Transit hostel", "Campus", "Transit hostel", "Campus", "Transit hostel",
             "Campus", "Transit hostel", "Campus", "Transit hostel", "Campus"],
    "BusName": ["Institute Bus 1", "Institute Bus 2", "Institute Bus 1", "Institute Bus 2", "Institute Bus 1",
                "Institute Bus 1", "Institute Bus 2", "Institute Bus 2", "Institute Bus 2", "Institute Bus 2",
                "Institute Bus 2", "Institute Bus 2", "Institute Bus 2", "Institute Bus 2", "Institute Bus 2",
                "Institute Bus 1", "Institute Bus 1", "Institute Bus 1", "Institute Bus 1", "Institute Bus 1",
                "Institute Bus 1", "Institute Bus 1", "Institute Bus 1", "Institute Bus 1", "Institute Bus 1"]
}

df_bus = pd.DataFrame(bus_data)

# --- 4. EXPORT ---

df_menu.to_csv("menu_data.csv", index=False)
df_bus.to_csv("bus_data.csv", index=False)

print("✅ Files Created: 'menu_data.csv' and 'bus_data.csv'")