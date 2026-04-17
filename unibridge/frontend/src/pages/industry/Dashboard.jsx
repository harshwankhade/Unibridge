import { useNavigate } from "react-router-dom";
import { getUser } from "../../utils/auth";

const BOOKMARKS_KEY = "unibridge_bookmarks";

function getBookmarks() {
  try { return JSON.parse(localStorage.getItem(BOOKMARKS_KEY)) || []; }
  catch { return []; }
}

export default function Dashboard() {
  const navigate = useNavigate();
  const user = getUser();
  const bookmarks = getBookmarks();

  return (
    <div
      className="min-h-screen bg-slate-900 text-white"
      style={{ fontFamily: "'DM Sans', sans-serif" }}
    >
      {/* ── Nav bar ── */}
      <nav className="border-b border-slate-800 px-8 py-4 flex items-center justify-between">
        <span className="text-cyan-400 font-bold text-xl tracking-tight" style={{ fontFamily: "'DM Serif Display', serif" }}>
          UniBridge
        </span>
        <span className="text-slate-400 text-sm">{user?.email}</span>
      </nav>

      <main className="max-w-5xl mx-auto px-6 py-12">

        {/* ── Welcome header ── */}
        <div className="mb-10">
          <h1
            className="text-4xl text-white mb-2"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            Welcome back
          </h1>
          <p className="text-slate-400 text-base">{user?.email}</p>
        </div>

        {/* ── Stat card ── */}
        <div className="mb-10">
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6 inline-block min-w-[180px]">
            <p className="text-slate-400 text-xs uppercase tracking-widest mb-2">Bookmarks</p>
            <p className="text-3xl font-semibold text-white mb-1">{bookmarks.length}</p>
            <p className="text-slate-500 text-xs">saved results</p>
          </div>
        </div>

        {/* ── Quick actions ── */}
        <div className="flex gap-4 mb-14">
          <button
            onClick={() => navigate("/industry/search")}
            className="bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold px-6 py-3 rounded-xl transition"
          >
            🔍 Start Searching
          </button>
          <button
            onClick={() => navigate("/industry/bookmarks")}
            className="bg-slate-700 hover:bg-slate-600 text-white font-medium px-6 py-3 rounded-xl transition"
          >
            🔖 View Bookmarks
          </button>
        </div>

        {/* ── How it works ── */}
        <div>
          <h2
            className="text-xl text-white mb-6"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            How it works
          </h2>
          <div className="grid grid-cols-3 gap-5">
            {[
              { step: "01", title: "Choose your search mode",        desc: "Select Solve, Benchmark, or Landscape to frame your need." },
              { step: "02", title: "Describe your need",              desc: "Write in plain business language — no jargon required."     },
              { step: "03", title: "Explore matched research",        desc: "Browse university patents and papers ranked by relevance."  },
            ].map(({ step, title, desc }) => (
              <div key={step} className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-6">
                <span className="text-cyan-400 text-xs font-bold tracking-widest">{step}</span>
                <h3 className="text-white font-semibold mt-2 mb-2 text-sm">{title}</h3>
                <p className="text-slate-400 text-xs leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
