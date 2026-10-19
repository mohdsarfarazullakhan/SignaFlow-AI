import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Search, SlidersHorizontal } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { compactMoney, date } from "../lib/format";
import type { Lead } from "../types";
import { Badge, Empty, ErrorState, Loading, PageHeader } from "../components/ui";

export function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]); const [search, setSearch] = useState(""); const [temperature, setTemperature] = useState(""); const [error, setError] = useState("");
  useEffect(() => { api<Lead[]>("/leads").then(setLeads).catch(err => setError(err.message)); }, []);
  const filtered = useMemo(() => leads.filter(lead => (!temperature || lead.lead_temperature === temperature) && (!search || `${lead.customer_name} ${lead.company} ${lead.requirement}`.toLowerCase().includes(search.toLowerCase()))), [leads, search, temperature]);
  return <><PageHeader eyebrow="CRM" title="Sales opportunities" description="Every lead carries its requirement, product context, deterministic score, and recommended next action." /><div className="toolbar"><label className="search-field"><Search size={18} /><input placeholder="Search name, company, requirement…" value={search} onChange={e => setSearch(e.target.value)} /></label><label className="select-field"><SlidersHorizontal size={17} /><select value={temperature} onChange={e => setTemperature(e.target.value)}><option value="">All temperatures</option><option>Hot</option><option>Warm</option><option>Cold</option></select></label></div>
  {error ? <ErrorState message={error} /> : !leads.length ? <Loading label="Loading CRM" /> : !filtered.length ? <Empty title="No matching leads" text="Try a different search or score filter." /> : <div className="table-card"><table><thead><tr><th>Opportunity</th><th>Requirement</th><th>Score</th><th>Status</th><th>Budget</th><th>Created</th><th /></tr></thead><tbody>{filtered.map(lead => <tr key={lead.id}><td><b>{lead.company || lead.customer_name}</b><small>{lead.customer_name} • {lead.location || "Location not provided"}</small></td><td><span className="truncate">{lead.requirement}</span></td><td><Badge tone={lead.lead_temperature.toLowerCase() as "hot" | "warm" | "cold"}>{lead.lead_temperature} · {lead.lead_score}</Badge></td><td>{lead.lead_status.replaceAll("_", " ")}</td><td>{compactMoney(lead.budget)}</td><td>{date(lead.created_at)}</td><td><Link className="icon-button" to={`/leads/${lead.id}`} aria-label="Open lead"><ArrowRight /></Link></td></tr>)}</tbody></table></div>}</>;
}

