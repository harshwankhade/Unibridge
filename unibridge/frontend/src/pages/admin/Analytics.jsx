import { useEffect, useState } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import AdminNav from "../../components/AdminNav";
import { getToken } from "../../utils/auth";

const ADMIN = "http://localhost:8000/admin";
const hdrs  = () => ({ Authorization: `Bearer ${getToken()}` });

const PIE_COLORS = { solve: "#60a5fa", benchmark: "#a78bfa", landscape: "#2dd4bf" };
const PIE_FALLBACK = ["#60a5fa", "#a78bfa", "#2dd4bf", "#f59e0b", "#34d399"];

function ChartBox({ title, children, failed }) {
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6">
      <h3 className="text-white font-semibold mb-5" style={{ fontFamily: "'DM Serif Display', serif" }}>
        {title}
      </h3>
      {failed
        ? <p className="text-red-400 text-sm">Failed to load</p>
        : children
      }
    </div>
  );
}

const truncate = (str, n) => str?.length > n ? str.slice(0, n) + "…" : str;

export default function AdminAnalytics() {
  const [trending,   setTrending]   = useState(null);
  const [gaps,       setGaps]       = useState(null);
  const [trlDist,    setTrlDist]    = useState(null);
  const [catBreak,   setCatBreak]   = useState(null);
  const [failed,     setFailed]     = useState({});
  const [loading,    setLoading]    = useState(true);

  useEffect(() => {
    (async () => {
      const [tr, gp, trl, cb] = await Promise.allSettled([
        axios.get(`${ADMIN}/analytics/trending`,          { headers: hdrs() }),
        axios.get(`${ADMIN}/analytics/gaps`,              { headers: hdrs() }),
        axios.get(`${ADMIN}/analytics/trl-distribution`,  { headers: hdrs() }),
        axios.get(`${ADMIN}/analytics/category-breakdown`,{ headers: hdrs() }),
      ]);

      if (tr.status  === "fulfilled") setTrending(tr.value.data.trending ?? []);
      else setFailed(p => ({ ...p, trending: true }));

      if (gp.status  === "fulfilled") setGaps(gp.value.data.gaps ?? []);
      else setFailed(p => ({ ...p, gaps: true }));

      if (trl.status === "fulfilled") setTrlDist(trl.value.data.trl_distribution ?? {});
      else setFailed(p => ({ ...p, trl: true }));

      if (cb.status  === "fulfilled") setCatBreak(cb.value.data.category_breakdown ?? []);
      else setFailed(p => ({ ...p, catBreak: true }));

      setLoading(false);
    })();
  }, []);

  // Convert trl_dist object → pie array
  const pieData = trlDist
    ? Object.entries(trlDist).map(([name, value]) => ({ name, value }))
    : [];

  const tooltipStyle = {
    backgroundColor: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "10px",
    color: "#f1f5f9",
    fontSize: "12px",
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center" style={{ fontFamily: "'DM Sans', sans-serif" }}>
        <div className="w-10 h-10 border-2 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <AdminNav />

      <main className="max-w-6xl mx-auto px-6 py-10">

        {/* Header */}
        <div className="mb-10">
          <h1 className="text-4xl text-white mb-2" style={{ fontFamily: "'DM Serif Display', serif" }}>
            Analytics
          </h1>
          <p className="text-slate-400 text-sm">Platform search behaviour and research gap intelligence</p>
        </div>

        {/* Row 1 */}
        <div className="grid grid-cols-2 gap-6 mb-6">

          {/* Trending Searches */}
          <ChartBox title="Trending Searches" failed={failed.trending}>
            {!trending || trending.length === 0 ? (
              <p className="text-slate-500 text-sm">No search data yet</p>
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={trending} layout="vertical" margin={{ left: 10, right: 20 }}>
                  <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                  <YAxis type="category" dataKey="query" width={140} tick={{ fill: "#cbd5e1", fontSize: 11 }}
                    tickFormatter={v => truncate(v, 22)} />
                  <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(45,212,191,0.05)" }} />
                  <Bar dataKey="count" fill="#2dd4bf" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </ChartBox>

          {/* Search Category Breakdown (Pie) */}
          <ChartBox title="Search Category Breakdown" failed={failed.trl}>
            {pieData.length === 0 ? (
              <p className="text-slate-500 text-sm">No category data yet</p>
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="45%"
                    outerRadius={90}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={{ stroke: "#475569" }}
                  >
                    {pieData.map((entry, i) => (
                      <Cell key={entry.name} fill={PIE_COLORS[entry.name] ?? PIE_FALLBACK[i % PIE_FALLBACK.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} />
                  <Legend wrapperStyle={{ fontSize: "12px", color: "#94a3b8" }} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </ChartBox>
        </div>

        {/* Row 2 */}
        <div className="grid grid-cols-2 gap-6">

          {/* Domain Breakdown */}
          <ChartBox title="Domain Breakdown" failed={failed.catBreak}>
            {!catBreak || catBreak.length === 0 ? (
              <p className="text-slate-500 text-sm">No domain data yet</p>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={catBreak} margin={{ bottom: 30 }}>
                  <XAxis
                    dataKey="domain"
                    tick={{ fill: "#94a3b8", fontSize: 10 }}
                    tickFormatter={v => truncate(v, 12)}
                    angle={-35}
                    textAnchor="end"
                  />
                  <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                  <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(96,165,250,0.05)" }} />
                  <Bar dataKey="count" fill="#60a5fa" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </ChartBox>

          {/* Research Gaps */}
          <ChartBox title="Unmet Queries (0 results)" failed={failed.gaps}>
            {!gaps || gaps.length === 0 ? (
              <p className="text-emerald-400 text-sm">
                ✓ No gaps detected — all searches returned results
              </p>
            ) : (
              <div className="space-y-2 mt-1">
                {gaps.map((g, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between bg-slate-700/40 border border-slate-600/40 rounded-xl px-4 py-2.5"
                  >
                    <span className="text-slate-200 text-sm truncate flex-1 mr-3">{g.query}</span>
                    <span className="bg-red-900/50 text-red-300 border border-red-700/50 text-xs font-bold px-2.5 py-0.5 rounded-full flex-shrink-0">
                      {g.count}×
                    </span>
                  </div>
                ))}
              </div>
            )}
          </ChartBox>
        </div>

      </main>
    </div>
  );
}
