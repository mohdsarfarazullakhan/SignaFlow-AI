import { ArrowRight, BarChart3, Bot, ChevronRight, Megaphone, MonitorUp, Sparkles, Target } from "lucide-react";
import { Link } from "react-router-dom";
import hero from "../assets/signaflow-ai-hero.png";
import { useAuth } from "../context/AuthContext";

const capabilities = [
  { icon: Sparkles, title: "AI Product Advisor", text: "Find the right solution", to: "/advisor", accent: "coral" },
  { icon: Bot, title: "AI Sales Copilot", text: "Convert leads faster", to: "/sales-copilot", accent: "cyan" },
  { icon: Megaphone, title: "Campaign Studio", text: "Create digital campaigns", to: "/campaign-studio", accent: "sand" },
  { icon: BarChart3, title: "Smart Signage", text: "Measure engagement", to: "/smart-signage", accent: "blue" },
];

export function HomePage() {
  const { user } = useAuth();
  return <>
    <section className="hero" style={{ backgroundImage: `linear-gradient(90deg, rgba(11,19,31,.98) 0%, rgba(11,19,31,.88) 43%, rgba(11,19,31,.2) 100%), url(${hero})` }}>
      <div className="hero-content"><div className="eyebrow light"><Sparkles size={14} /> SIGNAGE INTELLIGENCE LAYER</div><h1>From Requirement to Revenue — <em>Powered by AI</em></h1><p>An independent AI portfolio project for product discovery, sales automation, smart signage, and campaign analytics.</p><div className="hero-actions"><Link to="/advisor" className="button primary">Try AI Product Advisor <ArrowRight size={18} /></Link><Link to={user?.role === "CUSTOMER" ? "/campaign-studio" : "/dashboard"} className="button ghost-light">Explore the platform</Link></div></div>
      <div className="hero-kicker"><MonitorUp /><span><b>One connected journey</b>Requirement → product → revenue</span></div>
    </section>
    <section className="capability-grid">{capabilities.filter(item => user?.role !== "CUSTOMER" || !["/sales-copilot", "/smart-signage"].includes(item.to)).map(({ icon: Icon, ...item }) => <Link to={item.to} key={item.title} className={`capability-card ${item.accent}`}><div className="capability-icon"><Icon /></div><div><h3>{item.title}</h3><p>{item.text}</p></div><ChevronRight /></Link>)}</section>
    <section className="journey-section"><div><div className="eyebrow">THE CONNECTED SALES JOURNEY</div><h2>Every insight moves the opportunity forward.</h2></div><div className="journey-track">{["Understand", "Recommend", "Configure", "Qualify", "Quote", "Engage", "Measure"].map((label, index) => <div className="journey-step" key={label}><span>{String(index + 1).padStart(2, "0")}</span><b>{label}</b></div>)}</div></section>
    <section className="home-callout"><div><Target /><div><span>Management-ready prototype</span><h2>Built to demonstrate measurable operating value.</h2><p>Authoritative calculations stay in application code. AI focuses on understanding, explanation, creative support, and next-best actions.</p></div></div><Link to="/business-impact" className="button secondary">View potential KPIs <ArrowRight size={17} /></Link></section>
  </>;
}

