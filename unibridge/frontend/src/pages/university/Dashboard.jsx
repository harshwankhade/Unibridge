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
    <div className="min-h-screen bg-[#fdfcf7] text-[#1a1a2e]" style={{ fontFamily: "'DM Sans', sans-serif" }}>

      {/* ── Nav ── */}
      <nav className="bg-white border-b border-[#e8e4d9] shadow-sm px-8 py-4 flex items-center justify-between">
        <span className="text-[#0d9488] font-bold text-xl tracking-tight" style={{ fontFamily: "'DM Serif Display', serif" }}>
          UniBridge
        </span>
        <div className="flex items-center gap-6 text-sm text-[#4a4a6a]">
          <Link to="/university/dashboard"   className="text-[#0d9488] font-semibold">Dashboard</Link>
          <Link to="/university/submit"      className="hover:text-[#0d9488] transition">Submit IP</Link>
          <Link to="/university/submissions" className="hover:text-[#0d9488] transition">My Submissions</Link>
          <button onClick={logout} className="text-[#dc2626] hover:bg-red-50 px-2 py-1 rounded-lg transition">Sign out</button>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-6 py-12">

        {/* ── Header ── */}
        <div className="mb-10">
          <h1 className="text-4xl text-[#1a1a2e] mb-2" style={{ fontFamily: "'DM Serif Display', serif" }}>
            University Portal
          </h1>
          <p className="text-[#4a4a6a] text-base">Welcome, {user?.email}</p>
        </div>

        {/* ── Stat cards ── */}
        <div className="grid grid-cols-3 gap-5 mb-10">
          {statCards.map(({ label, value, sub }) => (
            <div key={label} className="bg-white border border-[#e8e4d9] shadow-sm rounded-2xl p-6">
              <p className="text-[#8888aa] text-xs uppercase tracking-widest mb-2">{label}</p>
              <p className="text-3xl font-semibold text-[#1a1a2e] mb-1">{value}</p>
              <p className="text-[#8888aa] text-xs">{sub}</p>
            </div>
          ))}
        </div>

        {/* ── Quick actions ── */}
        <div className="flex gap-4 mb-14">
          <button
            onClick={() => navigate("/university/submit")}
            className="bg-[#0d9488] hover:bg-[#0f766e] text-white font-semibold px-6 py-3 rounded-xl transition"
          >
            📤 Submit New IP
          </button>
          <button
            onClick={() => navigate("/university/submissions")}
            className="border border-[#0d9488] text-[#0d9488] bg-transparent hover:bg-[#ccfbf1] font-medium px-6 py-3 rounded-xl transition"
          >
            📋 View My Submissions
          </button>
        </div>

        {/* ── Submission Guidelines ── */}
        <div>
          <h2 className="text-xl text-[#1a1a2e] mb-4" style={{ fontFamily: "'DM Serif Display', serif" }}>
            Submission Guidelines
          </h2>
          <div className="bg-white border border-[#e8e4d9] shadow-sm rounded-2xl p-6">
            <ul className="space-y-3">
              {guidelines.map((g, i) => (
                <li key={i} className="flex items-start gap-3 text-[#4a4a6a] text-sm leading-relaxed">
                  <span className="text-[#0d9488] font-bold mt-0.5">0{i + 1}</span>
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
