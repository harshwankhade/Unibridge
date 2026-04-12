import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { getUser, getToken, logout } from "../../utils/auth";

const SUB_SERVICE = "http://localhost:8000/submission";

export default function UniversityDashboard() {
  const navigate = useNavigate();
  const user = getUser();

  const [stats, setStats] = useState({ total: 0, pending: 0, approved: 0 });

  useEffect(() => {
    (async () => {
      try {
        const { data } = await axios.get(`${SUB_SERVICE}/submissions`, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        const subs = data.submissions || [];
        setStats({
          total:    subs.length,
          pending:  subs.filter((s) => s.status === "pending").length,
          approved: subs.filter((s) => s.status === "approved").length,
        });
      } catch {
        // leave stats at 0 on failure
      }
    })();
  }, []);

  const statCards = [
    { label: "Total Submissions", value: stats.total,    sub: "submitted by you"  },
    { label: "Pending Review",    value: stats.pending,  sub: "awaiting decision" },
    { label: "Approved",          value: stats.approved, sub: "indexed & live"    },
  ];

  const guidelines = [
    "Ensure your abstract clearly describes the technology and its applications",
    "Include all contributing researchers and inventors",
    "Select the most accurate domain for faster matching with industry partners",
    "Patents and research papers are both accepted",
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white" style={{ fontFamily: "'DM Sans', sans-serif" }}>

      {/* ── Nav ── */}
      <nav className="border-b border-slate-800 px-8 py-4 flex items-center justify-between">
        <span className="text-cyan-400 font-bold text-xl tracking-tight" style={{ fontFamily: "'DM Serif Display', serif" }}>
          UniBridge
        </span>
        <div className="flex items-center gap-6 text-sm text-slate-400">
          <Link to="/university/dashboard"    className="text-white font-medium">Dashboard</Link>
          <Link to="/university/submit"       className="hover:text-white transition">Submit IP</Link>
          <Link to="/university/submissions"  className="hover:text-white transition">My Submissions</Link>
          <button onClick={logout} className="hover:text-red-400 transition">Sign out</button>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-6 py-12">

        {/* ── Header ── */}
        <div className="mb-10">
          <h1 className="text-4xl text-white mb-2" style={{ fontFamily: "'DM Serif Display', serif" }}>
            University Portal
          </h1>
          <p className="text-slate-400 text-base">Welcome, {user?.email}</p>
        </div>

        {/* ── Stat cards ── */}
        <div className="grid grid-cols-3 gap-5 mb-10">
          {statCards.map(({ label, value, sub }) => (
            <div key={label} className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
              <p className="text-slate-400 text-xs uppercase tracking-widest mb-2">{label}</p>
              <p className="text-3xl font-semibold text-white mb-1">{value}</p>
              <p className="text-slate-500 text-xs">{sub}</p>
            </div>
          ))}
        </div>

        {/* ── Quick actions ── */}
        <div className="flex gap-4 mb-14">
          <button
            onClick={() => navigate("/university/submit")}
            className="bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold px-6 py-3 rounded-xl transition"
          >
            📤 Submit New IP
          </button>
          <button
            onClick={() => navigate("/university/submissions")}
            className="bg-slate-700 hover:bg-slate-600 text-white font-medium px-6 py-3 rounded-xl transition"
          >
            📋 View My Submissions
          </button>
        </div>

        {/* ── Submission Guidelines ── */}
        <div>
          <h2 className="text-xl text-white mb-4" style={{ fontFamily: "'DM Serif Display', serif" }}>
            Submission Guidelines
          </h2>
          <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-6">
            <ul className="space-y-3">
              {guidelines.map((g, i) => (
                <li key={i} className="flex items-start gap-3 text-slate-300 text-sm leading-relaxed">
                  <span className="text-cyan-400 font-bold mt-0.5">0{i + 1}</span>
                  {g}
                </li>
              ))}
            </ul>
          </div>
        </div>

      </main>
    </div>
  );
}
