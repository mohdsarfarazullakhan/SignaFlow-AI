import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { BarChart3, Bot, Boxes, BriefcaseBusiness, Building2, ChevronLeft, CircleGauge, FileText, Globe2, Home, Image, LogOut, Megaphone, Menu, Settings, Sparkles, Target, UserCog, Users, Video } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const nav = [
  { to: "/", label: "Overview", icon: Home, roles: ["CUSTOMER", "SALES", "ADMIN"] },
  { to: "/advisor", label: "AI Product Advisor", icon: Sparkles, roles: ["CUSTOMER", "SALES", "ADMIN"] },
  { to: "/products", label: "Products", icon: Boxes, roles: ["CUSTOMER", "SALES", "ADMIN"] },
  { to: "/dashboard", label: "CRM Dashboard", icon: CircleGauge, roles: ["SALES", "ADMIN"] },
  { to: "/leads", label: "Leads", icon: Users, roles: ["SALES", "ADMIN"] },
  { to: "/sales-copilot", label: "Sales Copilot", icon: Bot, roles: ["SALES", "ADMIN"] },
  { to: "/quotations", label: "Quotations", icon: FileText, roles: ["SALES", "ADMIN"] },
  { to: "/campaign-studio", label: "Campaign Studio", icon: Megaphone, roles: ["CUSTOMER", "SALES", "ADMIN"] },
  { to: "/analytics", label: "Analytics", icon: BarChart3, roles: ["SALES", "ADMIN"] },
  { to: "/smart-signage", label: "Smart Signage", icon: Video, roles: ["SALES", "ADMIN"] },
  { to: "/visual-advisor", label: "Visual Advisor", icon: Image, roles: ["CUSTOMER", "SALES", "ADMIN"] },
  { to: "/website-opportunities", label: "Website Opportunities", icon: Globe2, roles: ["ADMIN"] },
  { to: "/business-impact", label: "Business Impact", icon: Target, roles: ["ADMIN", "SALES"] },
  { to: "/admin", label: "Admin Console", icon: UserCog, roles: ["ADMIN"] },
  { to: "/settings", label: "Settings", icon: Settings, roles: ["ADMIN"] },
];

export function Layout() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  return <div className="app-shell">
    <aside className={open ? "sidebar open" : "sidebar"}>
      <div className="brand"><div className="brand-mark"><Building2 size={19} /></div><div><b>SignaFlow</b><span>AI</span></div><button className="mobile-close" onClick={() => setOpen(false)} aria-label="Close navigation"><ChevronLeft /></button></div>
      <div className="workspace-label">INTELLIGENT SALES OS</div>
      <nav>{nav.filter(item => item.roles.includes(user?.role || "CUSTOMER")).map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} end={to === "/"} onClick={() => setOpen(false)}><Icon size={18} /><span>{label}</span></NavLink>)}</nav>
      <div className="sidebar-footer"><div className="avatar">{user?.name?.slice(0, 2).toUpperCase()}</div><div><b>{user?.name}</b><span>{user?.role.toLowerCase()} workspace</span></div><button onClick={logout} aria-label="Log out"><LogOut size={17} /></button></div>
    </aside>
    <main><header className="topbar"><button className="menu-button" aria-label="Open navigation" onClick={() => setOpen(true)}><Menu /></button><div className="topbar-title"><BriefcaseBusiness size={18} /> Signage intelligence workspace</div><div className="demo-status"><i /> Demo mode active</div></header><div className="page"><Outlet /></div></main>
    {open && <button className="scrim" onClick={() => setOpen(false)} aria-label="Close navigation" />}
  </div>;
}
