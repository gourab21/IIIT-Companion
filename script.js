// --- STATE ---
let allMenus = []; // Will store parsed CSV data
let busSchedule = []; 
let mealTimes = [];
const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// --- INIT ---
function init() {
    updateDate();
    loadData();
    loadCalendarData();
    
    setInterval(() => {
        updateDate();
        updateHome();
    }, 60000); // Update every minute
}

async function loadData() {
    try {
        // Load all CSVs in parallel
        const [menuRes, busRes, timesRes] = await Promise.all([
            fetch('./menu_data.csv'),
            fetch('./bus_data.csv'),
            fetch('./meal_times.csv')
        ]);

        if (!menuRes.ok || !busRes.ok || !timesRes.ok) throw new Error("CSV files not found");

        const menuText = await menuRes.text();
        const busText = await busRes.text();
        const timesText = await timesRes.text();

        allMenus = parseCSV(menuText);
        busSchedule = parseCSV(busText);
        mealTimes = parseCSV(timesText);

        renderAllMenus();
        renderBusLists();
        updateHome();

    } catch (err) {
        console.error(err);
        document.getElementById("home-next-bus").innerHTML = "<span style='color:red'>Error loading CSVs. Run server?</span>";
    }
}

// --- CSV PARSER ---
function parseCSV(text) {
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    
    return lines.slice(1).map(line => {
        const obj = {};
        // Complex split to handle commas inside quotes "Item 1, Item 2"
        const values = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || [];
        
        // Fallback for simple split if regex fails or no quotes used
        const simpleValues = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);

        headers.forEach((header, i) => {
            let val = simpleValues[i] || "";
            // Remove quotes if present
            val = val.replace(/^"|"$/g, '').trim(); 
            obj[header] = val;
        });
        return obj;
    });
}

// --- UI UPDATES ---

