import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

const AUTH_URL = "http://localhost:8000/auth";

export default function Register() {
  const navigate  = useNavigate();
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [role,     setRole]     = useState("industry");
  const [error,    setError]    = useState("");
  const [success,  setSuccess]  = useState("");
  const [loading,  setLoading]  = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setSuccess("");
    setLoading(true);
    try {
      await axios.post(`${AUTH_URL}/register`, { email, password, role });
      setSuccess("Account created. Please log in.");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      const msg = err.response?.data?.detail ?? "Registration failed. Please try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const inputCls =
    "w-full bg-white border border-[#e8e4d9] rounded-lg px-4 py-2 text-sm text-[#1a1a2e] " +
    "placeholder-[#8888aa] focus:outline-none focus:border-[#0d9488] focus:ring-1 focus:ring-[#0d9488] transition";

  return (
    <div
      className="min-h-screen bg-[#fdfcf7] flex items-center justify-center px-4"
      style={{ fontFamily: "'DM Sans', sans-serif" }}
    >
      <div className="bg-white border border-[#e8e4d9] shadow-md rounded-2xl w-full max-w-md p-8">
        {/* Title */}
        <h1
          className="text-3xl font-bold text-center text-[#1a1a2e] mb-2"
          style={{ fontFamily: "'DM Serif Display', serif" }}
        >
          UniBridge
        </h1>
        <p className="text-center text-[#8888aa] text-sm mb-8">
          Create your account
        </p>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-[#4a4a6a] mb-1">Email</label>
            <input
              id="register-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className={inputCls}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#4a4a6a] mb-1">Password</label>
            <input
              id="register-password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className={inputCls}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#4a4a6a] mb-1">Role</label>
            <select
              id="register-role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className={inputCls + " bg-white cursor-pointer"}
            >
              <option value="industry">Industry</option>
              <option value="university">University</option>
            </select>
          </div>

          {error   && <p className="text-red-500 text-sm text-center">{error}</p>}
          {success && <p className="text-green-600 text-sm text-center">{success}</p>}

          <button
            id="register-submit"
            type="submit"
            disabled={loading}
            className="w-full bg-[#0d9488] hover:bg-[#0f766e] disabled:bg-[#8888aa]
                       text-white font-semibold py-2 rounded-lg transition"
          >
            {loading ? "Creating account…" : "Register"}
          </button>
        </form>

        <p className="text-center text-sm text-[#8888aa] mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-[#0d9488] hover:underline font-medium">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
