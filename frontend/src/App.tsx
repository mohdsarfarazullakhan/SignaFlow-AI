import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { RequireAuth } from "./components/RequireAuth";
import { Loading } from "./components/ui";
import { AuthProvider } from "./context/AuthContext";

const page = <T extends Record<string, unknown>>(loader: () => Promise<T>, name: keyof T) => lazy(async () => ({ default: (await loader())[name] as React.ComponentType }));
const LoginPage = page(() => import("./pages/LoginPage"), "LoginPage");
const HomePage = page(() => import("./pages/HomePage"), "HomePage");
const AdvisorPage = page(() => import("./pages/AdvisorPage"), "AdvisorPage");
const ProductsPage = page(() => import("./pages/ProductsPage"), "ProductsPage");
const DashboardPage = page(() => import("./pages/DashboardPage"), "DashboardPage");
const LeadsPage = page(() => import("./pages/LeadsPage"), "LeadsPage");
const LeadDetailPage = page(() => import("./pages/LeadDetailPage"), "LeadDetailPage");
const CopilotPage = page(() => import("./pages/CopilotPage"), "CopilotPage");
const QuotationsPage = page(() => import("./pages/QuotationsPage"), "QuotationsPage");
const CampaignStudioPage = page(() => import("./pages/CampaignStudioPage"), "CampaignStudioPage");
const AnalyticsPage = page(() => import("./pages/AnalyticsPage"), "AnalyticsPage");
const SmartSignagePage = page(() => import("./pages/SmartSignagePage"), "SmartSignagePage");
const VisualAdvisorPage = page(() => import("./pages/VisualAdvisorPage"), "VisualAdvisorPage");
const OpportunitiesPage = page(() => import("./pages/OpportunitiesPage"), "OpportunitiesPage");
const BusinessImpactPage = page(() => import("./pages/BusinessImpactPage"), "BusinessImpactPage");
const AdminPage = page(() => import("./pages/AdminPage"), "AdminPage");
const SettingsPage = page(() => import("./pages/SettingsPage"), "SettingsPage");

export default function App() {
  return <BrowserRouter><AuthProvider><Suspense fallback={<main className="center-page"><Loading label="Opening module" /></main>}><Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route element={<RequireAuth />}><Route element={<Layout />}>
      <Route index element={<HomePage />} />
      <Route path="advisor" element={<AdvisorPage />} />
      <Route path="products" element={<ProductsPage />} />
      <Route path="dashboard" element={<DashboardPage />} />
      <Route path="leads" element={<LeadsPage />} />
      <Route path="leads/:id" element={<LeadDetailPage />} />
      <Route path="sales-copilot" element={<CopilotPage />} />
      <Route path="quotations" element={<QuotationsPage />} />
      <Route path="campaign-studio" element={<CampaignStudioPage />} />
      <Route path="analytics" element={<AnalyticsPage />} />
      <Route path="smart-signage" element={<SmartSignagePage />} />
      <Route path="visual-advisor" element={<VisualAdvisorPage />} />
      <Route path="website-opportunities" element={<OpportunitiesPage />} />
      <Route path="business-impact" element={<BusinessImpactPage />} />
      <Route path="admin" element={<AdminPage />} />
      <Route path="settings" element={<SettingsPage />} />
    </Route></Route>
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes></Suspense></AuthProvider></BrowserRouter>;
}
