import { FormEvent, useState } from "react";
import { ArrowRight, Check, ChevronRight, CircleDollarSign, ClipboardCheck, ExternalLink, LoaderCircle, MapPin, PackageCheck, Send, Sparkles, WandSparkles } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { money } from "../lib/format";
import type { Lead, Recommendation, Requirement, Solution } from "../types";
import { Badge, ErrorState, PageHeader } from "../components/ui";
import { useAuth } from "../context/AuthContext";

const scenarios = [
  "I am opening a restaurant in Dubai. I need three indoor digital menu screens and one outdoor advertising screen.",
  "I own a retail shop and want a display near the entrance.",
  "I run a signage company and need materials for outdoor illuminated signage.",
  "We have a hotel and want digital wayfinding screens.",
  "I need equipment for large-format advertising printing.",
];

export function AdvisorPage() {
  const { user } = useAuth();
  const [message, setMessage] = useState(scenarios[0]);
  const [requirement, setRequirement] = useState<Requirement>();
  const [question, setQuestion] = useState<string>();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [solution, setSolution] = useState<Solution>();
  const [stage, setStage] = useState<"idle" | "understanding" | "recommending" | "solution" | "lead">("idle");
  const [error, setError] = useState("");
  const [showLead, setShowLead] = useState(false);
  const [lead, setLead] = useState<Lead>();
  const [contact, setContact] = useState({ customer_name: "Ahmed Mansoor", company: "ABC Restaurant Group", email: "ahmed@example.com", phone: "+971 50 000 2026", budget: "35000", timeline: "2 weeks" });

  async function understand(event?: FormEvent) {
    event?.preventDefault(); setStage("understanding"); setError(""); setRequirement(undefined); setRecommendations([]); setSolution(undefined); setLead(undefined);
    try {
      const result = await api<{ requirement: Requirement; clarification_question?: string }>("/requirements/extract", { method: "POST", body: JSON.stringify({ message }) });
      setRequirement(result.requirement); setQuestion(result.clarification_question);
      if (!result.clarification_question) await findProducts(result.requirement);
      else setStage("idle");
    } catch (err) { setError(err instanceof Error ? err.message : "Could not understand this requirement"); setStage("idle"); }
  }

  async function findProducts(value = requirement) {
    if (!value) return; setStage("recommending"); setError("");
    try { const result = await api<{ recommendations: Recommendation[] }>("/recommend", { method: "POST", body: JSON.stringify({ requirement: value, limit: 3 }) }); setRecommendations(result.recommendations); setStage("idle"); }
    catch (err) { setError(err instanceof Error ? err.message : "Product search is temporarily unavailable"); setStage("idle"); }
  }

  async function buildSolution() {
    if (!requirement) return; setStage("solution"); setError("");
    try { const result = await api<Solution>("/solutions/build", { method: "POST", body: JSON.stringify({ requirement, recommendation_product_ids: recommendations.map(item => item.product.id) }) }); setSolution(result); setStage("idle"); setTimeout(() => document.getElementById("solution")?.scrollIntoView({ behavior: "smooth" }), 50); }
    catch (err) { setError(err instanceof Error ? err.message : "Could not build the solution"); setStage("idle"); }
  }

  async function createLead(event: FormEvent) {
    event.preventDefault(); if (!requirement || !solution) return; setStage("lead"); setError("");
    try {
      const result = await api<Lead>("/leads", { method: "POST", body: JSON.stringify({ ...contact, budget: Number(contact.budget) || null, industry: requirement.industry, location: requirement.location, requirement: requirement.source_text, requirement_json: { ...requirement, timeline: contact.timeline }, recommended_products: recommendations.map(item => ({ product_id: item.product.id, name: item.product.name, confidence_score: item.confidence_score })), solution_json: solution, timeline: contact.timeline, quotation_requested: true, source: "AI Product Advisor" }) });
      setLead(result); setShowLead(false);
    } catch (err) { setError(err instanceof Error ? err.message : "Could not create the quotation request"); } finally { setStage("idle"); }
  }

  return <>
    <PageHeader eyebrow="CUSTOMER INTELLIGENCE" title="Describe the outcome. We’ll find the products." description="No technical catalogue knowledge required. The advisor turns a business need into a grounded, complete signage solution." />
    <section className="advisor-shell"><div className="advisor-main"><div className="assistant-intro"><div className="ai-orb"><Sparkles /></div><div><b>SignaFlow Product Advisor</b><p>Tell me about the business, the space, and what the signage should achieve. I’ll ask only what changes the recommendation.</p></div></div>
      <div className="scenario-list">{scenarios.map((scenario, index) => <button key={scenario} className={message === scenario ? "selected" : ""} onClick={() => setMessage(scenario)}><span>0{index + 1}</span>{scenario}</button>)}</div>
      <form className="advisor-input" onSubmit={understand}><textarea value={message} onChange={event => setMessage(event.target.value)} aria-label="Describe your signage requirement" /><button aria-label="Find matching products" disabled={stage !== "idle"}>{stage === "understanding" || stage === "recommending" ? <LoaderCircle className="spin" /> : <Send />}</button></form><div className="advisor-hint"><WandSparkles size={15} /> Try the preloaded restaurant scenario for the complete demo journey.</div>
    </div><aside className="advisor-steps"><h3>Journey progress</h3>{[["Requirement", requirement], ["Product shortlist", recommendations.length], ["Complete solution", solution], ["Qualified lead", lead]].map(([label, done], index) => <div className={done ? "done" : ""} key={String(label)}><span>{done ? <Check size={15} /> : index + 1}</span><p>{String(label)}</p></div>)}</aside></section>
    {error && <ErrorState message={error} />}
    {question && !recommendations.length && <section className="clarification-card"><div><Sparkles /><span><b>One useful question</b>{question}</span></div><p>Add the answer to your requirement above, then run the advisor again.</p></section>}
    {requirement && <section className="panel requirement-panel"><div className="panel-heading"><div><span>STRUCTURED REQUIREMENT</span><h3>What the advisor understood</h3></div><Badge tone="accent">AI extracted</Badge></div><div className="requirement-grid"><Data label="Industry" value={requirement.industry} /><Data label="Location" value={requirement.location} icon={<MapPin />} /><Data label="Use case" value={requirement.use_case} /><Data label="Environment" value={requirement.indoor_outdoor} /><Data label="Total quantity" value={requirement.quantity} /><Data label="Indoor / outdoor" value={`${requirement.indoor_quantity ?? 0} / ${requirement.outdoor_quantity ?? 0}`} /></div></section>}
    {recommendations.length > 0 && <section className="recommendation-section"><div className="section-title"><div><div className="eyebrow">CATALOGUE-GROUNDED</div><h2>Recommended products</h2><p>Ranked with semantic relevance, industry, environment, use case, and catalogue availability signals.</p></div><button className="button primary" onClick={buildSolution} disabled={stage !== "idle"}>{stage === "solution" ? <LoaderCircle className="spin" /> : <PackageCheck />} Build complete solution</button></div><div className="recommendation-grid">{recommendations.map((item, index) => <article className="recommendation-card" key={item.product.id}><div className="recommendation-rank">0{index + 1}</div><div className="recommendation-top"><Badge tone="warm">{item.product.is_demo ? "Demo Product" : "Verified source"}</Badge><strong>{item.confidence_score}% match</strong></div><h3>{item.product.name}</h3><p>{item.product.description}</p><div className="match-reasons">{item.matched_signals.slice(0, 3).map(signal => <span key={signal}><Check size={13} />{signal}</span>)}</div><dl><div><dt>Recommended use</dt><dd>{item.recommended_use}</dd></div><div><dt>Environment</dt><dd>{item.product.environment || "Specification not available"}</dd></div><div><dt>Size</dt><dd>{item.product.dimensions || "Specification not available"}</dd></div></dl><div className="product-price"><span>Catalogue price</span><b>{money(item.product.price)}</b></div>{item.product.source_url && <a href={item.product.source_url} target="_blank" rel="noreferrer">View source <ExternalLink size={14} /></a>}</article>)}</div></section>}
    {solution && <section className="solution-section" id="solution"><div className="solution-heading"><div><div className="eyebrow light">SOLUTION ARCHITECT</div><h2>{solution.name}</h2><p>{solution.summary}</p></div><ClipboardCheck /></div><div className="solution-table"><div className="solution-row head"><span>Component</span><span>Role</span><span>Qty</span><span>Unit price</span></div>{solution.items.map(item => <div className={item.optional ? "solution-row optional" : "solution-row"} key={`${item.product_id}-${item.role}`}><span><b>{item.product_name}</b><small>{item.rationale}</small></span><span>{item.role}{item.optional && <Badge>Optional</Badge>}</span><span>{item.quantity}</span><span>{money(item.unit_price)}</span></div>)}</div><div className="solution-footer"><div><b>Compatibility checkpoints</b>{solution.compatibility_notes.map(note => <p key={note}><Check size={14} />{note}</p>)}</div><button className="button primary" onClick={() => setShowLead(true)}><CircleDollarSign /> Request quotation</button></div></section>}
    {showLead && <div className="modal-backdrop"><form className="modal" onSubmit={createLead}><button type="button" className="modal-close" onClick={() => setShowLead(false)}>×</button><div className="eyebrow">CREATE QUALIFIED LEAD</div><h2>Request a quotation</h2><p>Demo details are pre-filled so the scoring and CRM journey can be shown end to end.</p><div className="form-grid"><label>Name<input required value={contact.customer_name} onChange={e => setContact({ ...contact, customer_name: e.target.value })} /></label><label>Company<input value={contact.company} onChange={e => setContact({ ...contact, company: e.target.value })} /></label><label>Email<input required type="email" value={contact.email} onChange={e => setContact({ ...contact, email: e.target.value })} /></label><label>Phone<input required value={contact.phone} onChange={e => setContact({ ...contact, phone: e.target.value })} /></label><label>Budget (AED)<input type="number" value={contact.budget} onChange={e => setContact({ ...contact, budget: e.target.value })} /></label><label>Timeline<input value={contact.timeline} onChange={e => setContact({ ...contact, timeline: e.target.value })} /></label></div><button className="button primary full" disabled={stage === "lead"}>{stage === "lead" ? <LoaderCircle className="spin" /> : <ArrowRight />} Create quotation request</button></form></div>}
    {lead && <section className="lead-success"><div><span><Check /></span><div><div className="eyebrow light">LEAD CREATED & SCORED</div><h2>{lead.lead_temperature} — {lead.lead_score}/100</h2><p>The requirement, product shortlist, and complete solution are now attached to the CRM lead.</p></div></div>{user?.role !== "CUSTOMER" ? <Link className="button light" to={`/leads/${lead.id}`}>Open in CRM <ChevronRight /></Link> : <Badge tone="success">Sales follow-up ready</Badge>}</section>}
  </>;
}

function Data({ label, value, icon }: { label: string; value?: string | number | null; icon?: React.ReactNode }) { return <div><span>{label}</span><b>{icon}{value ?? "Not provided"}</b></div>; }
