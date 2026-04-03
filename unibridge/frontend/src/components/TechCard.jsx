import { useState } from "react";

// ─── TRL colour helper ───────────────────────────────────────────────────────
function trlColor(trl) {
  if (trl <= 3) return "bg-red-500/20 text-red-300 border-red-500/40";
  if (trl <= 6) return "bg-yellow-500/20 text-yellow-300 border-yellow-500/40";
  return "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
}

function sourceBadgeColor(source) {
  return source === "patent"
    ? "bg-violet-500/20 text-violet-300 border-violet-500/40"
    : "bg-sky-500/20 text-sky-300 border-sky-500/40";
}

// ─── Component ───────────────────────────────────────────────────────────────
export default function TechCard({ result, onBookmark, isBookmarked }) {
  const [expanded, setExpanded] = useState(false);

  const {
    title = "",
    abstract = "",
    university = "",
    source = "paper",
    domain = "",
    explanation = "",
    contributors = [],
    date = "",
    trl,
    trl_reasoning = "",
    is_indian = false,
  } = result;

  const year = date ? String(date).slice(0, 4) : "—";
  const displayContributors =
    contributors.length > 2
      ? contributors.slice(0, 2).join(", ") + ` +${contributors.length - 2} more`
      : contributors.join(", ");

  return (
    <div className="flex flex-col bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5 gap-3 hover:border-cyan-500/40 transition-all duration-200 shadow-lg hover:shadow-cyan-900/20">

      {/* ── Header row ── */}
      <div className="flex items-center justify-between gap-2">
        {/* Source badge */}
        <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full border capitalize ${sourceBadgeColor(source)}`}>
          {source}
        </span>

        {/* TRL badge with tooltip */}
        <div className="relative group cursor-default">
          <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full border ${trlColor(trl)}`}>
            TRL {trl ?? "?"}
          </span>
          {trl_reasoning && (
            <div className="absolute right-0 top-6 z-20 hidden group-hover:block w-72 bg-slate-900 border border-slate-600 rounded-xl p-3 text-xs text-slate-300 shadow-2xl leading-relaxed">
              {trl_reasoning}
            </div>
          )}
        </div>
      </div>

      {/* ── Title ── */}
      <h3
        className="font-semibold text-white text-sm leading-snug line-clamp-2"
        style={{ fontFamily: "'DM Sans', sans-serif" }}
      >
        {title}
      </h3>

      {/* ── University ── */}
      <p className="text-slate-400 text-xs">
        {university}
        {is_indian && <span className="ml-1">🇮🇳</span>}
      </p>

      {/* ── Domain tag ── */}
      {domain && (
        <span className="self-start text-[11px] bg-slate-700/60 text-slate-300 border border-slate-600/60 px-2.5 py-0.5 rounded-full">
          {domain}
        </span>
      )}

      {/* ── Explanation ── */}
      {explanation && (
        <p className="text-slate-400 italic text-xs leading-relaxed line-clamp-2">
          {explanation}
        </p>
      )}

      {/* ── Contributors ── */}
      {displayContributors && (
        <p className="text-slate-500 text-[11px] truncate">
          👤 {displayContributors}
        </p>
      )}

      {/* ── Bottom row ── */}
      <div className="flex items-center justify-between mt-auto pt-2 border-t border-slate-700/50">
        <span className="text-slate-500 text-xs">{year}</span>
        <button
          onClick={() => onBookmark(result)}
          aria-label={isBookmarked ? "Remove bookmark" : "Add bookmark"}
          className="text-lg hover:scale-110 transition-transform"
        >
          {isBookmarked ? "🔖" : "🏷️"}
        </button>
      </div>

      {/* ── Expandable abstract ── */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="text-cyan-400 hover:text-cyan-300 text-xs text-left transition-colors"
      >
        {expanded ? "Hide abstract ▲" : "Show abstract ▼"}
      </button>
      {expanded && (
        <p className="text-slate-400 text-xs leading-relaxed border-t border-slate-700/40 pt-3">
          {abstract || "No abstract available."}
        </p>
      )}
    </div>
  );
}
