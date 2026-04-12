import { useEffect, useState } from "react";
import axios from "axios";
import AdminNav from "../../components/AdminNav";
import { getToken, getUser } from "../../utils/auth";

const ADMIN = "http://localhost:8000/admin";

const ROLE_COLORS = {
  industry:   "bg-blue-500/20 text-blue-300 border-blue-500/40",
  university: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
  admin:      "bg-red-500/20 text-red-300 border-red-500/40",
};

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-IN", { year: "numeric", month: "short", day: "numeric" });
}

export default function AdminUsers() {
  const [users,    setUsers]    = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState("");
  const [updating, setUpdating] = useState({});  // { [user_id]: boolean }
  const [selRole,  setSelRole]  = useState({});   // { [user_id]: string }
  const [rowError, setRowError] = useState({});   // { [user_id]: string }

  const me    = getUser();
  const hdrs  = { Authorization: `Bearer ${getToken()}` };

  async function fetchUsers() {
    setLoading(true); setError("");
    try {
      const { data } = await axios.get(`${ADMIN}/users`, { headers: hdrs });
      const list = Array.isArray(data) ? data : data.users ?? [];
      setUsers(list);
      // seed role selectors
      const roles = {};
      list.forEach(u => { roles[u.id] = u.role; });
      setSelRole(roles);
    } catch {
      setError("Failed to load users.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchUsers(); }, []);

  async function handleRoleUpdate(userId) {
    setUpdating(p => ({ ...p, [userId]: true }));
    setRowError(p => ({ ...p, [userId]: "" }));
    try {
      const { data } = await axios.put(
        `${ADMIN}/users/${userId}/role`,
        { role: selRole[userId] },
        { headers: hdrs }
      );
      setUsers(p => p.map(u => u.id === userId ? { ...u, role: selRole[userId] } : u));
    } catch (err) {
      setRowError(p => ({ ...p, [userId]: err.response?.data?.detail ?? "Update failed" }));
    } finally {
      setUpdating(p => ({ ...p, [userId]: false }));
    }
  }

  async function handleDelete(userId) {
    if (!window.confirm("Are you sure you want to delete this user?")) return;
    setUpdating(p => ({ ...p, [userId]: true }));
    setRowError(p => ({ ...p, [userId]: "" }));
    try {
      await axios.delete(`${ADMIN}/users/${userId}`, { headers: hdrs });
      setUsers(p => p.filter(u => u.id !== userId));
    } catch (err) {
      setRowError(p => ({ ...p, [userId]: err.response?.data?.detail ?? "Delete failed" }));
    } finally {
      setUpdating(p => ({ ...p, [userId]: false }));
    }
  }

  const isSelf = (u) => u.id === me?.user_id || u.id === me?.id;

  return (
    <div className="min-h-screen bg-slate-900 text-white" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <AdminNav />

      <main className="max-w-6xl mx-auto px-6 py-10">

        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <h1 className="text-4xl text-white" style={{ fontFamily: "'DM Serif Display', serif" }}>
            User Management
          </h1>
          {!loading && (
            <span className="bg-slate-700/70 text-slate-300 text-xs font-semibold px-3 py-1 rounded-full border border-slate-600/50">
              {users.length} users
            </span>
          )}
        </div>

        {loading && (
          <div className="flex justify-center py-24">
            <div className="w-10 h-10 border-2 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" />
          </div>
        )}

        {error && (
          <div className="bg-red-900/30 border border-red-700/60 rounded-xl px-5 py-4 text-red-300 text-sm mb-6">{error}</div>
        )}

        {!loading && !error && (
          <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700/60 text-slate-400 text-xs uppercase tracking-widest">
                  <th className="px-6 py-4 text-left w-12">ID</th>
                  <th className="px-6 py-4 text-left">Email</th>
                  <th className="px-6 py-4 text-left w-32">Role</th>
                  <th className="px-6 py-4 text-left w-36">Joined</th>
                  <th className="px-6 py-4 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u, idx) => {
                  const self    = isSelf(u);
                  const busy    = updating[u.id];
                  const rError  = rowError[u.id];
                  return (
                    <tr
                      key={u.id}
                      className={`border-b border-slate-700/30 transition-colors ${idx % 2 === 0 ? "" : "bg-slate-800/20"} ${self ? "opacity-70" : "hover:bg-slate-700/20"}`}
                    >
                      {/* ID */}
                      <td className="px-6 py-4 text-slate-500">{u.id}</td>

                      {/* Email */}
                      <td className="px-6 py-4 text-white font-medium">
                        {u.email}
                        {self && (
                          <span className="ml-2 text-xs text-cyan-500">(you)</span>
                        )}
                      </td>

                      {/* Role pill */}
                      <td className="px-6 py-4">
                        <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${ROLE_COLORS[u.role] ?? "bg-slate-700 text-slate-300 border-slate-600"}`}>
                          {u.role}
                        </span>
                      </td>

                      {/* Joined */}
                      <td className="px-6 py-4 text-slate-400">{formatDate(u.created_at)}</td>

                      {/* Actions */}
                      <td className="px-6 py-4">
                        {self ? (
                          <span className="text-slate-600 text-xs italic">Cannot modify your own account</span>
                        ) : (
                          <div className="flex flex-col gap-2">
                            <div className="flex items-center gap-2">
                              <select
                                value={selRole[u.id] ?? u.role}
                                onChange={e => setSelRole(p => ({ ...p, [u.id]: e.target.value }))}
                                className="bg-slate-700 border border-slate-600 text-white text-xs rounded-lg px-2 py-1.5 focus:outline-none focus:border-cyan-500"
                              >
                                {["industry", "university", "admin"].map(r => (
                                  <option key={r} value={r}>{r}</option>
                                ))}
                              </select>
                              <button
                                onClick={() => handleRoleUpdate(u.id)}
                                disabled={busy}
                                className="bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-600 text-white text-xs font-medium px-3 py-1.5 rounded-lg transition"
                              >
                                {busy ? "…" : "Update"}
                              </button>
                              <button
                                onClick={() => handleDelete(u.id)}
                                disabled={busy}
                                className="border border-red-700/60 hover:bg-red-900/30 disabled:opacity-40 text-red-400 text-xs font-medium px-3 py-1.5 rounded-lg transition"
                              >
                                Delete
                              </button>
                            </div>
                            {rError && <p className="text-red-400 text-xs">{rError}</p>}
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
