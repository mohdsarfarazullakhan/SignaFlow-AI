import { useEffect, useState } from "react";
import { ArrowRight, Bot, CircleCheck, LineChart, Sparkles } from "lucide-react";
import { api } from "../lib/api";
import { ErrorState, Loading, PageHeader } from "../components/ui";

export function OpportunitiesPage() {
  const [data, setData] = useState<any>(); const [error, setError] = useState(""); useEffect(() => { api("/opportunities").then(setData).catch(err => setError(err.message)); }, []);
  return <><PageHeader eyebrow="DIGITAL OPPORTUNITY MAP" title="Build on a signage business’s strengths" description="A structured view of how an AI layer can make a product catalogue and signage operation easier to discover, sell, and measure." />{error ? <ErrorState message={error} /> : !data ? <Loading /> : <div className="opportunity-list">{data.items.map((item: any, index: number) => <article key={item.strength}><span className="opp-number">0{index + 1}</span><div className="opp-stage"><CircleCheck /><small>EXISTING STRENGTH</small><h3>{item.strength}</h3></div><ArrowRight /><div className="opp-stage"><Sparkles /><small>OPPORTUNITY</small><h3>{item.opportunity}</h3></div><ArrowRight /><div className="opp-stage highlight"><Bot /><small>AI ENHANCEMENT</small><h3>{item.enhancement}</h3></div><ArrowRight /><div className="opp-stage"><LineChart /><small>BUSINESS BENEFIT</small><h3>{item.benefit}</h3></div></article>)}</div>}</>;
}

