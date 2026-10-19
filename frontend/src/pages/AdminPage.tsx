import { FormEvent, useEffect, useState } from "react";
import { CheckCircle2, DatabaseZap, LoaderCircle, ShieldCheck, UploadCloud, Users } from "lucide-react";
import { api } from "../lib/api";
import type { User } from "../types";
import { Badge, ErrorState, Loading, PageHeader } from "../components/ui";

const sample = JSON.stringify([{ name: "Demo Counter Display Stand", category: "Accessories", subcategory: "Display Stands", description: "Illustrative counter display stand for the local demo catalogue.", use_cases: ["counter promotions"], industries: ["retail", "restaurant"], environment: "indoor", price: 175, currency: "AED" }], null, 2);

export function AdminPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [json, setJson] = useState(sample);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  useEffect(() => { api<User[]>("/admin/users").then(setUsers).catch(err => setError(err.message)); }, []);
  async function importProducts(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError(""); setResult("");
    try {
      const products = JSON.parse(json);
      const response = await api<{ created: number; updated: number; notice: string }>("/admin/products/import", { method: "POST", body: JSON.stringify({ source_label: "admin-demo-import", is_demo: true, products }) });
      setResult(`${response.created} created, ${response.updated} updated. ${response.notice}`);
    } catch (err) { setError(err instanceof Error ? err.message : "Import failed"); }
    finally { setBusy(false); }
  }
  return <><PageHeader eyebrow="ADMINISTRATION" title="Users & catalogue ingestion" description="Manage role visibility and import reviewed product records without exposing secrets or granting an AI agent mutation access." />
    <div className="admin-grid"><section className="panel"><div className="panel-heading"><div><span>ACCESS DIRECTORY</span><h3>Demo users and roles</h3></div><Users /></div>{users.length ? <div className="user-list">{users.map(user => <div key={user.id}><span>{user.name.slice(0, 2).toUpperCase()}</span><p><b>{user.name}</b><small>{user.email}</small></p><Badge tone={user.role === "ADMIN" ? "accent" : "neutral"}>{user.role}</Badge></div>)}</div> : error ? <ErrorState message={error} /> : <Loading label="Loading users" />}<div className="security-note"><ShieldCheck /> Password hashes and credentials are never returned by the API.</div></section><form className="panel import-panel" onSubmit={importProducts}><div className="panel-heading"><div><span>PRODUCT INGESTION</span><h3>Validated JSON import</h3></div><DatabaseZap /></div><p>Paste an approved JSON array. This panel intentionally imports Demo Products; public-source ingestion uses the robots-aware CLI pipeline.</p><textarea value={json} onChange={e => setJson(e.target.value)} aria-label="Product import JSON" /><button className="button primary" disabled={busy}>{busy ? <><LoaderCircle className="spin" /> Importing…</> : <><UploadCloud /> Validate & import demo records</>}</button>{result && <div className="import-success"><CheckCircle2 />{result}</div>}{error && users.length > 0 && <ErrorState message={error} />}</form></div>
  </>;
}

