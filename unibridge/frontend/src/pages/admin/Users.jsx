import { useEffect, useState } from "react";
import axios from "axios";
import AdminNav from "../../components/AdminNav";
import { getToken, getUser } from "../../utils/auth";

const ADMIN = "http://localhost:8000/admin";

const ROLE_COLORS = {
  industry:   "bg-blue-100 text-blue-800 border-blue-200",
  university: "bg-teal-100 text-teal-800 border-teal-200",
  admin:      "bg-red-100 text-red-800 border-red-200",
};

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-IN", { year: "numeric", month: "short", day: "numeric" });
}

export default function AdminUsers() {
  const [users,    setUsers]    = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState("");
  const [updating, setUpdating] = useState({});
  const [selRole,  setSelRole]  = useState({});
  const [rowError, setRowError] = useState({});

  const me   = getUser();
  const hdrs = { Authorization: `Bearer ${getToken()}` };

  async function fetchUsers() {
    setLoading(true); setError("");
    try {
      const { data } = await axios.get(`${ADMIN}/users`, { headers: hdrs });
      const list = Array.isArray(data) ? data : data.users ?? [];
      setUsers(list);
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
      await axios.put(
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
    <div className="min-h-screen bg-[#fdfcf7] text-[#1a1a2e]" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <AdminNav />

      <main className="max-w-6xl mx-auto px-6 py-10">

        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <h1 className="text-4xl text-[#1a1a2e]" style={{ fontFamily: "'DM Serif Display', serif" }}>
            User Management
          </h1>
          {!loading && (
            <span className="bg-[#f7f5ed] text-[#4a4a6a] text-xs font-semibold px-3 py-1 rounded-full border border-[#e8e4d9]">
              {users.length} users
            </span>
          )}
        </div>

        {loading && (
          <div className="flex justify-center py-24">
            <div className="w-10 h-10 border-2 border-[#0d9488]/30 border-t-[#0d9488] rounded-full animate-spin" />
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-5 py-4 text-red-700 text-sm mb-6">{error}</div>
        )}

        {!loading && !error && (
          <div className="bg-white border border-[#e8e4d9] shadow-sm rounded-2xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#e8e4d9] text-[#8888aa] text-xs uppercase tracking-widest">
                  <th className="px-6 py-4 text-left w-12">ID</th>
                  <th className="px-6 py-4 text-left">Email</th>
                  <th className="px-6 py-4 text-left w-32">Role</th>
                  <th className="px-6 py-4 text-left w-36">Joined</th>
                  <th className="px-6 py-4 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u, idx) => {
                  const self   = isSelf(u);
                  const busy   = updating[u.id];
                  const rError = rowError[u.id];
                  return (
                    <tr
                      key={u.id}
                      className={`border-b border-[#e8e4d9] transition-colors ${idx % 2 === 0 ? "" : "bg-[#fdfcf7]"} ${self ? "opacity-70" : "hover:bg-[#f7f5ed]"}`}
                    >
                      {/* ID */}
                      <td className="px-6 py-4 text-[#8888aa]">{u.id}</td>

                      {/* Email */}
                      <td className="px-6 py-4 text-[#1a1a2e] font-medium">
                        {u.email}
                        {self && (
                          <span className="ml-2 text-xs text-[#0d9488]">(you)</span>
                        )}
                      </td>

                      {/* Role pill */}
                      <td className="px-6 py-4">
                        <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${ROLE_COLORS[u.role] ?? "bg-[#f7f5ed] text-[#4a4a6a] border-[#e8e4d9]"}`}>
                          {u.role}
                        </span>
                      </td>

                      {/* Joined */}
                      <td className="px-6 py-4 text-[#4a4a6a]">{formatDate(u.created_at)}</td>

                      {/* Actions */}
                      <td className="px-6 py-4">
                        {self ? (
                          <span className="text-[#8888aa] text-xs italic">Cannot modify your own account</span>
                        ) : (
                          <div className="flex flex-col gap-2">
                            <div className="flex items-center gap-2">
                              <select
                                value={selRole[u.id] ?? u.role}
                                onChange={e => setSelRole(p => ({ ...p, [u.id]: e.target.value }))}
                                className="bg-white border border-[#e8e4d9] text-[#1a1a2e] text-xs rounded-lg px-2 py-1.5 focus:outline-none focus:border-[#0d9488]"
                              >
                                {["industry", "university", "admin"].map(r => (
                                  <option key={r} value={r}>{r}</option>
                                ))}
                              </select>
                              <button
                                onClick={() => handleRoleUpdate(u.id)}
                                disabled={busy}
                                className="bg-[#0d9488] hover:bg-[#0f766e] disabled:bg-[#8888aa] text-white text-xs font-medium px-3 py-1.5 rounded-lg transition"
                              >
                                {busy ? "…" : "Update"}
                              </button>
                              <button
                                onClick={() => handleDelete(u.id)}
                                disabled={busy}
                                className="border border-red-300 hover:bg-red-50 disabled:opacity-40 text-red-600 text-xs font-medium px-3 py-1.5 rounded-lg transition"
                              >
                                Delete
                              </button>
                            </div>
                            {rError && <p className="text-red-600 text-xs">{rError}</p>}
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
