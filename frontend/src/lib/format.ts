export const money = (value?: number | null) => value == null ? "Price to be confirmed" : new Intl.NumberFormat("en-AE", { style: "currency", currency: "AED", maximumFractionDigits: 2 }).format(value);
export const compactMoney = (value?: number | null) => value == null ? "—" : new Intl.NumberFormat("en-AE", { style: "currency", currency: "AED", notation: "compact", maximumFractionDigits: 1 }).format(value);
export const date = (value: string) => new Intl.DateTimeFormat("en-AE", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(value));

