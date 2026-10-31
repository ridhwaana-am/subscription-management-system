from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
from datetime import datetime, timedelta

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db_connection():
    conn = sqlite3.connect("subscriptions.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            plan TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    # Insert initial mock data if empty
    cursor.execute("SELECT COUNT(*) FROM subscriptions")
    if cursor.fetchone()[0] == 0:
        today = datetime.now().date()
        mock_data = [
            ("Alice Smith", "Premium", str(today - timedelta(days=30)), str(today + timedelta(days=30)), 1500.0),
            ("Bob Jones", "Basic", str(today - timedelta(days=20)), str(today + timedelta(days=10)), 500.0),
            ("Charlie Brown", "Standard", str(today - timedelta(days=60)), str(today - timedelta(days=5)), 999.0),
            ("Diana Prince", "Premium", str(today - timedelta(days=15)), str(today + timedelta(days=3)), 1500.0),
            ("Evan Wright", "Standard", str(today - timedelta(days=40)), str(today + timedelta(days=20)), 999.0)
        ]
        cursor.executemany('''
            INSERT INTO subscriptions (customer_name, plan, start_date, end_date, price)
            VALUES (?, ?, ?, ?, ?)
        ''', mock_data)
        conn.commit()
    conn.close()

init_db()

def calculate_status(end_date_str):
    today = datetime.now().date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    days_left = (end_date - today).days
    
    if days_left < 0:
        return "Expired"
    elif 0 <= days_left <= 7:
        return "Expiring Soon"
    else:
        return "Active"

# --- LEADER: MAIN DASHBOARD ROUTE ---
@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    conn = get_db_connection()
    subscriptions = conn.fetchall("SELECT * FROM subscriptions") if hasattr(conn, 'fetchall') else conn.execute("SELECT * FROM subscriptions").fetchall()
    conn.close()

    total_subscribers = len(subscriptions)
    active_count = 0
    expired_count = 0
    expiring_soon_count = 0
    monthly_revenue = 0.0

    for sub in subscriptions:
        status = calculate_status(sub["end_date"])
        if status == "Active" or status == "Expiring Soon":
            active_count += 1
            monthly_revenue += sub["price"]
        if status == "Expired":
            expired_count += 1
        if status == "Expiring Soon":
            expiring_soon_count += 1

    return templates.TemplateResponse("index.html", {
        "request": request,
        "total_subscribers": total_subscribers,
        "active_count": active_count,
        "expired_count": expired_count,
        "expiring_soon_count": expiring_soon_count,
        "monthly_revenue": monthly_revenue
    })

# --- MEMBER 2: SUBSCRIPTION CRUD API / ROUTES ---
@app.get("/subscriptions", response_class=HTMLResponse)
async def list_subscriptions(request: Request):
    conn = get_db_connection()
    subs = conn.execute("SELECT * FROM subscriptions").fetchall()
    conn.close()
    
    sub_list = []
    for s in subs:
        sub_dict = dict(s)
        sub_dict["status"] = calculate_status(s["end_date"])
        sub_list.append(sub_dict)
        
    return templates.TemplateResponse("subscriptions.html", {"request": request, "subscriptions": sub_list})

@app.post("/subscriptions/add")
async def add_subscription(customer_name: str = Form(...), plan: str = Form(...), start_date: str = Form(...), end_date: str = Form(...), price: float = Form(...)):
    conn = get_db_connection()
    conn.execute("INSERT INTO subscriptions (customer_name, plan, start_date, end_date, price) VALUES (?, ?, ?, ?, ?)",
                 (customer_name, plan, start_date, end_date, price))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/subscriptions", status_code=303)

# --- MEMBER 3: INSIGHTS & ANALYTICS API ---
@app.get("/api/analytics")
async def get_analytics():
    conn = get_db_connection()
    subs = conn.execute("SELECT * FROM subscriptions").fetchall()
    conn.close()
    
    plan_counts = {}
    for s in subs:
        plan_counts[s["plan"]] = plan_counts.get(s["plan"], 0) + 1
        
    return {
        "plans": list(plan_counts.keys()),
        "counts": list(plan_counts.values())
    }