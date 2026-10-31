
import { useState } from "react";
import "./App.css";

const initialAlerts = [
  { id: 1, title: "Subscription Expiring Soon", message: "Rahul's Premium plan expires in 3 days.", time: "5 minutes ago", type: "warning", read: false, icon: "⚠️" },
  { id: 2, title: "New Subscription", message: "Ananya joined the Premium plan.", time: "25 minutes ago", type: "success", read: false, icon: "👤" },
  { id: 3, title: "Subscription Expired", message: "Arjun's Basic plan has expired.", time: "1 hour ago", type: "danger", read: false, icon: "❌" },
  { id: 4, title: "Renewal Reminder", message: "Priya's subscription is due for renewal.", time: "Yesterday", type: "info", read: true, icon: "🔔" },
  { id: 5, title: "New Subscription", message: "A customer joined the Standard plan.", time: "Yesterday", type: "success", read: true, icon: "🎉" }
];

const customers = [
  { name: "Rahul Sharma", email: "rahul@gmail.com", plan: "Premium", price: "₹999", status: "Active" },
  { name: "Ananya Nair", email: "ananya@gmail.com", plan: "Standard", price: "₹499", status: "Active" },
  { name: "Arjun Kumar", email: "arjun@gmail.com", plan: "Basic", price: "₹199", status: "Expired" },
  { name: "Priya Menon", email: "priya@gmail.com", plan: "Premium", price: "₹999", status: "Expiring Soon" }
];

