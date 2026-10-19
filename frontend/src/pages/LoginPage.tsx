import { FormEvent, useState } from "react";
import { ArrowRight, Building2, CheckCircle2, LoaderCircle, ShieldCheck, Sparkles } from "lucide-react";
import { Navigate, useNavigate } from "react-router-dom";
import hero from "../assets/signaflow-ai-hero.png";
import { useAuth } from "../context/AuthContext";

const accounts = [
  { label: "Sales workspace", email: "sales@signaflow.example.com", detail: "CRM, Copilot, quotes & analytics" },
  { label: "Admin workspace", email: "admin@signaflow.example.com", detail: "All modules & settings" },
  { label: "Customer journey", email: "customer@signaflow.example.com", detail: "Advisor & campaign preview" },
];

export function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState(accounts[0].email);
  const [password, setPassword] = useState("demo123");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  if (user) return <Navigate to="/" replace />;
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    try { await login(email, password); navigate("/"); } catch (err) { setError(err instanceof Error ? err.message : "Could not sign in"); } finally { setBusy(false); }
  }
  return <main className="login-page">
    <section className="login-visual" style={{ backgroundImage: `linear-gradient(90deg, rgba(11,19,31,.98) 0%, rgba(11,19,31,.78) 52%, rgba(11,19,31,.12) 100%), url(${hero})` }}>
      <div className="login-brand"><span><Building2 /></span><b>SignaFlow AI</b></div>
      <div className="login-copy"><div className="eyebrow light"><Sparkles size={14} /> INTELLIGENT SIGNAGE PLATFORM</div><h1>From Requirement<br />to Revenue.</h1><p>One connected operating layer for product discovery, sales automation, campaigns, and measurable signage.</p><div className="login-proof"><span><CheckCircle2 /> Catalogue-grounded recommendations</span><span><CheckCircle2 /> Human-controlled business actions</span><span><CheckCircle2 /> Reliable offline demo mode</span></div></div>
      <div className="login-visual-footer"><ShieldCheck /> Groq keys stay on the backend. Product prices never come from an LLM.</div>
    </section>
    <section className="login-panel"><div className="login-form-wrap"><div className="eyebrow">SECURE WORKSPACE</div><h2>Welcome to SignaFlow AI</h2><p>Choose a demo workspace or sign in with configured credentials.</p><div className="account-grid">{accounts.map(account => <button key={account.email} type="button" className={email === account.email ? "account-option selected" : "account-option"} onClick={() => { setEmail(account.email); setPassword("demo123"); }}><span>{account.label}</span><small>{account.detail}</small></button>)}</div><form onSubmit={submit}><label>Email<input value={email} onChange={event => setEmail(event.target.value)} type="email" autoComplete="email" required /></label><label>Password<input value={password} onChange={event => setPassword(event.target.value)} type="password" autoComplete="current-password" required /></label>{error && <div className="form-error">{error}</div>}<button className="button primary full" disabled={busy}>{busy ? <><LoaderCircle className="spin" size={18} /> Signing in…</> : <>Enter workspace <ArrowRight size={18} /></>}</button></form><small className="demo-note">Demo credentials are local-only and configurable via environment variables.</small></div></section>
  </main>;
}

