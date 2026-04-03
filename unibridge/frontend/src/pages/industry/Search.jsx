import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import TechCard from "../../components/TechCard";

const BOOKMARKS_KEY  = "unibridge_bookmarks";
const SEARCH_SERVICE = "http://localhost:8002";

const CATEGORIES = [
  {
    id:    "solve",
    label: "Solve a Problem",
    desc:  "Find research that addresses your technical challenge",
    placeholder: "e.g. We're struggling with heat dissipation in power electronics",
  },
  {
    id:    "benchmark",
    label: "Benchmark Technologies",
    desc:  "Compare approaches and technologies in your domain",
    placeholder: "e.g. Compare solid-state vs lithium-ion battery technologies",
  },
  {
    id:    "landscape",
    label: "Landscape a Field",
    desc:  "Explore the full research landscape of a field",
    placeholder: "e.g. Overview of CRISPR gene editing research",
  },
];

function loadBookmarks() {
  try { return JSON.parse(localStorage.getItem(BOOKMARKS_KEY)) || []; }
  catch { return []; }
}

function saveBookmarks(bm) {
  localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bm));
}

export default function Search() {
  const [query,           setQuery]           = useState("");
  const [category,        setCategory]        = useState("solve");
  const [results,         setResults]         = useState([]);
  const [loading,         setLoading]         = useState(false);
  const [error,           setError]           = useState("");
  const [translatedQuery, setTranslatedQuery] = useState("");
  const [bookmarks,       setBookmarks]       = useState(loadBookmarks);
  const [indianOnly,      setIndianOnly]      = useState(false);
  const [showTranslated,  setShowTranslated]  = useState(false);

  const activeCat = CATEGORIES.find((c) => c.id === category);

  // ── Bookmark toggle ──────────────────────────────────────────────────────
  const handleBookmark = (result) => {
    setBookmarks((prev) => {
      const exists = prev.some((b) => b.id === result.id);
      const next   = exists ? prev.filter((b) => b.id !== result.id) : [...prev, result];
      saveBookmarks(next);
      return next;
    });
  };

  const isBookmarked = (result) => bookmarks.some((b) => b.id === result.id);

  // ── Search ───────────────────────────────────────────────────────────────
  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setTranslatedQuery("");
    setResults([]);

    try {
      const { data } = await axios.post(`${SEARCH_SERVICE}/search`, {
        query,
        category,
        n_results: 10,
      });
      setResults(data.results || []);
      setTranslatedQuery(data.translated_query || "");
      setShowTranslated(true);
    } catch {
      setError("Search failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => { if (e.key === "Enter") handleSearch(); };

  // ── Filtered results ─────────────────────────────────────────────────────
  const displayResults = indianOnly
    ? results.filter((r) => r.is_indian === true || r.is_indian === "true")
    : results;

  return (
    <div
      className="min-h-screen bg-slate-900 text-white"
      style={{ fontFamily: "'DM Sans', sans-serif" }}
    >
      {/* ── Nav ── */}
      <nav className="border-b border-slate-800 px-8 py-4 flex items-center justify-between">
        <span className="text-cyan-400 font-bold text-xl tracking-tight" style={{ fontFamily: "'DM Serif Display', serif" }}>
          UniBridge
        </span>
        <div className="flex gap-6 text-sm text-slate-400">
          <Link to="/industry/dashboard" className="hover:text-white transition">Dashboard</Link>
          <Link to="/industry/search"    className="text-white font-medium">Search</Link>
          <Link to="/industry/bookmarks" className="hover:text-white transition">Bookmarks</Link>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-6 py-10">

        {/* ── Page header ── */}
        <div className="mb-8">
          <h1
            className="text-4xl text-white mb-2"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            Technology Search
          </h1>
          <p className="text-slate-400">
            Discover university IP and research across 1,000+ institutions
          </p>
        </div>

        {/* ── Category selector ── */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setCategory(cat.id)}
              className={`text-left rounded-2xl px-5 py-4 border transition-all duration-150
                ${category === cat.id
                  ? "bg-cyan-500/20 border-cyan-500/60 shadow-lg shadow-cyan-900/30"
                  : "bg-slate-800/50 border-slate-700/50 hover:border-slate-500"
                }`}
            >
              <p className={`font-semibold text-sm mb-1 ${category === cat.id ? "text-cyan-300" : "text-white"}`}>
                {cat.label}
              </p>
              <p className="text-slate-400 text-xs leading-relaxed">{cat.desc}</p>
            </button>
          ))}
        </div>

        {/* ── Search input ── */}
        <div className="flex gap-3 mb-4">
          <input
            id="search-input"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={activeCat?.placeholder}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-5 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/40 transition"
          />
          <button
            id="search-button"
            onClick={handleSearch}
            disabled={loading}
            className="bg-cyan-500 hover:bg-cyan-400 disabled:bg-slate-600 text-slate-900 font-semibold px-6 py-3 rounded-xl transition"
          >
            {loading ? "Searching…" : "Search"}
          </button>
        </div>

        {/* ── Translated query box ── */}
        {translatedQuery && showTranslated && (
          <div className="mb-6 bg-slate-800/50 border border-slate-700/60 rounded-xl px-5 py-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-slate-500 text-xs uppercase tracking-widest">Translated query</span>
              <button
                onClick={() => setShowTranslated(false)}
                className="text-slate-600 hover:text-slate-400 text-xs"
              >
                ✕ hide
              </button>
            </div>
            <p className="text-slate-300 text-sm leading-relaxed">{translatedQuery}</p>
          </div>
        )}

        {/* ── Filter row ── */}
        {results.length > 0 && (
          <div className="flex items-center gap-3 mb-6">
            <button
              onClick={() => setIndianOnly((v) => !v)}
              className={`flex items-center gap-2 text-sm px-4 py-2 rounded-xl border transition
                ${indianOnly
                  ? "bg-orange-500/20 border-orange-400/50 text-orange-300"
                  : "bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-500"
                }`}
            >
              🇮🇳 Indian universities only
            </button>
            <span className="text-slate-500 text-xs">
              {displayResults.length} of {results.length} result{results.length !== 1 ? "s" : ""}
            </span>
          </div>
        )}

        {/* ── States ── */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <div className="w-10 h-10 border-2 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" />
            <p className="text-slate-400 text-sm">Translating query and searching…</p>
          </div>
        )}

        {error && (
          <div className="bg-red-900/30 border border-red-700/60 rounded-xl px-5 py-4 text-red-300 text-sm mb-6">
            {error}
          </div>
        )}

        {!loading && !error && results.length === 0 && query && (
          <div className="text-center py-24 text-slate-500">
            No results found. Try rephrasing your query.
          </div>
        )}

        {/* ── Results grid ── */}
        {!loading && displayResults.length > 0 && (
          <div className="grid grid-cols-2 gap-5">
            {displayResults.map((r, i) => (
              <TechCard
                key={r.id ?? i}
                result={r}
                isBookmarked={isBookmarked(r)}
                onBookmark={handleBookmark}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
