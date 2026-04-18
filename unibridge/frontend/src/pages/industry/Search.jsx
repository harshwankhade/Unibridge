import { useState } from "react";
import { Link } from "react-router-dom";
import client from "../../api/client";
import { getToken, logout } from "../../utils/auth";
import TechCard from "../../components/TechCard";

const BOOKMARKS_KEY  = "unibridge_bookmarks";

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
      const { data } = await client.post('/search', {
        query,
        category,
        n_results: 10,
      }, {
        headers: { Authorization: `Bearer ${getToken()}` }
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
          <Link to="/industry/search"    className="text-[#0d9488] font-semibold">Search</Link>
          <Link to="/industry/bookmarks" className="hover:text-[#0d9488] transition">Bookmarks</Link>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-6 py-10">

        {/* ── Page header ── */}
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h1
              className="text-4xl text-[#1a1a2e] mb-2"
              style={{ fontFamily: "'DM Serif Display', serif" }}
            >
              Technology Search
            </h1>
            <p className="text-[#4a4a6a]">
              Discover university IP and research across 1,000+ institutions
            </p>
          </div>
          <button
            id="sign-out-button"
            onClick={logout}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "rgba(220,38,38,0.08)";
              e.currentTarget.style.borderColor = "rgba(220,38,38,0.6)";
              e.currentTarget.style.color = "#dc2626";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "transparent";
              e.currentTarget.style.borderColor = "#e8e4d9";
              e.currentTarget.style.color = "#4a4a6a";
            }}
            style={{
              background: "transparent",
              border: "1px solid #e8e4d9",
              color: "#4a4a6a",
              fontSize: "0.8rem",
              fontWeight: 500,
              padding: "6px 16px",
              borderRadius: "10px",
              cursor: "pointer",
              transition: "background-color 0.15s, border-color 0.15s, color 0.15s",
              marginTop: "6px",
              flexShrink: 0,
            }}
          >
            Sign Out
          </button>
        </div>

        {/* ── Category selector ── */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setCategory(cat.id)}
              className={`text-left rounded-2xl px-5 py-4 border transition-all duration-150
                ${category === cat.id
                  ? "bg-[#ccfbf1] border-[#0d9488]/50 shadow-sm"
                  : "bg-white border-[#e8e4d9] hover:border-[#0d9488]/40"
                }`}
            >
              <p className={`font-semibold text-sm mb-1 ${category === cat.id ? "text-[#0d9488]" : "text-[#1a1a2e]"}`}>
                {cat.label}
              </p>
              <p className="text-[#4a4a6a] text-xs leading-relaxed">{cat.desc}</p>
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
            className="flex-1 bg-white border border-[#e8e4d9] rounded-xl px-5 py-3 text-sm text-[#1a1a2e] placeholder-[#8888aa] focus:outline-none focus:border-[#0d9488] focus:ring-1 focus:ring-[#0d9488] transition"
          />
          <button
            id="search-button"
            onClick={handleSearch}
            disabled={loading}
            className="bg-[#0d9488] hover:bg-[#0f766e] disabled:bg-[#8888aa] text-white font-semibold px-6 py-3 rounded-xl transition"
          >
            {loading ? "Searching…" : "Search"}
          </button>
        </div>

        {/* ── Translated query box ── */}
        {translatedQuery && showTranslated && (
          <div className="mb-6 bg-white border border-[#e8e4d9] rounded-xl px-5 py-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[#8888aa] text-xs uppercase tracking-widest">Translated query</span>
              <button
                onClick={() => setShowTranslated(false)}
                className="text-[#8888aa] hover:text-[#4a4a6a] text-xs"
              >
                ✕ hide
              </button>
            </div>
            <p className="text-[#4a4a6a] text-sm leading-relaxed">{translatedQuery}</p>
          </div>
        )}

        {/* ── Filter row ── */}
        {results.length > 0 && (
          <div className="flex items-center gap-3 mb-6">
            <button
              onClick={() => setIndianOnly((v) => !v)}
              className={`flex items-center gap-2 text-sm px-4 py-2 rounded-xl border transition
                ${indianOnly
                  ? "bg-orange-50 border-orange-300 text-orange-700"
                  : "bg-white border-[#e8e4d9] text-[#4a4a6a] hover:border-[#0d9488]/40"
                }`}
            >
              🇮🇳 Indian universities only
            </button>
            <span className="text-[#8888aa] text-xs">
              {displayResults.length} of {results.length} result{results.length !== 1 ? "s" : ""}
            </span>
          </div>
        )}

        {/* ── States ── */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <div className="w-10 h-10 border-2 border-[#0d9488]/30 border-t-[#0d9488] rounded-full animate-spin" />
            <p className="text-[#4a4a6a] text-sm">Translating query and searching…</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-5 py-4 text-red-700 text-sm mb-6">
            {error}
          </div>
        )}

        {!loading && !error && results.length === 0 && query && (
          <div className="text-center py-24 text-[#8888aa]">
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
