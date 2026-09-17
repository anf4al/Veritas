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
        const match = u.companies.find(c => c.id === savedCompId) || u.companies[0];
        setActiveCompany(match);
        localStorage.setItem("veritas_active_company_id", match.id);
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
    const res = await api.switchCompany(companyId);
    if (res.new_token) {
      localStorage.setItem("veritas_token", res.new_token);
      setToken(res.new_token);
    }
    localStorage.setItem("veritas_active_company_id", companyId);
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

