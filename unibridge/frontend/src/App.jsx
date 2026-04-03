import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ProtectedRoute from "./components/ProtectedRoute";
import RoleRoute from "./components/RoleRoute";
import Dashboard from "./pages/industry/Dashboard";
import Search from "./pages/industry/Search";
import Bookmarks from "./pages/industry/Bookmarks";

// ---------- Placeholder pages ----------
const Placeholder = ({ label }) => (
  <div className="min-h-screen flex items-center justify-center text-gray-600 text-lg">
    {label}
  </div>
);

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Root → login */}
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* Public */}
        <Route path="/login"    element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* ── Industry ── */}
        <Route
          path="/industry/search"
          element={
            <ProtectedRoute>
              <RoleRoute role="industry">
                <Search />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/industry/dashboard"
          element={
            <ProtectedRoute>
              <RoleRoute role="industry">
                <Dashboard />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/industry/bookmarks"
          element={
            <ProtectedRoute>
              <RoleRoute role="industry">
                <Bookmarks />
              </RoleRoute>
            </ProtectedRoute>
          }
        />

        {/* ── University ── */}
        <Route
          path="/university/dashboard"
          element={
            <ProtectedRoute>
              <RoleRoute role="university">
                <Placeholder label="University Dashboard — coming soon" />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/university/submit"
          element={
            <ProtectedRoute>
              <RoleRoute role="university">
                <Placeholder label="Submit IP — coming soon" />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/university/submissions"
          element={
            <ProtectedRoute>
              <RoleRoute role="university">
                <Placeholder label="Submissions — coming soon" />
              </RoleRoute>
            </ProtectedRoute>
          }
        />

        {/* ── Admin ── */}
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute>
              <RoleRoute role="admin">
                <Placeholder label="Admin Dashboard — coming soon" />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute>
              <RoleRoute role="admin">
                <Placeholder label="User Management — coming soon" />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/submissions"
          element={
            <ProtectedRoute>
              <RoleRoute role="admin">
                <Placeholder label="Submission Queue — coming soon" />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/analytics"
          element={
            <ProtectedRoute>
              <RoleRoute role="admin">
                <Placeholder label="Analytics — coming soon" />
              </RoleRoute>
            </ProtectedRoute>
          }
        />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
