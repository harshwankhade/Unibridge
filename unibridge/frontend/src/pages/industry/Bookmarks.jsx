import { useState } from "react";
import { Link } from "react-router-dom";
import TechCard from "../../components/TechCard";

const BOOKMARKS_KEY = "unibridge_bookmarks";

function loadBookmarks() {
  try { return JSON.parse(localStorage.getItem(BOOKMARKS_KEY)) || []; }
  catch { return []; }
}

function saveBookmarks(bm) {
  localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bm));
}

export default function Bookmarks() {
  const [bookmarks, setBookmarks] = useState(loadBookmarks);

  const handleRemove = (result) => {
    setBookmarks((prev) => {
      const next = prev.filter((b) => b.id !== result.id);
      saveBookmarks(next);
      return next;
    });
  };

  const clearAll = () => {
    localStorage.removeItem(BOOKMARKS_KEY);
    setBookmarks([]);
  };

  return (
    <div
      className="min-h-screen bg-[#fdfcf7] text-[#1a1a2e]"
      style={{ fontFamily: "'DM Sans', sans-serif" }}
    >
      {/* ── Nav ── */}
      <nav className="bg-white border-b border-[#e8e4d9] shadow-sm px-8 py-4 flex items-center justify-between">
        <span className="text-[#0d9488] font-bold text-xl tracking-tight" style={{ fontFamily: "'DM Serif Display', serif" }}>
          UniBridge
        </span>
        <div className="flex gap-6 text-sm text-[#4a4a6a]">
          <Link to="/industry/dashboard" className="hover:text-[#0d9488] transition">Dashboard</Link>
          <Link to="/industry/search"    className="hover:text-[#0d9488] transition">Search</Link>
          <Link to="/industry/bookmarks" className="text-[#0d9488] font-semibold">Bookmarks</Link>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-6 py-10">

        {/* ── Header ── */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1
              className="text-4xl text-[#1a1a2e] mb-2"
              style={{ fontFamily: "'DM Serif Display', serif" }}
            >
              Saved Bookmarks
            </h1>
            <p className="text-[#4a4a6a]">
              {bookmarks.length} saved result{bookmarks.length !== 1 ? "s" : ""}
            </p>
          </div>

          {bookmarks.length > 0 && (
            <button
              onClick={clearAll}
              className="text-sm text-red-600 hover:text-red-700 border border-red-200 hover:border-red-400 hover:bg-red-50 px-4 py-2 rounded-xl transition"
            >
              Clear all bookmarks
            </button>
          )}
        </div>

        {/* ── Empty state ── */}
        {bookmarks.length === 0 && (
          <div className="flex flex-col items-center justify-center py-32 gap-4 text-center">
            <span className="text-5xl">🔖</span>
            <p className="text-[#4a4a6a] text-lg">No bookmarks yet.</p>
            <p className="text-[#8888aa] text-sm">
              Start searching to save results.
            </p>
            <Link
              to="/industry/search"
              className="mt-2 bg-[#0d9488] hover:bg-[#0f766e] text-white font-semibold px-5 py-2.5 rounded-xl transition"
            >
              Go to Search
            </Link>
          </div>
        )}

        {/* ── Bookmarks grid ── */}
        {bookmarks.length > 0 && (
          <div className="grid grid-cols-2 gap-5">
            {bookmarks.map((r, i) => (
              <TechCard
                key={r.id ?? i}
                result={r}
                isBookmarked={true}
                onBookmark={handleRemove}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
