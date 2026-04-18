import { useState, useEffect } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import axios from "axios";
import { getUser, getToken, logout } from "../../utils/auth";

const SUB_SERVICE = "http://localhost:8000/submission";

const DOMAINS = [
  "Computing & AI",
  "Life Sciences",
  "Chemistry & Materials",
  "Physics & Computing",
  "Engineering",
  "Mathematics",
  "Environmental Science",
  "Economics & Business",
  "Electronics & Electrical",
  "Mechanical Engineering",
  "Other",
];

export default function SubmitIP() {
  const navigate = useNavigate();
  const location = useLocation();
  const prefill = location.state?.submission;
  const isEdit = Boolean(prefill);
  const user = getUser();

  // ── Form state ───────────────────────────────────────────────────────────
  const [title, setTitle] = useState(prefill?.title ?? "");
  const [abstract, setAbstract] = useState(prefill?.abstract ?? "");
  const [university, setUniversity] = useState(prefill?.university ?? user?.university ?? "");
  const [contributors, setContributors] = useState(prefill?.contributors ?? "");
  const [domain, setDomain] = useState(prefill?.domain ?? "");
  const [ip_type, setIpType] = useState(prefill?.ip_type ?? "paper");
  const [legal_status, setLegalStatus] = useState(prefill?.legal_status ?? "PENDING");
  const [doi, setDoi] = useState(prefill?.doi || "");
  const [patentNumber, setPatentNumber] = useState(prefill?.patent_number || "");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  // ── Validation ───────────────────────────────────────────────────────────
  function validate() {
    if (!title.trim()) return "Title must not be empty.";
    if (abstract.trim().length < 100) return "Abstract must be at least 100 characters.";
    if (!university.trim()) return "University / Institution must not be empty.";
    if (!contributors.trim()) return "Contributors must not be empty.";
    if (!domain) return "Please select a domain.";
    return null;
  }

  // ── Submit ───────────────────────────────────────────────────────────────
  async function handleSubmit(e) {
    e.preventDefault();
    const validationError = validate();
    if (validationError) { setError(validationError); return; }

    setError("");
    setLoading(true);

    try {
      await axios.post(
        `${SUB_SERVICE}/submit`,
        {
          title,
          abstract,
          university,
          contributors,
          domain,
          ip_type,
          legal_status: ip_type === "patent" ? legal_status : "PENDING",
          doi,
          patent_number: patentNumber,
        },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );

      setSuccess(true);
      setTitle(""); setAbstract(""); setContributors("");
      setDomain(""); setIpType("paper"); setLegalStatus("PENDING");
      setDoi(""); setPatentNumber("");
    } catch (err) {
      setError(err.response?.data?.detail ?? "Submission failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  // ── Input class helper ───────────────────────────────────────────────────
  const inputCls =
    "w-full bg-white border border-[#e8e4d9] rounded-xl px-4 py-3 text-sm text-[#1a1a2e] " +
    "placeholder-[#8888aa] focus:outline-none focus:border-[#0d9488] focus:ring-1 focus:ring-[#0d9488] transition";

  return (
    <div className="min-h-screen bg-[#fdfcf7] text-[#1a1a2e]" style={{ fontFamily: "'DM Sans', sans-serif" }}>

      {/* ── Nav ── */}
      <nav className="bg-white border-b border-[#e8e4d9] shadow-sm px-8 py-4 flex items-center justify-between">
        <span className="text-[#0d9488] font-bold text-xl tracking-tight" style={{ fontFamily: "'DM Serif Display', serif" }}>
          UniBridge
        </span>
        <div className="flex items-center gap-6 text-sm text-[#4a4a6a]">
          <Link to="/university/dashboard" className="hover:text-[#0d9488] transition">Dashboard</Link>
          <Link to="/university/submit" className="text-[#0d9488] font-semibold">Submit IP</Link>
          <Link to="/university/submissions" className="hover:text-[#0d9488] transition">My Submissions</Link>
          <button onClick={logout} className="text-[#dc2626] hover:bg-red-50 px-2 py-1 rounded-lg transition">Sign out</button>
        </div>
      </nav>

      <main className="max-w-2xl mx-auto px-6 py-12">

        {/* ── Page header ── */}
        <div className="mb-10">
          <h1 className="text-4xl text-[#1a1a2e] mb-2" style={{ fontFamily: "'DM Serif Display', serif" }}>
            {isEdit ? "Edit Submission" : "Submit Intellectual Property"}
          </h1>
          <p className="text-[#4a4a6a] text-sm">
            {isEdit
              ? "Update the fields below and submit a revised version."
              : "Share your university's research and patents with industry partners."
            }
          </p>
        </div>

        {/* ── Success banner ── */}
        {success && (
          <div className="mb-8 bg-green-50 border border-green-200 rounded-2xl p-6">
            <p className="text-green-800 font-semibold mb-1">
              ✅ Submission received!
            </p>
            <p className="text-green-700 text-sm mb-4">
              It will be reviewed by our team shortly.
            </p>
            <button
              onClick={() => navigate("/university/submissions")}
              className="text-[#0d9488] text-sm hover:text-[#0f766e] underline underline-offset-4 transition"
            >
              View My Submissions →
            </button>
          </div>
        )}

        {/* ── Form ── */}
        <form onSubmit={handleSubmit} className="space-y-7">

          {/* Title */}
          <div>
            <label className="block text-sm text-[#4a4a6a] mb-2 font-medium">Title *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value.slice(0, 200))}
              placeholder="e.g. A novel polymer membrane for CO₂ capture"
              className={inputCls}
            />
            <p className="text-[#8888aa] text-xs mt-1.5 text-right">{title.length} / 200</p>
          </div>

          {/* IP Type */}
          <div>
            <label className="block text-sm text-[#4a4a6a] mb-3 font-medium">IP Type *</label>
            <div className="flex gap-3">
              {[
                { val: "paper", label: "📄 Research Paper" },
                { val: "patent", label: "🔬 Patent" },
              ].map(({ val, label }) => (
                <button
                  key={val}
                  type="button"
                  onClick={() => setIpType(val)}
                  className={`flex-1 px-4 py-3 rounded-xl border text-sm font-medium transition
                    ${ip_type === val
                      ? "bg-[#ccfbf1] border-[#0d9488]/50 text-[#0d9488]"
                      : "bg-white border-[#e8e4d9] text-[#4a4a6a] hover:border-[#0d9488]/40"
                    }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Domain */}
          <div>
            <label className="block text-sm text-[#4a4a6a] mb-2 font-medium">Domain *</label>
            <select
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className={inputCls + " appearance-none cursor-pointer"}
            >
              <option value="" disabled>Select a domain…</option>
              {DOMAINS.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>

          {/* University */}
          <div>
            <label className="block text-sm text-[#4a4a6a] mb-2 font-medium">University / Institution *</label>
            <input
              type="text"
              value={university}
              onChange={(e) => setUniversity(e.target.value)}
              placeholder="e.g. IIT Bombay"
              className={inputCls}
            />
          </div>

          {/* Contributors */}
          <div>
            <label className="block text-sm text-[#4a4a6a] mb-2 font-medium">Contributors *</label>
            <input
              type="text"
              value={contributors}
              onChange={(e) => setContributors(e.target.value)}
              placeholder="e.g. Dr. Sharma, Dr. Patel, Prof. Singh"
              className={inputCls}
            />
            <p className="text-[#8888aa] text-xs mt-1.5">Enter contributor names separated by commas</p>
          </div>

          {/* Legal Status — only for Patents */}
          {ip_type === "patent" && (
            <div>
              <label className="block text-sm text-[#4a4a6a] mb-2 font-medium">Legal Status *</label>
              <select
                value={legal_status}
                onChange={(e) => setLegalStatus(e.target.value)}
                className={inputCls + " appearance-none cursor-pointer"}
              >
                <option value="PENDING">PENDING</option>
                <option value="ACTIVE">ACTIVE</option>
                <option value="EXPIRED">EXPIRED</option>
              </select>
            </div>
          )}

          {/* Abstract */}
          <div>
            <label className="block text-sm text-[#4a4a6a] mb-2 font-medium">Abstract *</label>
            <textarea
              value={abstract}
              onChange={(e) => setAbstract(e.target.value.slice(0, 2000))}
              placeholder="Describe the technology, methodology, and its applications…"
              rows={7}
              style={{ minHeight: "150px" }}
              className={inputCls + " resize-y leading-relaxed"}
            />
            <p className="text-[#8888aa] text-xs mt-1.5 text-right">{abstract.length} / 2000</p>
          </div>

          {/* DOI — only for Research Papers */}
          {ip_type === "paper" && (
            <div>
              <label className="block text-sm text-[#4a4a6a] mb-2 font-medium">DOI</label>
              <input
                type="text"
                value={doi}
                onChange={e => setDoi(e.target.value)}
                placeholder="e.g. 10.1038/s41586-021-03819-2"
                className={inputCls}
              />
              <p className="text-[#8888aa] text-xs mt-1.5">Digital Object Identifier — found on the paper's journal page</p>
            </div>
          )}

          {/* Patent Number — only for Patents */}
          {ip_type === "patent" && (
            <div>
              <label className="block text-sm text-[#4a4a6a] mb-2 font-medium">Patent Number</label>
              <input
                type="text"
                value={patentNumber}
                onChange={e => setPatentNumber(e.target.value)}
                placeholder="e.g. US10123456B2"
                className={inputCls}
              />
              <p className="text-[#8888aa] text-xs mt-1.5">Found on the patent document or Lens.org</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl px-5 py-4 text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* Submit button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#0d9488] hover:bg-[#0f766e] disabled:bg-[#8888aa] disabled:cursor-not-allowed text-white font-semibold py-3.5 rounded-xl transition text-sm"
          >
            {loading
              ? "Submitting…"
              : isEdit ? "Update Submission" : "Submit for Review"
            }
          </button>

        </form>
      </main>
    </div>
  );
}
