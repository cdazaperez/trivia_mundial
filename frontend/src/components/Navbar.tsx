import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!user) return null;

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">Trivia Mundial 2026 - Amigos</Link>
      </div>
      <div className="navbar-links">
        {!user.is_admin && (
          <>
            <Link to="/today">Hoy</Link>
            <Link to="/matches">Partidos</Link>
            <Link to="/bracket">Llaves</Link>
            <Link to="/predictions">Mis Pronósticos</Link>
            <Link to="/groups">Grupos</Link>
            <Link to="/bonus">Apuestas Bonus</Link>
          </>
        )}
        <Link to="/leaderboard">Tabla de Posiciones</Link>
        {user.is_admin && <Link to="/admin">Admin</Link>}
      </div>
      <div className="navbar-user">
        <span>{user.full_name}</span>
        <Link to="/change-password" className="btn btn-sm">
          Contraseña
        </Link>
        <button onClick={handleLogout} className="btn btn-sm">
          Salir
        </button>
      </div>
    </nav>
  );
}
