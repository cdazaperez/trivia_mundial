import { useState, FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register } from "../services/api";
import { RulesCompact } from "../components/Disclaimer";

export default function Register() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    full_name: "",
  });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await register(form);
      navigate("/login");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Error al registrarse");
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
        <h2>Registro</h2>
        {error && <div className="error-msg">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Nombre Completo</label>
            <input
              type="text"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Usuario</label>
            <input
              type="text"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Contraseña (mínimo 6 caracteres)</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
              minLength={6}
            />
          </div>
          <button type="submit" className="btn btn-primary btn-full">
            Registrarse
          </button>
        </form>
        <p className="auth-link">
          ¿Ya tienes cuenta? <Link to="/login">Inicia Sesión</Link>
        </p>
      </div>
      <RulesCompact />
    </div>
  );
}
