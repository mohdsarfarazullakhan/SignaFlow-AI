import { useEffect, useState } from "react";
import { Download, FileCheck2 } from "lucide-react";
import { api, downloadQuotePdf } from "../lib/api";
import { date, money } from "../lib/format";
import type { Quote } from "../types";
import { Badge, Empty, ErrorState, Loading, PageHeader } from "../components/ui";

export function QuotationsPage() {
  const [quotes, setQuotes] = useState<Quote[]>([]); const [error, setError] = useState("");
  useEffect(() => { api<Quote[]>("/quotes").then(setQuotes).catch(err => setError(err.message)); }, []);
  return <><PageHeader eyebrow="COMMERCIAL CONTROL" title="Quotation drafts" description="Prices come from product records and every total, VAT amount, and status is controlled by application code." />{error ? <ErrorState message={error} /> : !quotes.length ? <Empty title="No quotation drafts yet" text="Open a CRM lead and ask the Sales Copilot to prepare one." /> : <div className="quote-grid">{quotes.map(quote => <article className="quote-card" key={quote.id}><div className="quote-card-head"><span><FileCheck2 /></span><Badge tone="warm">{quote.status}</Badge></div><h3>{quote.reference}</h3><p>{quote.company || quote.customer}</p><dl><div><dt>Date</dt><dd>{date(quote.created_at)}</dd></div><div><dt>Items</dt><dd>{quote.items.length}</dd></div><div><dt>VAT</dt><dd>{quote.vat_rate}%</dd></div></dl><div className="quote-total"><span>Grand total{quote.has_unconfirmed_pricing && "*"}</span><strong>{money(quote.grand_total)}</strong></div>{quote.has_unconfirmed_pricing && <small>* Excludes unconfirmed-price items.</small>}<button className="button secondary full" onClick={() => downloadQuotePdf(quote.id, quote.reference)}><Download /> Download draft PDF</button></article>)}</div>}</>;
}

