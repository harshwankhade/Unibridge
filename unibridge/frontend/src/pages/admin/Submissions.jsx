import { useEffect, useState } from "react";
import axios from "axios";
import AdminNav from "../../components/AdminNav";
import { getToken } from "../../utils/auth";

const ADMIN = "http://localhost:8006";
const hdrs  = () => ({ Authorization: `Bearer ${getToken()}` });

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-IN", { year: "numeric", month: "short", day: "numeric" });
}

function StatusBadge({ status }) {
  const map = {
    pending:  "bg-amber-500/20 text-amber-300 border-amber-500/40",
    approved: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
    rejected: "bg-red-500/20 text-red-300 border-red-500/40",
  };
  const labels = { pending: "Pending", approved: "Approved", rejected: "Rejected" };
  return (
    <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${map[status] ?? "bg-slate-700 text-slate-300 border-slate-600"}`}>
      {labels[status] ?? status}
    </span>
  );
}

function Pill({ children }) {
  return (
    <span className="text-xs bg-slate-700/70 text-slate-300 border border-slate-600/50 px-2.5 py-1 rounded-full">
      {children}
    </span>
  );
}

const FILTERS = ["all", "pending", "approved", "rejected"];

function SubmissionCard({ sub, onStatusChange }) {
  const [expanded,   setExpanded]   = useState(false);
  const [note,       setNote]       = useState("");
  const [busy,       setBusy]       = useState(false);
  const [cardError,  setCardError]  = useState("");

  const preview = sub.abstract?.slice(0, 200) ?? "";
  const hasMore = (sub.abstract?.length ?? 0) > 200;

  async function doAction(action) {
    setBusy(true); setCardError("");
    try {
      await axios.post(
        `${ADMIN}/submissions/${sub.id}/${action}`,
        { admin_note: note },
        { headers: hdrs() }
      );
      onStatusChange(sub.id, action === "approve" ? "approved" : "rejected", note);
    } catch (err) {
      setCardError(err.response?.data?.detail ?? `${action} failed`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6 hover:border-slate-600/80 transition-all">

      {/* Top row */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <h3 className="text-white font-semibold text-base leading-snug flex-1">{sub.title}</h3>
        <StatusBadge status={sub.status} />
      </div>

      {/* Pills */}
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <Pill>{sub.ip_type === "patent" ? "🔬 Patent" : "📄 Paper"}</Pill>
        <Pill>{sub.domain}</Pill>
        <span className="text-slate-500 text-xs">{sub.submitted_by_email}</span>
        <span className="text-slate-500 text-xs ml-auto">{formatDate(sub.created_at)}</span>
      </div>

      {/* University & contributors */}
      <p className="text-slate-400 text-xs mb-3">
        <span className="font-medium text-slate-300">{sub.university}</span>
        {sub.contributors && <> &middot; {sub.contributors}</>}
      </p>

      {/* Abstract */}
      <p className="text-slate-400 text-sm leading-relaxed mb-1">
        {expanded ? sub.abstract : preview}
        {!expanded && hasMore && "…"}
      </p>
      {hasMore && (
        <button onClick={() => setExpanded(v => !v)} className="text-cyan-500 text-xs hover:text-cyan-400 transition">
          {expanded ? "Show less" : "Show more"}
        </button>
      )}

      {/* Admin note (already set) */}
      {sub.admin_note && (
        <div className="mt-4 bg-slate-700/40 border border-slate-600/40 rounded-xl px-4 py-3">
          <p className="text-slate-300 text-xs">
            <span className="font-semibold text-slate-200">Note:</span> {sub.admin_note}
          </p>
        </div>
      )}

      {/* Action row — pending only */}
      {sub.status === "pending" && (
        <div className="mt-5 pt-4 border-t border-slate-700/50">
          <input
            type="text"
            value={note}
            onChange={e => setNote(e.target.value)}
            placeholder="Add a note (optional)"
            className="w-full bg-slate-700/60 border border-slate-600 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 mb-3 transition"
          />
          <div className="flex items-center gap-3">
            <button
              onClick={() => doAction("approve")}
              disabled={busy}
              className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-semibold px-5 py-2 rounded-xl transition"
            >
              {busy ? "…" : "✓ Approve"}
            </button>
            <button
              onClick={() => doAction("reject")}
              disabled={busy}
              className="border border-red-600/60 hover:bg-red-900/30 disabled:opacity-50 text-red-400 text-sm font-medium px-5 py-2 rounded-xl transition"
            >
              {busy ? "…" : "✕ Reject"}
            </button>
          </div>
          {cardError && <p className="text-red-400 text-xs mt-2">{cardError}</p>}
        </div>
      )}
    </div>
  );
}

export default function AdminSubmissions() {
  const [submissions, setSubmissions] = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState("");
  const [filter,      setFilter]      = useState("all");

  async function fetchSubmissions() {
    setLoading(true); setError("");
    try {
      const { data } = await axios.get(`${ADMIN}/submissions`, { headers: hdrs() });
      setSubmissions(data.submissions ?? []);
    } catch {
      setError("Failed to load submissions.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchSubmissions(); }, []);

  function handleStatusChange(id, newStatus, adminNote) {
    setSubmissions(prev =>
      prev.map(s => s.id === id ? { ...s, status: newStatus, admin_note: adminNote } : s)
    );
  }

  const pending  = submissions.filter(s => s.status === "pending").length;
  const filtered = filter === "all" ? submissions : submissions.filter(s => s.status === filter);

  return (
    <div className="min-h-screen bg-slate-900 text-white" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <AdminNav pendingCount={pending} />

      <main className="max-w-4xl mx-auto px-6 py-10">

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <h1 className="text-4xl text-white" style={{ fontFamily: "'DM Serif Display', serif" }}>
              Submission Queue
            </h1>
            {pending > 0 && (
              <span className="bg-amber-500 text-slate-900 text-xs font-bold px-2.5 py-1 rounded-full">
                {pending} pending
              </span>
            )}
          </div>
          <button
            onClick={fetchSubmissions}
            disabled={loading}
            className="flex items-center gap-2 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 px-4 py-2.5 rounded-xl transition disabled:opacity-50"
          >
            <span className={loading ? "animate-spin inline-block" : ""}>↻</span> Refresh
          </button>
        </div>

        {/* Filter tabs */}
        <div className="flex gap-2 mb-6">
          {FILTERS.map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-xl text-sm font-medium capitalize transition ${
                filter === f
                  ? "bg-cyan-500/20 border border-cyan-500/50 text-cyan-300"
                  : "bg-slate-800 border border-slate-700 text-slate-400 hover:border-slate-500"
              }`}
            >
              {f}
              {f !== "all" && (
                <span className="ml-1.5 text-xs opacity-60">
                  ({submissions.filter(s => s.status === f).length})
                </span>
              )}
            </button>
          ))}
        </div>

        {/* States */}
        {loading && (
          <div className="flex justify-center py-24">
            <div className="w-10 h-10 border-2 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" />
          </div>
        )}
        {!loading && error && (
          <div className="bg-red-900/30 border border-red-700/60 rounded-xl px-5 py-4 text-red-300 text-sm">{error}</div>
        )}
        {!loading && !error && filtered.length === 0 && (
          <p className="text-slate-500 text-center py-20">No submissions in this category.</p>
        )}

        {/* Cards */}
        {!loading && !error && filtered.length > 0 && (
          <div className="space-y-5">
            {filtered.map(sub => (
              <SubmissionCard key={sub.id} sub={sub} onStatusChange={handleStatusChange} />
            ))}
          </div>
        )}

      </main>
    </div>
  );
}