function updateDate() {
    const now = new Date();
    document.getElementById("current-day").innerText = days[now.getDay()];
    document.getElementById("current-date").innerText = `${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
}

function updateHome() {
    const now = new Date();
    const currentDay = days[now.getDay()];
    const currentMins = now.getHours() * 60 + now.getMinutes();

    // 1. UPDATE MENUS
    const todayData = allMenus.filter(item => item.Day === currentDay);

    const setMenu = (type, id) => {
        const card = document.getElementById(id).parentElement;

        // Find meal time for today, fallback to default
        let timeInfo = mealTimes.find(t => t.Day === currentDay && t.Type === type);
        if (!timeInfo) {
            timeInfo = mealTimes.find(t => t.Day === "Default" && t.Type === type);
        }

        const meal = todayData.find(m => m.Type === type);

        if (!timeInfo || !meal) {
            card.style.display = 'none'; // Hide if no time or meal info
            return;
        }

        const endTime = parse24HTime(timeInfo.EndTime);

        if (currentMins > endTime) {
            card.style.display = 'none';
        } else {
            card.style.display = 'block';
            card.style.opacity = 1;
            let menuText = meal.Main;
            if (meal.Sides) {
                menuText += ` - ${meal.Sides}`;
            }
            document.getElementById(id).innerText = menuText;
        }
    };

    setMenu("Breakfast", "home-breakfast");
    setMenu("Lunch", "home-lunch");
    setMenu("Snacks", "home-snacks");
    setMenu("Dinner", "home-dinner");

    // 2. UPDATE NEXT BUS
    const nextToHostel = getNextBus(currentMins, "Campus", "Transit hostel");
    const nextToCampus = getNextBus(currentMins, "Transit hostel", "Campus");

    document.getElementById("home-next-bus").innerHTML = `
        <strong>To Hostel:</strong> ${nextToHostel}<br>
        <strong>To Campus:</strong> ${nextToCampus}
    `;
}

function getNextBus(currentMins, fromLoc, toLoc) {
    // Filter buses matching route
    const relevantBuses = busSchedule.filter(b => 
        b.Pickup.toLowerCase().includes(fromLoc.toLowerCase()) && 
        b.Drop.toLowerCase().includes(toLoc.toLowerCase())
    );

    // Find first one after current time
    for (let bus of relevantBuses) {
        const busMins = parseTimeStr(bus.Time);
        if (busMins > currentMins) {
            return `${bus.Time} (${bus.BusName})`;
        }
    }
    return "No more buses today";
}

function parse24HTime(timeStr) {
    if (!timeStr) return -1;
    const [h, m] = timeStr.split(':').map(Number);
    return h * 60 + m;
}

function parseTimeStr(timeStr) {
    // Formats: "7:30am", "12:00pm", "2:00pm"
    if(!timeStr) return -1;
    const match = timeStr.match(/(\d+):(\d+)([ap]m)/i);
    if (!match) return -1;

    let [_, h, m, period] = match;
    h = parseInt(h);
    m = parseInt(m);
    period = period.toLowerCase();

    if (period === 'pm' && h !== 12) h += 12;
    if (period === 'am' && h === 12) h = 0;

    return h * 60 + m;
}

function renderAllMenus() {
    const types = ["Breakfast", "Lunch", "Snacks", "Dinner"];
    
    types.forEach(type => {
        const container = document.getElementById(`list-${type}`);
        container.innerHTML = "";
        
        // Sort by day index to keep order Mon-Sun
        // Helper map
        const dayMap = {"Monday":1, "Tuesday":2, "Wednesday":3, "Thursday":4, "Friday":5, "Saturday":6, "Sunday":7};
        
        const meals = allMenus.filter(m => m.Type === type);
        meals.sort((a,b) => dayMap[a.Day] - dayMap[b.Day]);

        meals.forEach(meal => {
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
    const listCH = document.getElementById("bus-campus-hostel");
    const listHC = document.getElementById("bus-hostel-campus");

    listCH.innerHTML = "";
    listHC.innerHTML = "";

    busSchedule.forEach(bus => {
        const li = document.createElement("li");
        li.innerText = `${bus.Time} - ${bus.BusName}`;
        
        if (bus.Pickup.toLowerCase().includes("campus")) {
            listCH.appendChild(li);
        } else {
            listHC.appendChild(li);
        }
    });
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active-section'));
    document.getElementById(sectionId).classList.add('active-section');
    
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    // Find button with matching text
    const buttons = Array.from(document.querySelectorAll('.nav-btn'));
    const activeBtn = buttons.find(b => b.innerText.toLowerCase() === sectionId.toLowerCase());
    if(activeBtn) activeBtn.classList.add('active');
}

// --- CALENDAR (CSV VERSION) ---
async function loadCalendarData() {
    const calendarContainer = document.getElementById("calendar-events");
    calendarContainer.innerHTML = "<em>Syncing...</em>";

    try {
        // Fetch the generated CSV. 
        // We add '?t=' + timestamp to force the browser to ignore old cache
        const response = await fetch(`./events_data.csv?t=${new Date().getTime()}`);
        
        if (!response.ok) throw new Error("Events file not found");

        const csvText = await response.text();
        const events = parseCSV(csvText); // Uses your existing CSV parser

        // Filter for TODAY only
        const now = new Date();
        const todayStr = now.toISOString().split('T')[0]; // Format: YYYY-MM-DD

        const todayEvents = events.filter(e => e.Date === todayStr);

        if (todayEvents.length === 0) {
            calendarContainer.innerHTML = "<em>No events for today.</em>";
            return;
        }

        calendarContainer.innerHTML = todayEvents.map(evt => `
            <div class="calendar-event">
                <strong>${evt.Event}</strong><br>
                <small>${evt.Time}</small>
            </div>
        `).join('');

    } catch (err) {
        console.error("Calendar Error:", err);
        calendarContainer.innerHTML = "<small>Schedule unavailable</small>";
    }
}


function formatTime(date) {
    let hours = date.getHours();
    let minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    return `${hours}:${minutes}${ampm}`;
}


init();