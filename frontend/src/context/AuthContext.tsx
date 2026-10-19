import { createContext, ReactNode, useContext, useEffect, useState } from "react";
import { api } from "../lib/api";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null; loading: boolean; login: (email: string, password: string) => Promise<void>; logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const raw = localStorage.getItem("dsai_user");
    return raw ? JSON.parse(raw) as User : null;
  });
  const [loading, setLoading] = useState(Boolean(localStorage.getItem("dsai_token")));

  useEffect(() => {
    if (!localStorage.getItem("dsai_token")) { setLoading(false); return; }
    api<User>("/auth/me").then(setUser).catch(() => { localStorage.removeItem("dsai_token"); localStorage.removeItem("dsai_user"); setUser(null); }).finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const result = await api<{ access_token: string; user: User }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
    localStorage.setItem("dsai_token", result.access_token);
    localStorage.setItem("dsai_user", JSON.stringify(result.user));
    setUser(result.user);
  }
  function logout() { localStorage.removeItem("dsai_token"); localStorage.removeItem("dsai_user"); setUser(null); }
  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}

