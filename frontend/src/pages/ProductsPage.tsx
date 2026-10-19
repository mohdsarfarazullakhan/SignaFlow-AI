import { useEffect, useMemo, useState } from "react";
import { Box, Search, SlidersHorizontal } from "lucide-react";
import { api } from "../lib/api";
import { money } from "../lib/format";
import type { Product } from "../types";
import { Badge, Empty, ErrorState, Loading, PageHeader } from "../components/ui";

export function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => { api<{ items: Product[]; categories: string[] }>("/products").then(data => { setProducts(data.items); setCategories(data.categories); }).catch(err => setError(err.message)).finally(() => setLoading(false)); }, []);
  const filtered = useMemo(() => products.filter(product => (!category || product.category === category) && (!search || `${product.name} ${product.description} ${product.use_cases.join(" ")}`.toLowerCase().includes(search.toLowerCase()))), [products, search, category]);
  return <><PageHeader eyebrow="CATALOGUE INTELLIGENCE" title="Product knowledge base" description="Grounded product records used by search, recommendations, solutions, and quotations." />
    <div className="toolbar"><label className="search-field"><Search size={18} /><input placeholder="Search products, use cases, materials…" value={search} onChange={e => setSearch(e.target.value)} /></label><label className="select-field"><SlidersHorizontal size={17} /><select value={category} onChange={e => setCategory(e.target.value)}><option value="">All categories</option>{categories.map(item => <option key={item}>{item}</option>)}</select></label><span className="result-count">{filtered.length} records</span></div>
    {loading ? <Loading label="Loading catalogue" /> : error ? <ErrorState message={error} /> : filtered.length === 0 ? <Empty title="No products found" text="Try a broader category or natural-language query." /> : <div className="product-grid">{filtered.map(product => <article className="product-card" key={product.id}><div className="product-visual"><Box /><span>{product.category}</span></div><div className="product-body"><div className="product-meta"><Badge tone={product.is_demo ? "warm" : "success"}>{product.is_demo ? "Demo Product" : "Public source"}</Badge><span>{product.environment || "Not specified"}</span></div><h3>{product.name}</h3><p>{product.description}</p><div className="spec-line"><span>{product.dimensions || "Specification not available"}</span><strong>{money(product.price)}</strong></div></div></article>)}</div>}
  </>;
}
