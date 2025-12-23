let allMenus = [];
let busSchedule = [];
const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function init() {
    updateDate();
    loadData();
    loadCalendarData();
    setInterval(updateHome, 60000);
}

async function loadData() {
    try {
        const [menuRes, busRes] = await Promise.all([
            fetch("./menu_data.csv"),
            fetch("./bus_data.csv")
        ]);

        allMenus = parseCSV(await menuRes.text());
        busSchedule = parseCSV(await busRes.text());

        updateHome();
    } catch {
        document.getElementById("calendar-events").innerText = "Data unavailable";
    }
}

function parseCSV(text) {
    const [header, ...rows] = text.trim().split("\n");
    const keys = header.split(",");

    return rows.map(row => {
        const vals = row.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/);
        let obj = {};
        keys.forEach((k,i) => obj[k.trim()] = (vals[i] || "").replace(/"/g,"").trim());
        return obj;
    });
}

function updateDate() {
    const now = new Date();
    document.getElementById("current-day").innerText = days[now.getDay()];
    document.getElementById("current-date").innerText =
        `${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
}

function updateHome() {
    const now = new Date();
    const today = days[now.getDay()];
    const mins = now.getHours()*60 + now.getMinutes();

    ["Breakfast","Lunch","Snacks","Dinner"].forEach(type => {
        const card = document.getElementById(`home-${type.toLowerCase()}`);
        const parent = card?.parentElement;
        const meal = allMenus.find(m => m.Day===today && m.Type===type);

        if (!meal) {
            parent.style.display="none";
            return;
        }

        parent.style.display="block";
        card.innerText = meal.Main + (meal.Sides ? " - "+meal.Sides : "");
    });

    const nextBus = busSchedule.find(b => parseTime(b.Time) > mins);
    document.getElementById("home-next-bus").innerText =
        nextBus ? `${nextBus.Time} (${nextBus.BusName})` : "No more buses today";
}

function parseTime(t) {
    const m = t.match(/(\d+):(\d+)(am|pm)/);
    let h = +m[1], min = +m[2];
    if (m[3]==="pm" && h!==12) h+=12;
    if (m[3]==="am" && h===12) h=0;
    return h*60+min;
}

async function loadCalendarData() {
    const el = document.getElementById("calendar-events");
    try {
        const res = await fetch(`./events_data.csv?t=${Date.now()}`);
        const events = parseCSV(await res.text());
        const today = new Date().toISOString().split("T")[0];
        const todayEvents = events.filter(e=>e.Date===today);

        el.innerHTML = todayEvents.length
            ? todayEvents.map(e=>`<div><strong>${e.Event}</strong><br><small>${e.Time}</small></div>`).join("")
            : "<em>No events today</em>";
    } catch {
        el.innerHTML="<small>Schedule unavailable</small>";
    }
}

init();
