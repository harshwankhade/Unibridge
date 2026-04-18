import { useEffect, useState } from "react";
import axios from "axios";
import AdminNav from "../../components/AdminNav";
import { getToken } from "../../utils/auth";

const ADMIN = "http://localhost:8000/admin";

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

const CAT_COLORS = {
  solve:     "bg-blue-100 text-blue-700 border-blue-200",
  benchmark: "bg-purple-100 text-purple-700 border-purple-200",
  landscape: "bg-teal-100 text-teal-700 border-teal-200",
};

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-white border border-[#e8e4d9] shadow-sm rounded-2xl p-6">
      <p className="text-[#8888aa] text-xs uppercase tracking-widest mb-2">{label}</p>
      <p className="text-3xl font-semibold text-[#1a1a2e] mb-1">{value ?? 0}</p>
      {sub && <p className="text-[#8888aa] text-xs">{sub}</p>}
    </div>
  );
}

export default function AdminDashboard() {
  const [dataStats,   setDataStats]   = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [users,       setUsers]       = useState([]);
  const [recent,      setRecent]      = useState([]);
  const [loading,     setLoading]     = useState(true);
  const hdrs = { Authorization: `Bearer ${getToken()}` };

  useEffect(() => {
    (async () => {
      const [ds, subs, usrs, rec] = await Promise.allSettled([
        axios.get(`${ADMIN}/data/stats`,                { headers: hdrs }),
        axios.get(`${ADMIN}/submissions`,               { headers: hdrs }),
        axios.get(`${ADMIN}/users`,                     { headers: hdrs }),
        axios.get(`${ADMIN}/analytics/recent?limit=10`, { headers: hdrs }),
      ]);
      if (ds.status   === "fulfilled") setDataStats(ds.value.data);
      if (subs.status === "fulfilled") setSubmissions(subs.value.data.submissions ?? []);
      if (usrs.status === "fulfilled") setUsers(usrs.value.data.users ?? []);
      if (rec.status  === "fulfilled") setRecent(rec.value.data.recent ?? []);
      setLoading(false);
    })();
  }, []);

  const pending = submissions.filter(s => s.status === "pending").length;
  const now     = new Date().toLocaleString("en-IN", { dateStyle: "long", timeStyle: "short" });

  return (
    <div className="min-h-screen bg-[#fdfcf7] text-[#1a1a2e]" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <AdminNav pendingCount={pending} />

      <main className="max-w-6xl mx-auto px-6 py-10">

        {/* Header */}
        <div className="flex items-start justify-between mb-10">
          <div>
            <h1 className="text-4xl text-[#1a1a2e] mb-2" style={{ fontFamily: "'DM Serif Display', serif" }}>
              Admin Dashboard
            </h1>
            <p className="text-[#8888aa] text-sm">{now}</p>
          </div>
          {loading && <div className="w-6 h-6 border-2 border-[#0d9488]/30 border-t-[#0d9488] rounded-full animate-spin mt-3" />}
        </div>

        {/* Top stats row */}
        <div className="grid grid-cols-4 gap-4 mb-5">
          <StatCard label="Total Records"       value={dataStats?.total_records}  sub="indexed in platform" />
          <StatCard label="Total Users"         value={users.length}              sub="registered accounts" />
          <StatCard label="Pending Submissions" value={pending}                   sub="awaiting review"     />
          <StatCard label="Recent Searches"     value={recent.length}             sub="last 10 events"      />
        </div>

        {/* Second stats row */}
        <div className="grid grid-cols-3 gap-4 mb-10">
          <StatCard label="Patents"        value={dataStats?.source_distribution?.patent ?? 0} sub="indexed patents" />
          <StatCard label="Papers"         value={dataStats?.source_distribution?.paper  ?? 0} sub="indexed papers"  />
          <StatCard label="Indian Records" value={dataStats?.indian_records              ?? 0} sub="from India"      />
        </div>

        {/* Recent Searches feed */}
        <div>
          <h2 className="text-xl text-[#1a1a2e] mb-5" style={{ fontFamily: "'DM Serif Display', serif" }}>
            Recent Searches
          </h2>
          {recent.length === 0 ? (
            <p className="text-[#8888aa] text-sm">No search events logged yet.</p>
          ) : (
            <div className="space-y-2">
              {recent.map((e) => (
                <div
                  key={e.id}
                  className="flex items-center gap-4 bg-white border border-[#e8e4d9] rounded-xl px-5 py-3 shadow-sm"
                >
                  <p className="text-[#1a1a2e] font-medium text-sm flex-1 truncate">{e.query}</p>
                  <span className={`text-xs px-2.5 py-0.5 rounded-full border ${CAT_COLORS[e.category] ?? "bg-[#f7f5ed] text-[#4a4a6a] border-[#e8e4d9]"}`}>
                    {e.category}
                  </span>
                  <span className="text-[#4a4a6a] text-xs w-16 text-right">{e.result_count} results</span>
                  <span className="text-[#8888aa] text-xs w-16 text-right">{timeAgo(e.created_at)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

      </main>
    </div>
  );
}
