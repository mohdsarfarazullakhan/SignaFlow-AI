import { useEffect, useState } from "react";
import { ArrowUpRight, CircleDollarSign, Flame, Layers3, Quote, Users } from "lucide-react";
import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../lib/api";
import { compactMoney } from "../lib/format";
import { ErrorState, Loading, MetricCard, PageHeader } from "../components/ui";

export function DashboardPage() {
  const [data, setData] = useState<any>();
  const [error, setError] = useState("");
  useEffect(() => { api("/analytics/overview").then(setData).catch(err => setError(err.message)); }, []);
  if (error) return <ErrorState message={error} />;
  if (!data) return <Loading label="Calculating CRM metrics" />;
  const metrics = data.metrics;
  return <>
    <PageHeader eyebrow="SALES COMMAND CENTER" title="Good afternoon, sales team." description="Focus today’s effort on the opportunities with the clearest path to revenue." action={<span className="data-label"><i />{data.label}</span>} />
    <div className="metric-grid"><MetricCard label="Total leads" value={metrics.total_leads} detail={`${metrics.new_leads} new`} icon={<Users />} /><MetricCard label="Hot leads" value={metrics.hot_leads} detail="Priority follow-up" icon={<Flame />} /><MetricCard label="Pipeline value" value={compactMoney(metrics.pipeline_value)} detail="Open opportunities" icon={<CircleDollarSign />} /><MetricCard label="Quotes generated" value={metrics.quotes_generated} detail="Database calculated" icon={<Quote />} /></div>
    <div className="dashboard-grid"><section className="panel chart-panel"><div className="panel-heading"><div><span>LEAD MIX</span><h3>Opportunities by industry</h3></div><Link to="/leads">Open CRM <ArrowUpRight size={16} /></Link></div><div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><BarChart data={data.leads_by_industry}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e6e9ed" /><XAxis dataKey="name" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} /><YAxis allowDecimals={false} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} /><Tooltip cursor={{ fill: "#f6f7f8" }} /><Bar dataKey="value" fill="#d94b55" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer></div></section><section className="panel insights-panel"><div className="panel-heading"><div><span>AI-READY INSIGHTS</span><h3>Where to focus</h3></div><Layers3 size={20} /></div>{data.insights.map((text: string, index: number) => <div className="insight-row" key={text}><span>{index + 1}</span><p>{text}</p></div>)}</section></div>
    <section className="panel pipeline-panel"><div className="panel-heading"><div><span>PIPELINE HEALTH</span><h3>Sales stages</h3></div><small>Calculated from CRM records</small></div><div className="pipeline-bars">{data.pipeline.map((row: any) => <div key={row.name}><div><span>{row.name}</span><b>{row.value}</b></div><i><em style={{ width: `${Math.max(5, row.value / Math.max(1, metrics.total_leads) * 100)}%` }} /></i></div>)}</div></section>
  </>;
}

