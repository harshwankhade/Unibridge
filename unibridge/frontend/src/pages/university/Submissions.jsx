import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { getToken, logout } from "../../utils/auth";

const SUB_SERVICE = "http://localhost:8000/submission";

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-IN", {
    year: "numeric", month: "short", day: "numeric",
  });
}

function StatusBadge({ status }) {
  const map = {
    pending:  { label: "Under Review", cls: "bg-amber-100 text-amber-800 border-amber-200"   },
    approved: { label: "Approved",     cls: "bg-green-100 text-green-800 border-green-200"   },
    rejected: { label: "Rejected",     cls: "bg-red-100 text-red-800 border-red-200"         },
  };
  const { label, cls } = map[status] ?? { label: status, cls: "bg-[#f7f5ed] text-[#4a4a6a] border-[#e8e4d9]" };
  return (
    <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${cls}`}>
      {label}
    </span>
  );
}

function Pill({ children }) {
  return (
    <span className="text-xs bg-[#f7f5ed] text-[#4a4a6a] border border-[#e8e4d9] px-2.5 py-1 rounded-full">
      {children}
    </span>
  );
}

function SubmissionCard({ submission, onEdit }) {
  const [expanded, setExpanded] = useState(false);
  const preview = submission.abstract?.slice(0, 150);
  const hasMore = submission.abstract?.length > 150;

  return (
    <div className="bg-white border border-[#e8e4d9] shadow-sm rounded-2xl p-6 hover:border-[#0d9488]/40 hover:shadow-md transition-all duration-150">

      {/* ── Top row ── */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <h3 className="text-[#1a1a2e] font-semibold text-base leading-snug flex-1">
          {submission.title}
        </h3>
        <StatusBadge status={submission.status} />
      </div>

      {/* ── Pills row ── */}
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <Pill>{submission.ip_type === "patent" ? "🔬 Patent" : "📄 Research Paper"}</Pill>
        <Pill>{submission.domain}</Pill>
        <span className="text-[#8888aa] text-xs ml-auto">{formatDate(submission.created_at)}</span>
      </div>

      {/* ── University & contributors ── */}
      <p className="text-[#4a4a6a] text-xs mb-3">
        <span className="font-medium text-[#1a1a2e]">{submission.university}</span>
        {submission.contributors && (
          <> &middot; {submission.contributors}</>
        )}
      </p>

      {/* ── Abstract preview ── */}
      <p className="text-[#4a4a6a] text-sm leading-relaxed mb-1">
        {expanded ? submission.abstract : preview}
        {!expanded && hasMore && "…"}
      </p>
      {hasMore && (
        <button
          onClick={() => setExpanded((v) => !v)}
          className="text-[#0d9488] text-xs hover:text-[#0f766e] transition"
        >
          {expanded ? "Show less" : "Show more"}
        </button>
      )}

      {/* ── Rejection note ── */}
      {submission.status === "rejected" && submission.admin_note && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded-xl px-4 py-3">
          <p className="text-red-700 text-xs leading-relaxed">
            <span className="font-semibold">Reviewer note:</span> {submission.admin_note}
          </p>
        </div>
      )}

      {/* ── Approval note ── */}
      {submission.status === "approved" && submission.admin_note && (
        <div className="mt-4 bg-green-50 border border-green-200 rounded-xl px-4 py-3">
          <p className="text-green-700 text-xs leading-relaxed">
            <span className="font-semibold">Reviewer note:</span> {submission.admin_note}
          </p>
        </div>
      )}

      {/* ── Edit button (pending only) ── */}
      {submission.status === "pending" && (
        <div className="mt-4 pt-4 border-t border-[#e8e4d9]">
          <button
            onClick={() => onEdit(submission)}
            className="text-xs border border-[#0d9488] text-[#0d9488] hover:bg-[#ccfbf1] px-4 py-2 rounded-lg transition"
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
    <div className="min-h-screen bg-[#fdfcf7] text-[#1a1a2e]" style={{ fontFamily: "'DM Sans', sans-serif" }}>

      {/* ── Nav ── */}
      <nav className="bg-white border-b border-[#e8e4d9] shadow-sm px-8 py-4 flex items-center justify-between">
        <span className="text-[#0d9488] font-bold text-xl tracking-tight" style={{ fontFamily: "'DM Serif Display', serif" }}>
          UniBridge
        </span>
        <div className="flex items-center gap-6 text-sm text-[#4a4a6a]">
          <Link to="/university/dashboard"   className="hover:text-[#0d9488] transition">Dashboard</Link>
          <Link to="/university/submit"      className="hover:text-[#0d9488] transition">Submit IP</Link>
          <Link to="/university/submissions" className="text-[#0d9488] font-semibold">My Submissions</Link>
          <button onClick={logout} className="text-[#dc2626] hover:bg-red-50 px-2 py-1 rounded-lg transition">Sign out</button>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto px-6 py-12">

        {/* ── Page header ── */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-4xl text-[#1a1a2e] mb-2" style={{ fontFamily: "'DM Serif Display', serif" }}>
              My Submissions
            </h1>
            {!loading && !error && (
              <span className="inline-block bg-[#f7f5ed] text-[#4a4a6a] text-xs font-semibold px-3 py-1 rounded-full border border-[#e8e4d9]">
                {submissions.length} submission{submissions.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>
          <button
            onClick={fetchSubmissions}
            disabled={loading}
            className="flex items-center gap-2 text-sm bg-white hover:bg-[#f7f5ed] border border-[#e8e4d9] text-[#4a4a6a] px-4 py-2.5 rounded-xl transition disabled:opacity-50"
          >
            <span className={loading ? "animate-spin inline-block" : ""}>↻</span>
            Refresh
          </button>
        </div>

        {/* ── Loading spinner ── */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <div className="w-10 h-10 border-2 border-[#0d9488]/30 border-t-[#0d9488] rounded-full animate-spin" />
            <p className="text-[#4a4a6a] text-sm">Loading your submissions…</p>
          </div>
        )}

        {/* ── Error ── */}
        {!loading && error && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-5 py-4 text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* ── Empty state ── */}
        {!loading && !error && submissions.length === 0 && (
          <div className="text-center py-24">
            <p className="text-5xl mb-4">📭</p>
            <p className="text-[#1a1a2e] font-medium mb-2">No submissions yet</p>
            <p className="text-[#8888aa] text-sm mb-6">
              Submit your first IP to get started.
            </p>
            <button
              onClick={() => navigate("/university/submit")}
              className="bg-[#0d9488] hover:bg-[#0f766e] text-white font-semibold px-6 py-3 rounded-xl transition text-sm"
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
