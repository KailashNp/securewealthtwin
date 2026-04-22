import React from "react";
import "./Navbar.css";
import {
  LayoutDashboard,
  Target,
  Landmark,
  PieChart as PieIcon,
  AlertTriangle
} from "lucide-react";

export default function Navbar({ page, setPage }) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: <LayoutDashboard size={20} /> },
    { id: "goals", label: "Goals", icon: <Target size={20} /> },
    { id: "networth", label: "Net Worth", icon: <Landmark size={20} /> },
    { id: "portfolio", label: "Portfolio", icon: <PieIcon size={20} /> },
    { id: "alerts", label: "Alerts & Risk", icon: <AlertTriangle size={20} /> }
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h2>SecureWealth Twin</h2>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-group">
          {navItems.map((item) => (
            <div
              key={item.id}
              className={`nav-item ${page === item.id ? "active" : ""}`}
              onClick={() => setPage(item.id)}
            >
              {item.icon}
              {item.label}
            </div>
          ))}
        </div>
      </nav>
    </aside>
  );
}