import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import Today from "./pages/Today";
import Bracket from "./pages/Bracket";
import Matches from "./pages/Matches";
import Groups from "./pages/Groups";
import Bonus from "./pages/Bonus";
import Predictions from "./pages/Predictions";
import Leaderboard from "./pages/Leaderboard";
import Admin from "./pages/Admin";
import ChangePassword from "./pages/ChangePassword";
import "./App.css";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="loading">Cargando...</div>;
  return user ? <>{children}</> : <Navigate to="/login" />;
}

function AppRoutes() {
  const { user, loading } = useAuth();

  if (loading) return <div className="loading">Cargando...</div>;

  return (
    <>
      {user && <Navbar />}
      <main className="main-content">
        <Routes>
          <Route
            path="/login"
            element={user ? <Navigate to="/" /> : <Login />}
          />
          <Route
            path="/register"
            element={user ? <Navigate to="/" /> : <Register />}
          />
          <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
          <Route path="/today" element={<PrivateRoute><Today /></PrivateRoute>} />
          <Route path="/bracket" element={<PrivateRoute><Bracket /></PrivateRoute>} />
          <Route path="/matches" element={<PrivateRoute><Matches /></PrivateRoute>} />
          <Route path="/groups" element={<PrivateRoute><Groups /></PrivateRoute>} />
          <Route path="/bonus" element={<PrivateRoute><Bonus /></PrivateRoute>} />
          <Route path="/predictions" element={<PrivateRoute><Predictions /></PrivateRoute>} />
          <Route path="/leaderboard" element={<PrivateRoute><Leaderboard /></PrivateRoute>} />
          <Route path="/change-password" element={<PrivateRoute><ChangePassword /></PrivateRoute>} />
          <Route path="/admin" element={<PrivateRoute><Admin /></PrivateRoute>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
