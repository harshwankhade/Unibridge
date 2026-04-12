import { Link, useLocation } from "react-router-dom";
import { logout } from "../utils/auth";

export default function AdminNav({ pendingCount = 0 }) {
  const { pathname } = useLocation();

  const links = [
    { to: "/admin/dashboard",   label: "Dashboard"    },
    { to: "/admin/users",       label: "Users"        },
    { to: "/admin/submissions", label: "Submissions"  },
    { to: "/admin/analytics",   label: "Analytics"    },
  ];

  return (
    <nav
      className="border-b border-slate-800 px-8 py-4 flex items-center justify-between"
      style={{ fontFamily: "'DM Sans', sans-serif" }}
    >
      {/* Brand */}
      <span
        className="text-cyan-400 font-bold text-xl tracking-tight"
        style={{ fontFamily: "'DM Serif Display', serif" }}
      >
        UniBridge <span className="text-slate-500 text-sm font-normal ml-1">admin</span>
      </span>

      {/* Links */}
      <div className="flex items-center gap-6 text-sm">
        {links.map(({ to, label }) => {
          const active = pathname === to;
          const isPending = to === "/admin/submissions" && pendingCount > 0;
          return (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-1.5 transition ${
                active ? "text-white font-medium" : "text-slate-400 hover:text-white"
              }`}
            >
              {label}
              {isPending && (
                <span className="bg-amber-500 text-slate-900 text-xs font-bold px-1.5 py-0.5 rounded-full leading-none">
                  {pendingCount}
                </span>
              )}
            </Link>
          );
        })}
        <button
          onClick={logout}
          className="text-slate-400 hover:text-red-400 transition text-sm ml-2"
        >
          Sign out
        </button>
      </div>
    </nav>
  );
}
