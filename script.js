let allMenus = [];
let busSchedule = [];
let mealTimes = [];

const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

/* ================= INIT ================= */

function init() {
    updateDate();
    loadData();
    loadCalendarData();

    setInterval(() => {
        updateDate();
        updateHome();
    }, 60000);
}

/* ================= LOAD CSVs ================= */

async function loadData() {
    try {
        const [menuRes, busRes, timeRes] = await Promise.all([
            fetch("./menu_data.csv"),
            fetch("./bus_data.csv"),
            fetch("./meal_times.csv")
        ]);

        allMenus = parseCSV(await menuRes.text());
        busSchedule = parseCSV(await busRes.text());
        mealTimes = parseCSV(await timeRes.text());

        renderAllMenus();
        renderBusLists();
        updateHome();

    } catch (e) {
        console.error(e);
        document.getElementById("home-next-bus").innerHTML =
            "<span style='color:red'>CSV load error</span>";
    }
}

/* ================= CSV PARSER ================= */

function parseCSV(text) {
    const lines = text.trim().split("\n");
    const headers = lines[0].split(",");

    return lines.slice(1).map(line => {
        const values = line.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/);
        const obj = {};
        headers.forEach((h,i) => {
            obj[h.trim()] = (values[i] || "").replace(/"/g,"").trim();
        });
        return obj;
    });
}

/* ================= DATE ================= */

function updateDate() {
    const now = new Date();
    document.getElementById("current-day").innerText = days[now.getDay()];
    document.getElementById("current-date").innerText =
        `${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
}

/* ================= HOME LOGIC (CRITICAL) ================= */

function updateHome() {
    const now = new Date();
    const today = days[now.getDay()];
    const currentMins = now.getHours() * 60 + now.getMinutes();

    const todayMenus = allMenus.filter(m => m.Day === today);

    function setMenu(type, id) {
        const card = document.getElementById(id)?.parentElement;
        if (!card) return;

        const meal = todayMenus.find(m => m.Type === type);

        let timeInfo =
            mealTimes.find(t => t.Day === today && t.Type === type) ||
            mealTimes.find(t => t.Day === "Default" && t.Type === type);

        // Hide if no meal or timing
        if (!meal || !timeInfo || !timeInfo.EndTime) {
            card.style.display = "none";
            return;
        }

        const endTime = parse24HTime(timeInfo.EndTime);

        // Hide if meal time is over
        if (currentMins > endTime) {
            card.style.display = "none";
            return;
        }

        // Otherwise show
        card.style.display = "block";
        document.getElementById(id).innerText =
            meal.Main + (meal.Sides ? " - " + meal.Sides : "");
    }

    setMenu("Breakfast","home-breakfast");
    setMenu("Lunch","home-lunch");
    setMenu("Snacks","home-snacks");
    setMenu("Dinner","home-dinner");

    const nextToHostel = getNextBus(currentMins,"Campus","Transit hostel");
    const nextToCampus = getNextBus(currentMins,"Transit hostel","Campus");

    document.getElementById("home-next-bus").innerHTML = `
        <strong>To Hostel:</strong> ${nextToHostel}<br>
        <strong>To Campus:</strong> ${nextToCampus}
    `;
}

/* ================= BUS ================= */

function getNextBus(currentMins, from, to) {
    for (const bus of busSchedule) {
        if (
            bus.Pickup.toLowerCase().includes(from.toLowerCase()) &&
            bus.Drop.toLowerCase().includes(to.toLowerCase())
        ) {
            const mins = parseTimeStr(bus.Time);
            if (mins > currentMins) {
                return `${bus.Time} (${bus.BusName})`;
            }
        }
    }
    return "No more buses today";
}

function parseTimeStr(t) {
    const m = t.match(/(\d+):(\d+)(am|pm)/i);
    if (!m) return -1;
    let h = +m[1], min = +m[2];
    if (m[3].toLowerCase()==="pm" && h!==12) h+=12;
    if (m[3].toLowerCase()==="am" && h===12) h=0;
    return h*60+min;
}

function parse24HTime(t) {
    const [h,m] = t.split(":").map(Number);
    return h*60+m;
}

/* ================= LIST RENDER ================= */

function renderAllMenus() {
    ["Breakfast","Lunch","Snacks","Dinner"].forEach(type => {
        const container = document.getElementById(`list-${type}`);
        container.innerHTML = "";

        allMenus.filter(m => m.Type === type).forEach(meal => {
            const div = document.createElement("div");
            div.className = "menu-item";
            div.innerHTML = `
                <span class="day-label">${meal.Day}</span>
                <strong>${meal.Main}</strong><br>
                <small>${meal.Sides}</small>
            `;
            container.appendChild(div);
        });
    });
}

function renderBusLists() {
    const ch = document.getElementById("bus-campus-hostel");
    const hc = document.getElementById("bus-hostel-campus");
    ch.innerHTML = ""; hc.innerHTML = "";

    busSchedule.forEach(bus => {
        const li = document.createElement("li");
        li.innerText = `${bus.Time} - ${bus.BusName}`;
        if (bus.Pickup.toLowerCase().includes("campus")) ch.appendChild(li);
        else hc.appendChild(li);
    });
}

/* ================= NAV ================= */

function showSection(id) {
    document.querySelectorAll(".section").forEach(s => s.classList.remove("active-section"));
    document.getElementById(id).classList.add("active-section");

    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    [...document.querySelectorAll(".nav-btn")]
        .find(b => b.innerText.toLowerCase() === id.toLowerCase())
        ?.classList.add("active");
}

/* ================= CALENDAR ================= */

async function loadCalendarData() {
    const box = document.getElementById("calendar-events");
    box.innerHTML = "<em>Syncing...</em>";

    try {
        const res = await fetch(`./events_data.csv?t=${Date.now()}`);
        const events = parseCSV(await res.text());
        const today = new Date().toISOString().split("T")[0];

        const todayEvents = events.filter(e => e.Date === today);

        box.innerHTML = todayEvents.length
            ? todayEvents.map(e => `
                <div class="calendar-event">
                    <strong>${e.Event}</strong><br>
                    <small>${e.Time}</small>
                </div>`).join("")
            : "<em>No events for today.</em>";

    } catch {
        box.innerHTML = "<small>Schedule unavailable</small>";
    }
}

init();
