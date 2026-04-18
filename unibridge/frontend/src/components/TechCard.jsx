import { useState } from "react";

// ─── TRL colour helper ───────────────────────────────────────────────────────
function trlColor(trl) {
  if (trl <= 3) return "bg-red-100 text-red-700 border-red-200";
  if (trl <= 6) return "bg-amber-100 text-amber-700 border-amber-200";
  return "bg-green-100 text-green-700 border-green-200";
}

function sourceBadgeColor(source) {
  return source === "patent"
    ? "bg-violet-100 text-violet-700 border-violet-200"
    : "bg-sky-100 text-sky-700 border-sky-200";
}

// ─── Component ───────────────────────────────────────────────────────────────
export default function TechCard({ result, onBookmark, isBookmarked }) {
  const [expanded, setExpanded] = useState(false);
  const [showFullExplanation, setShowFullExplanation] = useState(false);

  const {
    title        = "",
    abstract     = "",
    university   = "",
    source       = "paper",
    domain       = "",
    explanation  = "",
    contributors = [],
    date         = "",
    trl,
    trl_reasoning = "",
    is_indian     = false,
  } = result;

  const year = date ? String(date).slice(0, 4) : "—";
  const displayContributors =
    contributors.length > 2
      ? contributors.slice(0, 2).join(", ") + ` +${contributors.length - 2} more`
      : contributors.join(", ");

  return (
    <div className="flex flex-col bg-white border border-[#e8e4d9] rounded-2xl p-5 gap-3 hover:border-[#0d9488]/50 hover:shadow-md transition-all duration-200 shadow-sm">

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
            <div className="absolute right-0 top-6 z-20 hidden group-hover:block w-72 bg-white border border-[#e8e4d9] rounded-xl p-3 text-xs text-[#4a4a6a] shadow-xl leading-relaxed">
              {trl_reasoning}
            </div>
          )}
        </div>
      </div>

      {/* ── Title ── */}
      <h3
        className="font-semibold text-[#1a1a2e] text-sm leading-snug line-clamp-2"
        style={{ fontFamily: "'DM Sans', sans-serif" }}
      >
        {title}
      </h3>

      {/* ── University ── */}
      <p className="text-[#4a4a6a] text-xs">
        {university}
        {is_indian && <span className="ml-1">🇮🇳</span>}
      </p>

      {/* ── Domain tag ── */}
      {domain && (
        <span className="self-start text-[11px] bg-[#f7f5ed] text-[#4a4a6a] border border-[#e8e4d9] px-2.5 py-0.5 rounded-full">
          {domain}
        </span>
      )}

      {/* ── Explanation ── */}
      {explanation && (
        <div>
          <p className="text-[#4a4a6a] italic text-xs leading-relaxed">
            {showFullExplanation || explanation.length <= 120
              ? explanation
              : explanation.slice(0, 120) + "..."}
          </p>
          {explanation.length > 120 && (
            <span
              onClick={() => setShowFullExplanation((v) => !v)}
              className="text-[#0d9488] text-sm cursor-pointer"
              style={{ textDecoration: "none" }}
            >
              {showFullExplanation ? "Show less" : "Show more"}
            </span>
          )}
        </div>
      )}

      {/* ── Contributors ── */}
      {displayContributors && (
        <p className="text-[#8888aa] text-[11px] truncate">
          👤 {displayContributors}
        </p>
      )}

      {/* ── Bottom row ── */}
      <div className="flex items-center justify-between mt-auto pt-2 border-t border-[#e8e4d9]">
        <span className="text-[#8888aa] text-xs">{year}</span>
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
        className="text-[#0d9488] hover:text-[#0f766e] text-xs text-left transition-colors"
      >
        {expanded ? "Hide abstract ▲" : "Show abstract ▼"}
      </button>
      {expanded && (
        <p className="text-[#4a4a6a] text-xs leading-relaxed border-t border-[#e8e4d9] pt-3">
          {abstract || "No abstract available."}
        </p>
      )}
    </div>
  );
}
