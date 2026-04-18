import { useNavigate } from "react-router-dom";
import { getUser } from "../../utils/auth";

const BOOKMARKS_KEY = "unibridge_bookmarks";

function getBookmarks() {
  try { return JSON.parse(localStorage.getItem(BOOKMARKS_KEY)) || []; }
  catch { return []; }
}

export default function Dashboard() {
  const navigate  = useNavigate();
  const user      = getUser();
  const bookmarks = getBookmarks();

  return (
    <div
      className="min-h-screen bg-[#fdfcf7] text-[#1a1a2e]"
      style={{ fontFamily: "'DM Sans', sans-serif" }}
    >
      {/* ── Nav bar ── */}
      <nav className="bg-white border-b border-[#e8e4d9] shadow-sm px-8 py-4 flex items-center justify-between">
        <span className="text-[#0d9488] font-bold text-xl tracking-tight" style={{ fontFamily: "'DM Serif Display', serif" }}>
          UniBridge
        </span>
        <span className="text-[#8888aa] text-sm">{user?.email}</span>
      </nav>

      <main className="max-w-5xl mx-auto px-6 py-12">

        {/* ── Welcome header ── */}
        <div className="mb-10">
          <h1
            className="text-4xl text-[#1a1a2e] mb-2"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            Welcome back
          </h1>
          <p className="text-[#4a4a6a] text-base">{user?.email}</p>
        </div>

        {/* ── Stat card ── */}
        <div className="mb-10">
          <div className="bg-white border border-[#e8e4d9] shadow-sm rounded-2xl p-6 inline-block min-w-[180px]">
            <p className="text-[#8888aa] text-xs uppercase tracking-widest mb-2">Bookmarks</p>
            <p className="text-3xl font-semibold text-[#1a1a2e] mb-1">{bookmarks.length}</p>
            <p className="text-[#8888aa] text-xs">saved results</p>
          </div>
        </div>

        {/* ── Quick actions ── */}
        <div className="flex gap-4 mb-14">
          <button
            onClick={() => navigate("/industry/search")}
            className="bg-[#0d9488] hover:bg-[#0f766e] text-white font-semibold px-6 py-3 rounded-xl transition"
          >
            🔍 Start Searching
          </button>
          <button
            onClick={() => navigate("/industry/bookmarks")}
            className="border border-[#0d9488] text-[#0d9488] bg-transparent hover:bg-[#ccfbf1] font-medium px-6 py-3 rounded-xl transition"
          >
            🔖 View Bookmarks
          </button>
        </div>

        {/* ── How it works ── */}
        <div>
          <h2
            className="text-xl text-[#1a1a2e] mb-6"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            How it works
          </h2>
          <div className="grid grid-cols-3 gap-5">
            {[
              { step: "01", title: "Choose your search mode",  desc: "Select Solve, Benchmark, or Landscape to frame your need." },
              { step: "02", title: "Describe your need",        desc: "Write in plain business language — no jargon required."    },
              { step: "03", title: "Explore matched research",  desc: "Browse university patents and papers ranked by relevance." },
            ].map(({ step, title, desc }) => (
              <div key={step} className="bg-white border border-[#e8e4d9] shadow-sm rounded-2xl p-6">
                <span className="text-[#0d9488] text-xs font-bold tracking-widest">{step}</span>
                <h3 className="text-[#1a1a2e] font-semibold mt-2 mb-2 text-sm">{title}</h3>
                <p className="text-[#4a4a6a] text-xs leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
