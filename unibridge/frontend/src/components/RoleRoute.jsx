import { Navigate } from "react-router-dom";
import { isLoggedIn, getRole } from "../utils/auth";

const RoleRoute = ({ children, role }) => {
  if (!isLoggedIn()) return <Navigate to="/login" replace />;
  if (getRole() !== role) return <Navigate to="/login" replace />;
  return children;
};

export default RoleRoute;
