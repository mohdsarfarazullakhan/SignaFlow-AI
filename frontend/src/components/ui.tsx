import { AlertCircle, LoaderCircle, Sparkles } from "lucide-react";
import type { ReactNode } from "react";

export function PageHeader({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description?: string; action?: ReactNode }) {
  return <div className="page-header"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1>{description && <p>{description}</p>}</div>{action}</div>;
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "hot" | "warm" | "cold" | "success" | "accent" }) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

export function Loading({ label = "Working" }: { label?: string }) { return <div className="state-card"><LoaderCircle className="spin" size={22} /><span>{label}…</span></div>; }
export function ErrorState({ message }: { message: string }) { return <div className="state-card error"><AlertCircle size={22} /><span>{message}</span></div>; }
export function Empty({ title, text }: { title: string; text: string }) { return <div className="empty"><Sparkles size={26} /><h3>{title}</h3><p>{text}</p></div>; }

export function MetricCard({ label, value, detail, icon }: { label: string; value: string | number; detail?: string; icon?: ReactNode }) {
  return <div className="metric-card"><div className="metric-top"><span>{label}</span>{icon}</div><strong>{value}</strong>{detail && <small>{detail}</small>}</div>;
}

