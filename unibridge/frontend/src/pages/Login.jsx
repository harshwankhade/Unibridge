import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { saveAuth } from "../utils/auth";

const AUTH_URL = "http://localhost:8000/auth";

const ROLE_REDIRECTS = {
  industry:   "/industry/search",
  university: "/university/dashboard",
  admin:      "/admin/dashboard",
};

export default function Login() {
  const navigate = useNavigate();
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [error,    setError]    = useState("");
  const [loading,  setLoading]  = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await axios.post(`${AUTH_URL}/login`, { email, password });
      saveAuth(data.access_token, {
        user_id: data.user_id,
        email:   data.email,
        role:    data.role,
      });
      navigate(ROLE_REDIRECTS[data.role] ?? "/login");
    } catch {
      setError("Invalid email or password");
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
          Sign in to your account
        </p>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-[#4a4a6a] mb-1">Email</label>
            <input
              id="login-email"
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
              id="login-password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className={inputCls}
            />
          </div>

          {error && (
            <p className="text-red-500 text-sm text-center">{error}</p>
          )}

          <button
            id="login-submit"
            type="submit"
            disabled={loading}
            className="w-full bg-[#0d9488] hover:bg-[#0f766e] disabled:bg-[#8888aa]
                       text-white font-semibold py-2 rounded-lg transition"
          >
            {loading ? "Signing in…" : "Login"}
          </button>
        </form>

        <p className="text-center text-sm text-[#8888aa] mt-6">
          Don&apos;t have an account?{" "}
          <Link to="/register" className="text-[#0d9488] hover:underline font-medium">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
