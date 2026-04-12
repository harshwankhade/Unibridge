import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ProtectedRoute from "./components/ProtectedRoute";
import RoleRoute from "./components/RoleRoute";
import Dashboard from "./pages/industry/Dashboard";
import Search from "./pages/industry/Search";
import Bookmarks from "./pages/industry/Bookmarks";
import UniversityDashboard from "./pages/university/Dashboard";
import SubmitIP from "./pages/university/SubmitIP";
import Submissions from "./pages/university/Submissions";
import AdminDashboard from "./pages/admin/Dashboard";
import AdminUsers from "./pages/admin/Users";
import AdminSubmissions from "./pages/admin/Submissions";
import AdminAnalytics from "./pages/admin/Analytics";

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
                <UniversityDashboard />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/university/submit"
          element={
            <ProtectedRoute>
              <RoleRoute role="university">
                <SubmitIP />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/university/submissions"
          element={
            <ProtectedRoute>
              <RoleRoute role="university">
                <Submissions />
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
                <AdminDashboard />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute>
              <RoleRoute role="admin">
                <AdminUsers />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/submissions"
          element={
            <ProtectedRoute>
              <RoleRoute role="admin">
                <AdminSubmissions />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/analytics"
          element={
            <ProtectedRoute>
              <RoleRoute role="admin">
                <AdminAnalytics />
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
