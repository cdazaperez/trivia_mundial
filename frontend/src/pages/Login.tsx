import { useState, FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { login } from "../services/api";
import { RulesCompact } from "../components/Disclaimer";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { setAuth } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res = await login(username, password);
      setAuth(res.data.access_token);
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Error al iniciar sesión");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-mascots">
          <div className="mascot mascot-maple">🦌<span>Maple</span></div>
          <div className="mascot mascot-zayu">🐆<span>Zayu</span></div>
          <div className="mascot mascot-clutch">🦅<span>Clutch</span></div>
        </div>
        <h1>Trivia Mundial 2026 - Amigos</h1>
        <p className="auth-subtitle">FIFA World Cup Canada/Mexico/USA</p>
        <h2>Iniciar Sesion</h2>
        {error && <div className="error-msg">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Usuario</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary btn-full">
            Entrar
          </button>
        </form>
        <p className="auth-link">
          ¿No tienes cuenta? <Link to="/register">Regístrate</Link>
        </p>
        <RulesCompact />
      </div>
    </div>
  );
}
