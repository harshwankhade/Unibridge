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

const PIE_COLORS   = { solve: "#60a5fa", benchmark: "#a78bfa", landscape: "#0d9488" };
const PIE_FALLBACK = ["#60a5fa", "#a78bfa", "#0d9488", "#f59e0b", "#34d399"];

function ChartBox({ title, children, failed }) {
  return (
    <div className="bg-white border border-[#e8e4d9] shadow-sm rounded-2xl p-6">
      <h3 className="text-[#1a1a2e] font-semibold mb-5" style={{ fontFamily: "'DM Serif Display', serif" }}>
        {title}
      </h3>
      {failed
        ? <p className="text-red-600 text-sm">Failed to load</p>
        : children
      }
    </div>
  );
}

const truncate = (str, n) => str?.length > n ? str.slice(0, n) + "…" : str;

export default function AdminAnalytics() {
  const [trending, setTrending] = useState(null);
  const [gaps,     setGaps]     = useState(null);
  const [trlDist,  setTrlDist]  = useState(null);
  const [catBreak, setCatBreak] = useState(null);
  const [failed,   setFailed]   = useState({});
  const [loading,  setLoading]  = useState(true);

  useEffect(() => {
    (async () => {
      const [tr, gp, trl, cb] = await Promise.allSettled([
        axios.get(`${ADMIN}/analytics/trending`,           { headers: hdrs() }),
        axios.get(`${ADMIN}/analytics/gaps`,               { headers: hdrs() }),
        axios.get(`${ADMIN}/analytics/trl-distribution`,   { headers: hdrs() }),
        axios.get(`${ADMIN}/analytics/category-breakdown`, { headers: hdrs() }),
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

  const pieData = trlDist
    ? Object.entries(trlDist).map(([name, value]) => ({ name, value }))
    : [];

  // Light-mode tooltip style
  const tooltipStyle = {
    backgroundColor: "#ffffff",
    border: "1px solid #e8e4d9",
    borderRadius: "10px",
    color: "#1a1a2e",
    fontSize: "12px",
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#fdfcf7] text-[#1a1a2e] flex items-center justify-center" style={{ fontFamily: "'DM Sans', sans-serif" }}>
        <div className="w-10 h-10 border-2 border-[#0d9488]/30 border-t-[#0d9488] rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#fdfcf7] text-[#1a1a2e]" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <AdminNav />

      <main className="max-w-6xl mx-auto px-6 py-10">

        {/* Header */}
        <div className="mb-10">
          <h1 className="text-4xl text-[#1a1a2e] mb-2" style={{ fontFamily: "'DM Serif Display', serif" }}>
            Analytics
          </h1>
          <p className="text-[#4a4a6a] text-sm">Platform search behaviour and research gap intelligence</p>
        </div>

        {/* Row 1 */}
        <div className="grid grid-cols-2 gap-6 mb-6">

          {/* Trending Searches */}
          <ChartBox title="Trending Searches" failed={failed.trending}>
            {!trending || trending.length === 0 ? (
              <p className="text-[#8888aa] text-sm">No search data yet</p>
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={trending} layout="vertical" margin={{ left: 10, right: 20 }}>
                  <XAxis type="number" tick={{ fill: "#4a4a6a", fontSize: 11 }} />
                  <YAxis type="category" dataKey="query" width={140} tick={{ fill: "#1a1a2e", fontSize: 11 }}
                    tickFormatter={v => truncate(v, 22)} />
                  <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(13,148,136,0.05)" }} />
                  <Bar dataKey="count" fill="#0d9488" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </ChartBox>

          {/* Search Category Breakdown (Pie) */}
          <ChartBox title="Search Category Breakdown" failed={failed.trl}>
            {pieData.length === 0 ? (
              <p className="text-[#8888aa] text-sm">No category data yet</p>
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
                    labelLine={{ stroke: "#e8e4d9" }}
                  >
                    {pieData.map((entry, i) => (
                      <Cell key={entry.name} fill={PIE_COLORS[entry.name] ?? PIE_FALLBACK[i % PIE_FALLBACK.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} />
                  <Legend wrapperStyle={{ fontSize: "12px", color: "#4a4a6a" }} />
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
              <p className="text-[#8888aa] text-sm">No domain data yet</p>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={catBreak} margin={{ bottom: 30 }}>
                  <XAxis
                    dataKey="domain"
                    tick={{ fill: "#4a4a6a", fontSize: 10 }}
                    tickFormatter={v => truncate(v, 12)}
                    angle={-35}
                    textAnchor="end"
                  />
                  <YAxis tick={{ fill: "#4a4a6a", fontSize: 11 }} />
                  <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(96,165,250,0.05)" }} />
                  <Bar dataKey="count" fill="#60a5fa" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </ChartBox>

          {/* Research Gaps */}
          <ChartBox title="Unmet Queries (0 results)" failed={failed.gaps}>
            {!gaps || gaps.length === 0 ? (
              <p className="text-green-700 text-sm">
                ✓ No gaps detected — all searches returned results
              </p>
            ) : (
              <div className="space-y-2 mt-1">
                {gaps.map((g, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between bg-[#f7f5ed] border border-[#e8e4d9] rounded-xl px-4 py-2.5"
                  >
                    <span className="text-[#1a1a2e] text-sm truncate flex-1 mr-3">{g.query}</span>
                    <span className="bg-red-100 text-red-700 border border-red-200 text-xs font-bold px-2.5 py-0.5 rounded-full flex-shrink-0">
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