function App() {
  const [page, setPage] = useState("Dashboard");
  const [alerts, setAlerts] = useState(initialAlerts);
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");

  const unread = alerts.filter(a => !a.read).length;

  const visibleAlerts = alerts.filter(a =>
    filter === "All" || (filter === "Unread" && !a.read) || (filter === "Read" && a.read)
  );

  function markRead(id) {
    setAlerts(old => old.map(a => a.id === id ? { ...a, read: true } : a));
  }

  function markAllRead() {
    setAlerts(old => old.map(a => ({ ...a, read: true })));
  }

  const stats = [
    { title: "Total Subscribers", number: "250", icon: "👥", color: "blue", detail: "+12.5% this month" },
    { title: "Active Subscriptions", number: "180", icon: "✓", color: "green", detail: "Currently active" },
    { title: "Expiring Soon", number: "25", icon: "◷", color: "orange", detail: "Needs attention" },
    { title: "Expired Subscriptions", number: "45", icon: "✕", color: "red", detail: "Review required" }
  ];

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">S</div>
          <div>
            <h2>SubTrack</h2>
            <span>Smart Management</span>
          </div>
        </div>

        <p className="menu-heading">MAIN MENU</p>

        {[
          ["Dashboard", "▦"],
          ["Subscriptions", "▤"],
          ["Notifications", "♧"]
        ].map(([name, icon]) => (
          <button
            key={name}
            className={`nav-item ${page === name ? "selected" : ""}`}
            onClick={() => setPage(name)}
          >
            <span>{icon}</span>
            {name}
            {name === "Notifications" && unread > 0 && (
              <b className="nav-count">{unread}</b>
            )}
          </button>
        ))}

        <div className="sidebar-bottom">
          <div className="avatar">A</div>
          <div>
            <strong>Administrator</strong>
            <small>Project Admin</small>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h2>{page}</h2>
            <p>Welcome back! Here's your subscription overview.</p>
          </div>

          <div className="top-actions">
            <input
              className="search"
              placeholder="Search customers..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
            <button className="bell" onClick={() => setPage("Notifications")}>
              ♧
              {unread > 0 && <span className="bell-dot">{unread}</span>}
            </button>
            <div className="avatar top-avatar">A</div>
          </div>
        </header>

        <section className="content">

          {page === "Dashboard" && (
            <>
              <div className="page-heading">
                <div>
                  <h1>Dashboard Overview</h1>
                  <p>Monitor and manage your subscriptions in one place.</p>
                </div>
                <span className="date-label">📅 October 2026</span>
              </div>

              <div className="stats-grid">
                {stats.map(s => (
                  <div className="stat-card" key={s.title}>
                    <div className="stat-top">
                      <span>{s.title}</span>
                      <div className={`stat-icon ${s.color}`}>{s.icon}</div>
                    </div>
                    <h2>{s.number}</h2>
                    <small>{s.detail}</small>
                  </div>
                ))}
              </div>

              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h3>Revenue Analytics</h3>
                    <p>Monthly subscription revenue</p>
                  </div>
                  <span className="tag">Last 6 months</span>
                </div>

                <div className="chart">
                  <div className="chart-labels">
                    <span>₹30k</span><span>₹20k</span><span>₹10k</span><span>₹0</span>
                  </div>
                  <svg viewBox="0 0 650 210" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#3978ed" stopOpacity=".3"/>
                        <stop offset="100%" stopColor="#3978ed" stopOpacity="0"/>
                      </linearGradient>
                    </defs>
                    {[25,75,125,175].map(y => (
                      <line key={y} x1="0" y1={y} x2="650" y2={y} stroke="#e9edf5" strokeDasharray="4 5"/>
                    ))}
                    <path d="M0 145 L130 100 L260 120 L390 65 L520 80 L650 20 L650 190 L0 190 Z" fill="url(#area)"/>
                    <path d="M0 145 L130 100 L260 120 L390 65 L520 80 L650 20" fill="none" stroke="#3978ed" strokeWidth="3" strokeLinecap="round"/>
                    {[0,130,260,390,520,650].map((x,i) => (
                      <circle key={x} cx={x} cy={[145,100,120,65,80,20][i]} r="4" fill="#3978ed"/>
                    ))}
                  </svg>
                </div>
                <div className="chart-months">
                  {["May", "Jun", "Jul", "Aug", "Sep", "Oct"].map(m => <span key={m}>{m}</span>)}
                </div>
              </div>

              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h3>Recent Subscriptions</h3>
                    <p>Latest customer activity</p>
                  </div>
                  <button className="text-button" onClick={() => setPage("Subscriptions")}>View all →</button>
                </div>
                <CustomerTable search={search} />
              </div>

              <button className="attention" onClick={() => setPage("Notifications")}>
                ⚠️ &nbsp; <span><strong>Attention Required</strong><small>25 subscriptions need attention.</small></span>
                <span>→</span>
              </button>
            </>
          )}

          {page === "Notifications" && (
            <>
              <div className="page-heading">
                <div>
                  <h1>Notification Centre 🔔</h1>
                  <p>Stay updated with your subscription activities.</p>
                </div>
                <button className="primary-button" onClick={markAllRead}>✓ Mark all as read</button>
              </div>

              <div className="notification-stats">
                <div className="mini-card">
                  <span>Total Notifications</span>
                  <h2>{alerts.length}</h2>
                </div>
                <div className="mini-card unread-card">
                  <span>Unread Notifications</span>
                  <h2>{unread}</h2>
                </div>
                <div className="mini-card read-card">
                  <span>Read Notifications</span>
                  <h2>{alerts.length - unread}</h2>
                </div>
              </div>

              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h3>All Notifications</h3>
                    <p>Manage your latest alerts and updates.</p>
                  </div>
                  <span className="tag">{unread} new</span>
                </div>

                <div className="filters">
                  {["All", "Unread", "Read"].map(f => (
                    <button
                      key={f}
                      onClick={() => setFilter(f)}
                      className={filter === f ? "filter-active" : ""}
                    >
                      {f} {f === "Unread" ? `(${unread})` : ""}
                    </button>
                  ))}
                </div>

                <div className="alert-list">
                  {visibleAlerts.map(a => (
                    <div className={`alert-item ${!a.read ? "unread-alert" : ""}`} key={a.id}>
                      <div className={`alert-icon ${a.type}`}>{a.icon}</div>
                      <div className="alert-body">
                        <div className="alert-title">
                          <strong>{a.title}</strong>
                          {!a.read && <span className="new-tag">NEW</span>}
                        </div>
                        <p>{a.message}</p>
                        <small>{a.time}</small>
                      </div>
                      {!a.read && (
                        <button className="read-button" onClick={() => markRead(a.id)}>
                          ✓ Mark read
                        </button>
                      )}
                    </div>
                  ))}
                  {visibleAlerts.length === 0 && (
                    <div className="empty-state">
                      <div>🔔</div>
                      <strong>No notifications found</strong>
                      <p>You're all caught up!</p>
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

          {page === "Subscriptions" && (
            <>
              <div className="page-heading">
                <div>
                  <h1>Subscription Management</h1>
                  <p>View customer subscription records.</p>
                </div>
              </div>
              <div className="panel">
                <div className="panel-heading"><h3>Customer Records</h3></div>
                <CustomerTable search={search} />
              </div>
            </>
          )}

          <footer>© 2026 SubTrack · Smart Subscription Management System</footer>
        </section>
      </main>
    </div>
  );
}

function CustomerTable({ search }) {
  const filtered = customers.filter(c =>
    (c.name + c.email + c.plan).toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr><th>Customer</th><th>Plan</th><th>Price</th><th>Status</th></tr>
        </thead>
        <tbody>
          {filtered.map(c => (
            <tr key={c.email}>
              <td><strong>{c.name}</strong><small>{c.email}</small></td>
              <td>{c.plan}</td>
              <td>{c.price}</td>
              <td><span className={`status ${c.status === "Active" ? "active" : c.status === "Expired" ? "expired" : "expiring"}`}>{c.status}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
      {filtered.length === 0 && <p className="no-results">No matching customers.</p>}
    </div>
  );
}

export default App;
