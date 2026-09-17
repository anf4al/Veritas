import React, { useEffect, useState } from "react";
import { User } from "../../types";
import { api } from "../../services/api";
import { Users, Shield, Building2, CheckCircle2 } from "lucide-react";

export const UsersTab: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.listUsers()
      .then(setUsers)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex-1 flex flex-col h-full bg-[#09090b] overflow-hidden p-8">
      <div className="pb-6 border-b border-zinc-800">
        <h1 className="text-xl font-semibold text-white tracking-tight">Users, Roles & Access Control</h1>
        <p className="text-xs text-zinc-400 mt-1">
          Manage system identities, assigned companies, and granular RBAC permissions.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto mt-6 border border-zinc-800 rounded-xl bg-[#0e0e11]">
        <table className="w-full text-left text-xs">
          <thead className="bg-zinc-900/80 text-zinc-400 font-mono text-[11px] uppercase border-b border-zinc-800 sticky top-0">
            <tr>
              <th className="py-3 px-4">User</th>
              <th className="py-3 px-4">Role</th>
              <th className="py-3 px-4">Assigned Companies</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Permissions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {loading ? (
              <tr>
                <td colSpan={5} className="text-center py-12 text-zinc-500">
                  Loading users...
                </td>
              </tr>
            ) : users.map((u) => (
              <tr key={u.id} className="hover:bg-zinc-900/40 transition">
                <td className="py-3 px-4">
                  <div className="font-medium text-white">{u.display_name}</div>
                  <div className="text-[11px] font-mono text-zinc-500">{u.username}</div>
                </td>
                <td className="py-3 px-4">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-zinc-800 text-zinc-300 border border-zinc-700">
                    {u.role}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <div className="flex flex-wrap gap-1">
                    {u.companies && u.companies.length > 0 ? (
                      u.companies.map((c) => (
                        <span key={c.id} className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-300">
                          {c.name}
                        </span>
                      ))
                    ) : (
                      <span className="text-zinc-600 text-[10px]">None</span>
                    )}
                  </div>
                </td>
                <td className="py-3 px-4">
                  <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
                    <CheckCircle2 size={12} /> {u.status}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <div className="flex flex-wrap gap-1 max-w-sm">
                    {u.permissions?.slice(0, 4).map((p) => (
                      <span key={p} className="text-[9px] font-mono px-1 rounded bg-black/40 border border-zinc-800 text-zinc-400">
                        {p}
                      </span>
                    ))}
                    {(u.permissions?.length || 0) > 4 && (
                      <span className="text-[9px] font-mono px-1 rounded bg-black/40 border border-zinc-800 text-zinc-500">
                        +{u.permissions.length - 4} more
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

