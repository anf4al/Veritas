import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { User, Company } from "../types";
import { api } from "../services/api";

interface AuthContextType {
  user: User | null;
  activeCompany: Company | null;
  token: string | null;
  loading: boolean;
  login: (username: string, password: string, company_id?: string) => Promise<void>;
  logout: () => void;
  switchActiveCompany: (companyId: string) => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [activeCompany, setActiveCompany] = useState<Company | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("veritas_token"));
  const [loading, setLoading] = useState<boolean>(true);

  const refreshProfile = async () => {
    try {
      const u = await api.getMe();
      setUser(u);
      if (u.companies && u.companies.length > 0) {
        const savedCompId = localStorage.getItem("veritas_active_company_id");
        // Authorized companies are the absolute source of truth.
        // If a savedCompId exists and is in the user's authorized companies, preserve it.
        // Otherwise, prioritize the authoritative active_company_id from the backend profile.
        let targetComp = u.companies.find(c => c.id === savedCompId);
        if (!targetComp && u.active_company_id) {
          targetComp = u.companies.find(c => c.id === u.active_company_id);
        }
        if (!targetComp) {
          targetComp = u.companies[0];
        }
        setActiveCompany(targetComp);
        localStorage.setItem("veritas_active_company_id", targetComp.id);
      } else {
        setActiveCompany(null);
        localStorage.removeItem("veritas_active_company_id");
      }
    } catch {
      logout();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      refreshProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (username: string, password: string, company_id?: string) => {
    // If no explicit company_id is provided, clear stale persisted selection
    // to prevent cross-session or previous user tenant bleed
    if (!company_id) {
      localStorage.removeItem("veritas_active_company_id");
    }
    const data = await api.login(username, password, company_id);
    localStorage.setItem("veritas_token", data.access_token);
    setToken(data.access_token);
    setUser(data.user);

    if (data.user.companies && data.user.companies.length > 0) {
      const initialComp = data.user.companies.find((c: Company) => c.id === data.user.active_company_id) || data.user.companies[0];
      setActiveCompany(initialComp);
      localStorage.setItem("veritas_active_company_id", initialComp.id);
    }
  };

  const logout = () => {
    localStorage.removeItem("veritas_token");
    localStorage.removeItem("veritas_active_company_id");
    setToken(null);
    setUser(null);
    setActiveCompany(null);
  };

  const switchActiveCompany = async (companyId: string) => {
    // Verify target company is authorized for current user
    if (user && user.companies && !user.companies.some(c => c.id === companyId)) {
      throw new Error(`Unauthorized company ID: ${companyId}`);
    }
    const res = await api.switchCompany(companyId);
    if (res.new_token) {
      localStorage.setItem("veritas_token", res.new_token);
      setToken(res.new_token);
    }
    localStorage.setItem("veritas_active_company_id", companyId);
    if (user?.companies) {
      const match = user.companies.find(c => c.id === companyId);
      if (match) {
        setActiveCompany(match);
      }
    }
    await refreshProfile();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        activeCompany,
        token,
        loading,
        login,
        logout,
        switchActiveCompany,
        refreshProfile
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};

