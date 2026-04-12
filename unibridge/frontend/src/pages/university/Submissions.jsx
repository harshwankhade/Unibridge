import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { getToken, logout } from "../../utils/auth";

const SUB_SERVICE = "http://localhost:8004";

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-IN", {
    year: "numeric", month: "short", day: "numeric",
  });
}

function StatusBadge({ status }) {
  const map = {
    pending:  { label: "Under Review", cls: "bg-amber-500/20 text-amber-300 border-amber-500/40"  },
    approved: { label: "Approved",     cls: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40" },
    rejected: { label: "Rejected",     cls: "bg-red-500/20 text-red-300 border-red-500/40"        },
  };
  const { label, cls } = map[status] ?? { label: status, cls: "bg-slate-700 text-slate-300 border-slate-600" };
  return (
    <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${cls}`}>
      {label}
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

function SubmissionCard({ submission, onEdit }) {
  const [expanded, setExpanded] = useState(false);
  const preview = submission.abstract?.slice(0, 150);
  const hasMore = submission.abstract?.length > 150;

  return (
    <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6 hover:border-slate-600/80 transition-all duration-150">

      {/* ── Top row ── */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <h3 className="text-white font-semibold text-base leading-snug flex-1">
          {submission.title}
        </h3>
        <StatusBadge status={submission.status} />
      </div>

      {/* ── Pills row ── */}
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <Pill>{submission.ip_type === "patent" ? "🔬 Patent" : "📄 Research Paper"}</Pill>
        <Pill>{submission.domain}</Pill>
        <span className="text-slate-500 text-xs ml-auto">{formatDate(submission.created_at)}</span>
      </div>

      {/* ── University & contributors ── */}
      <p className="text-slate-400 text-xs mb-3">
        <span className="font-medium text-slate-300">{submission.university}</span>
        {submission.contributors && (
          <> &middot; {submission.contributors}</>
        )}
      </p>

      {/* ── Abstract preview ── */}
      <p className="text-slate-400 text-sm leading-relaxed mb-1">
        {expanded ? submission.abstract : preview}
        {!expanded && hasMore && "…"}
      </p>
      {hasMore && (
        <button
          onClick={() => setExpanded((v) => !v)}
          className="text-cyan-500 text-xs hover:text-cyan-400 transition"
        >
          {expanded ? "Show less" : "Show more"}
        </button>
      )}

      {/* ── Rejection note ── */}
      {submission.status === "rejected" && submission.admin_note && (
        <div className="mt-4 bg-red-950/50 border border-red-800/50 rounded-xl px-4 py-3">
          <p className="text-red-300 text-xs leading-relaxed">
            <span className="font-semibold">Reviewer note:</span> {submission.admin_note}
          </p>
        </div>
      )}

      {/* ── Approval note ── */}
      {submission.status === "approved" && submission.admin_note && (
        <div className="mt-4 bg-emerald-950/40 border border-emerald-800/40 rounded-xl px-4 py-3">
          <p className="text-emerald-300 text-xs leading-relaxed">
            <span className="font-semibold">Reviewer note:</span> {submission.admin_note}
          </p>
        </div>
      )}

      {/* ── Edit button (pending only) ── */}
      {submission.status === "pending" && (
        <div className="mt-4 pt-4 border-t border-slate-700/50">
          <button
            onClick={() => onEdit(submission)}
            className="text-xs bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg transition"
          >
            ✏️ Edit
          </button>
        </div>
      )}

    </div>
  );
}

export default function Submissions() {
  const navigate = useNavigate();

  const [submissions, setSubmissions] = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState("");

  async function fetchSubmissions() {
    setLoading(true);
    setError("");
    try {
      const { data } = await axios.get(`${SUB_SERVICE}/submissions`, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setSubmissions(data.submissions || []);
    } catch {
      setError("Failed to load submissions. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchSubmissions(); }, []);

  function handleEdit(submission) {
    navigate("/university/submit", { state: { submission } });
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white" style={{ fontFamily: "'DM Sans', sans-serif" }}>

      {/* ── Nav ── */}
      <nav className="border-b border-slate-800 px-8 py-4 flex items-center justify-between">
        <span className="text-cyan-400 font-bold text-xl tracking-tight" style={{ fontFamily: "'DM Serif Display', serif" }}>
          UniBridge
        </span>
        <div className="flex items-center gap-6 text-sm text-slate-400">
          <Link to="/university/dashboard"   className="hover:text-white transition">Dashboard</Link>
          <Link to="/university/submit"      className="hover:text-white transition">Submit IP</Link>
          <Link to="/university/submissions" className="text-white font-medium">My Submissions</Link>
          <button onClick={logout} className="hover:text-red-400 transition">Sign out</button>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto px-6 py-12">

        {/* ── Page header ── */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-4xl text-white mb-2" style={{ fontFamily: "'DM Serif Display', serif" }}>
              My Submissions
            </h1>
            {!loading && !error && (
              <span className="inline-block bg-slate-700/70 text-slate-300 text-xs font-semibold px-3 py-1 rounded-full border border-slate-600/50">
                {submissions.length} submission{submissions.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>
          <button
            onClick={fetchSubmissions}
            disabled={loading}
            className="flex items-center gap-2 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 px-4 py-2.5 rounded-xl transition disabled:opacity-50"
          >
            <span className={loading ? "animate-spin inline-block" : ""}>↻</span>
            Refresh
          </button>
        </div>

        {/* ── Loading spinner ── */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <div className="w-10 h-10 border-2 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" />
            <p className="text-slate-400 text-sm">Loading your submissions…</p>
          </div>
        )}

        {/* ── Error ── */}
        {!loading && error && (
          <div className="bg-red-900/30 border border-red-700/60 rounded-xl px-5 py-4 text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* ── Empty state ── */}
        {!loading && !error && submissions.length === 0 && (
          <div className="text-center py-24">
            <p className="text-5xl mb-4">📭</p>
            <p className="text-slate-300 font-medium mb-2">No submissions yet</p>
            <p className="text-slate-500 text-sm mb-6">
              Submit your first IP to get started.
            </p>
            <button
              onClick={() => navigate("/university/submit")}
              className="bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold px-6 py-3 rounded-xl transition text-sm"
            >
              📤 Submit New IP
            </button>
          </div>
        )}

        {/* ── Submission cards ── */}
        {!loading && !error && submissions.length > 0 && (
          <div className="space-y-5">
            {submissions.map((sub) => (
              <SubmissionCard key={sub.id} submission={sub} onEdit={handleEdit} />
            ))}
          </div>
        )}

      </main>
    </div>
  );
}
