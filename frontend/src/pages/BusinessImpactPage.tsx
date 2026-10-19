import { useEffect, useState } from "react";
import { ArrowUpRight, Gauge, Target } from "lucide-react";
import { api } from "../lib/api";
import { ErrorState, Loading, PageHeader } from "../components/ui";

export function BusinessImpactPage() {
  const [data, setData] = useState<any>(); const [error, setError] = useState(""); useEffect(() => { api("/business-impact").then(setData).catch(err => setError(err.message)); }, []);
  return <><PageHeader eyebrow="VALUE REALIZATION" title="Business impact framework" description="Measure the operating changes that matter—without presenting prototype targets as achieved results." />{error ? <ErrorState message={error} /> : !data ? <Loading /> : <><div className="impact-hero"><Target /><div><span>{data.label}</span><h2>Make AI accountable to the sales process.</h2><p>Establish a baseline during the pilot, then measure time saved, conversion movement, and solution quality.</p></div></div><div className="impact-grid">{data.items.map((item: any, index: number) => <article key={item.metric}><div><span>0{index + 1}</span><Gauge /></div><h3>{item.metric}</h3><dl><div><dt>Baseline</dt><dd>{item.baseline}</dd></div><div><dt>Target direction</dt><dd>{item.target}</dd></div></dl><button>Define pilot measure <ArrowUpRight /></button></article>)}</div><p className="impact-notice">{data.notice}</p></>}</>;
}

