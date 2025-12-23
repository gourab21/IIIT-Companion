// --- STATE ---
let allMenus = []; 
let busSchedule = []; 
let allEvents = [];
const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// --- INIT ---
function init() {
    updateDate();
    loadData(); // Loads Menu, Bus, and Calendar CSVs
    
    // Auto-refresh clock and home UI every minute
    setInterval(() => {
        updateDate();
        updateHome();
    }, 60000); 
}

async function loadData() {
    try {
        // Fetch all 3 CSVs. Add cache busting (?t=...) to get fresh data.
        const bust = new Date().getTime();
        const [menuRes, busRes, eventRes] = await Promise.all([
            fetch('./menu_data.csv'),
            fetch('./bus_data.csv'),
            fetch(`./events_data.csv?t=${bust}`)
        ]);

        if (!menuRes.ok || !busRes.ok || !eventRes.ok) throw new Error("CSV files not found");

        const menuText = await menuRes.text();
        const busText = await busRes.text();
        const eventText = await eventRes.text();

        allMenus = parseCSV(menuText);
        busSchedule = parseCSV(busText);
        allEvents = parseCSV(eventText);

        renderAllMenus();
        renderBusLists();
        updateHome();

    } catch (err) {
        console.error(err);
        document.getElementById("home-next-bus").innerHTML = "<small style='color:red'>Data sync error</small>";
    }
}

// --- CSV PARSER (Simple & Robust) ---
function parseCSV(text) {
    const lines = text.trim().split('\n');
    if (lines.length < 2) return []; // Empty file
    
    const headers = lines[0].split(',').map(h => h.trim());
    
    return lines.slice(1).map(line => {
        const obj = {};
        // Regex to handle commas inside quotes
        const values = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || [];
        // Fallback split if regex fails
        const simpleValues = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);
        
        headers.forEach((header, i) => {
            let val = simpleValues[i] || "";
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

    // 1. UPDATE MENUS
    const todayData = allMenus.filter(item => item.Day === currentDay);
    
    const setMenu = (type, id) => {
        const meal = todayData.find(m => m.Type === type);
        document.getElementById(id).innerText = meal ? meal.Main : "Closed";
    };

    setMenu("Breakfast", "home-breakfast");
    setMenu("Lunch", "home-lunch");
    setMenu("Snacks", "home-snacks");
    setMenu("Dinner", "home-dinner");

    // 2. UPDATE EVENTS (Calendar)
    const todayStr = now.toISOString().split('T')[0]; // YYYY-MM-DD
    const todayEvents = allEvents.filter(e => e.Date === todayStr);
    
    const calContainer = document.getElementById("calendar-events");
    if (todayEvents.length === 0) {
        calContainer.innerHTML = "<em>No events for today.</em>";
    } else {
        calContainer.innerHTML = todayEvents.map(evt => `
            <div style="margin-bottom:8px; border-bottom:1px solid #eee; padding-bottom:4px;">
                <strong>${evt.Event}</strong><br>
                <small style="color:#007bff">${evt.Time}</small>
            </div>
        `).join('');
    }

    // 3. UPDATE NEXT BUS
    const currentMins = now.getHours() * 60 + now.getMinutes();
    const nextToHostel = getNextBus(currentMins, "Campus", "Transit hostel");
    const nextToCampus = getNextBus(currentMins, "Transit hostel", "Campus");

    document.getElementById("home-next-bus").innerHTML = `
        <strong>To Hostel:</strong> ${nextToHostel}<br>
        <strong>To Campus:</strong> ${nextToCampus}
    `;
}

function getNextBus(currentMins, fromLoc, toLoc) {
    const relevantBuses = busSchedule.filter(b => 
        b.Pickup.toLowerCase().includes(fromLoc.toLowerCase()) && 
        b.Drop.toLowerCase().includes(toLoc.toLowerCase())
    );

    for (let bus of relevantBuses) {
        const busMins = parseTimeStr(bus.Time);
        if (busMins > currentMins) {
            return `${bus.Time} (${bus.BusName})`;
        }
    }
    return "No more buses today";
}

function parseTimeStr(timeStr) {
    if(!timeStr) return -1;
    const match = timeStr.match(/(\d+):(\d+)([ap]m)/i);
    if (!match) return -1;

    let [_, h, m, period] = match;
    h = parseInt(h); m = parseInt(m); period = period.toLowerCase();
    if (period === 'pm' && h !== 12) h += 12;
    if (period === 'am' && h === 12) h = 0;
    return h * 60 + m;
}

function renderAllMenus() {
    const types = ["Breakfast", "Lunch", "Snacks", "Dinner"];
    const dayMap = {"Monday":1, "Tuesday":2, "Wednesday":3, "Thursday":4, "Friday":5, "Saturday":6, "Sunday":7};

    types.forEach(type => {
        const container = document.getElementById(`list-${type}`);
        container.innerHTML = "";
        
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
    listCH.innerHTML = ""; listHC.innerHTML = "";

    busSchedule.forEach(bus => {
        const li = document.createElement("li");
        li.innerText = `${bus.Time} - ${bus.BusName}`;
        if (bus.Pickup.toLowerCase().includes("campus")) listCH.appendChild(li);
        else listHC.appendChild(li);
    });
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active-section'));
    document.getElementById(sectionId).classList.add('active-section');
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    
    // Highlight button
    const buttons = Array.from(document.querySelectorAll('.nav-btn'));
    const activeBtn = buttons.find(b => b.innerText.toLowerCase() === sectionId.toLowerCase());
    if(activeBtn) activeBtn.classList.add('active');
}

// Start
init();