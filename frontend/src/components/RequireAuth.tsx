import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Loading } from "./ui";

export function RequireAuth() {
  const { user, loading } = useAuth();
  if (loading) return <main className="center-page"><Loading label="Opening workspace" /></main>;
  return user ? <Outlet /> : <Navigate to="/login" replace />;
}
