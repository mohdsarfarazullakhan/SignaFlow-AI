export type Role = "CUSTOMER" | "SALES" | "ADMIN";

export interface User { id: string; name: string; email: string; role: Role }
export interface Product {
  id: string; name: string; slug: string; category: string; subcategory?: string; description: string;
  use_cases: string[]; industries: string[]; environment?: string; dimensions?: string; material?: string;
  brand?: string; specifications_json: Record<string, string>; price?: number; currency: string; availability?: string;
  source: string; source_url?: string; image_url?: string; is_demo: boolean;
}
export interface Requirement {
  industry?: string; business_type?: string; location?: string; use_case: string;
  indoor_outdoor: "indoor" | "outdoor" | "both" | "unknown"; quantity?: number; indoor_quantity?: number;
  outdoor_quantity?: number; dimensions?: string; screen_size?: string; budget?: number; timeline?: string;
  installation_requirement?: string; content_requirement?: string; preferred_product_type?: string;
  contact_intent: string; source_text: string;
}
export interface Recommendation {
  product: Product; confidence_score: number; retrieval_score: number; why_it_matches: string;
  recommended_use: string; matched_signals: string[]; missing_information: string[];
}
export interface SolutionItem { product_id: string; product_name: string; quantity: number; role: string; rationale: string; optional: boolean; unit_price?: number; currency: string }
export interface Solution { name: string; summary: string; items: SolutionItem[]; compatibility_notes: string[]; optional_upgrades: string[]; pricing_note: string }
export interface Lead {
  id: string; customer_name: string; company?: string; email?: string; phone?: string; whatsapp?: string; industry?: string;
  location?: string; requirement: string; requirement_json: Record<string, unknown>; recommended_products: Record<string, unknown>[];
  solution_json: Record<string, unknown>; budget?: number; timeline?: string; quotation_requested: boolean; lead_score: number;
  lead_temperature: "Cold" | "Warm" | "Hot"; lead_status: string; source: string; assigned_salesperson?: string; notes?: string;
  created_at: string; updated_at: string;
}
export interface QuoteItem { id: string; product_id?: string; description: string; quantity: number; unit_price?: number; line_total?: number }
export interface Quote { id: string; reference: string; lead_id?: string; customer: string; company?: string; quote_date: string; subtotal: number; vat_rate: number; vat_amount: number; grand_total: number; has_unconfirmed_pricing: boolean; terms: string; notes?: string; status: string; items: QuoteItem[]; created_at: string }
export interface Campaign { id: string; campaign_name: string; business: string; offer: string; screen_format: string; resolution: string; audience: string; language: string; tone: string; content_json: Record<string, any>; status: string; is_demo: boolean; created_at: string }

