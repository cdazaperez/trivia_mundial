import { useState, useEffect } from "react";
import {
  getMatches,
  updateMatchResult,
  adminResetPassword,
  listUsers,
  resetAllResults,
} from "../services/api";
import { Match, User } from "../types";
import { useAuth } from "../contexts/AuthContext";

export default function Admin() {
  const { user } = useAuth();
  const [matches, setMatches] = useState<Match[]>([]);
  const [scores, setScores] = useState<Record<number, { home: string; away: string }>>({});
  const [msg, setMsg] = useState("");
  const [filter, setFilter] = useState<"pending" | "finished">("pending");

  // Password reset
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [pwdMsg, setPwdMsg] = useState("");

  // Reset confirmation
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [resetMsg, setResetMsg] = useState("");

  useEffect(() => {
    loadMatches();
    loadUsers();
  }, []);

  const loadMatches = async () => {
    try {
      const res = await getMatches();
      setMatches(res.data);
    } catch {
      // handle
    }
  };

  const loadUsers = async () => {
    try {
      const res = await listUsers();
      setUsers(res.data);
    } catch {
      // handle
    }
  };

  if (!user?.is_admin) {
    return (
      <div className="page">
        <h2>Acceso Denegado</h2>
        <p>No tienes permisos de administrador.</p>
      </div>
    );
  }

  const filteredMatches = matches.filter((m) =>
    filter === "pending" ? !m.is_finished : m.is_finished
  );

  const saveResult = async (matchId: number) => {
    const s = scores[matchId];
    if (!s || s.home === "" || s.away === "") {
      setMsg("Ingresa ambos marcadores");
      return;
    }

    try {
      await updateMatchResult(matchId, {
        home_score: parseInt(s.home),
        away_score: parseInt(s.away),
      });
      setMsg("Resultado guardado y puntos calculados");
      loadMatches();
    } catch (err: any) {
      setMsg(err.response?.data?.detail || "Error");
    }
  };

  const handleResetPassword = async () => {
    setPwdMsg("");
    if (!selectedUser || !newPassword) {
      setPwdMsg("Selecciona un usuario e ingresa la nueva contraseña");
      return;
    }
    if (newPassword.length < 6) {
      setPwdMsg("La contraseña debe tener al menos 6 caracteres");
      return;
    }

    try {
      const res = await adminResetPassword({
        username: selectedUser,
        new_password: newPassword,
      });
      setPwdMsg(res.data.detail);
      setNewPassword("");
      setSelectedUser("");
    } catch (err: any) {
      setPwdMsg(err.response?.data?.detail || "Error al resetear contraseña");
    }
  };

  const handleResetAll = async () => {
    try {
      const res = await resetAllResults();
      setResetMsg(res.data.detail);
      setShowResetConfirm(false);
      loadMatches();
    } catch (err: any) {
      setResetMsg(err.response?.data?.detail || "Error al reiniciar");
    }
  };

  return (
    <div className="page">
      <h2>Panel de Administración</h2>

      {/* === PASSWORD RESET SECTION === */}
      <div className="admin-section">
        <h3>Resetear Contraseña de Participante</h3>
        {pwdMsg && <div className="success-msg">{pwdMsg}</div>}
        <div className="admin-form-row">
          <div className="form-group">
            <label>Usuario</label>
            <select
              value={selectedUser}
              onChange={(e) => setSelectedUser(e.target.value)}
            >
              <option value="">Seleccionar usuario...</option>
              {users.map((u) => (
                <option key={u.id} value={u.username}>
                  {u.full_name} (@{u.username})
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Nueva Contraseña</label>
            <input
              type="text"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Mínimo 6 caracteres"
            />
          </div>
          <button className="btn btn-primary" onClick={handleResetPassword}>
            Resetear
          </button>
        </div>
      </div>

      {/* === RESET ALL SECTION === */}
      <div className="admin-section">
        <h3>Reiniciar Marcadores (Pruebas)</h3>
        <p className="hint">
          Reinicia todos los resultados de partidos y puntajes a cero. Los pronósticos de los
          participantes se mantienen. Usar solo para pruebas.
        </p>
        {resetMsg && <div className="success-msg">{resetMsg}</div>}
        {!showResetConfirm ? (
          <button
            className="btn btn-danger"
            onClick={() => setShowResetConfirm(true)}
          >
            Reiniciar Todos los Marcadores
          </button>
        ) : (
          <div className="confirm-box">
            <p>
              <strong>¿Estás seguro?</strong> Se borrarán todos los resultados
              de partidos y los puntos de todos los participantes.
            </p>
            <button className="btn btn-danger" onClick={handleResetAll}>
              Sí, Reiniciar Todo
            </button>
            <button
              className="btn"
              onClick={() => setShowResetConfirm(false)}
              style={{ marginLeft: "0.5rem", background: "#6b7280", color: "white" }}
            >
              Cancelar
            </button>
          </div>
        )}
      </div>

      {/* === MATCH RESULTS SECTION === */}
      <div className="admin-section">
        <h3>Resultados de Partidos</h3>
        <p className="hint">Ingresa los resultados reales de cada partido</p>

        <div className="phase-tabs">
          <button
            className={`tab ${filter === "pending" ? "active" : ""}`}
            onClick={() => setFilter("pending")}
          >
            Pendientes ({matches.filter((m) => !m.is_finished).length})
          </button>
          <button
            className={`tab ${filter === "finished" ? "active" : ""}`}
            onClick={() => setFilter("finished")}
          >
            Finalizados ({matches.filter((m) => m.is_finished).length})
          </button>
        </div>

        {msg && <div className="success-msg">{msg}</div>}

        <div className="matches-list">
          {filteredMatches.map((match) => {
            const s = scores[match.id] || {
              home: match.home_score?.toString() || "",
              away: match.away_score?.toString() || "",
            };

            return (
              <div key={match.id} className="match-card admin-card">
                <div className="match-teams">
                  <div className="team home">
                    <span className="flag">{match.home_team?.flag_emoji}</span>
                    <span className="name">{match.home_team?.name}</span>
                  </div>

                  <div className="match-prediction-input">
                    <input
                      type="number"
                      min="0"
                      max="20"
                      value={s.home}
                      onChange={(e) =>
                        setScores({
                          ...scores,
                          [match.id]: { ...s, home: e.target.value },
                        })
                      }
                    />
                    <span className="vs">-</span>
                    <input
                      type="number"
                      min="0"
                      max="20"
                      value={s.away}
                      onChange={(e) =>
                        setScores({
                          ...scores,
                          [match.id]: { ...s, away: e.target.value },
                        })
                      }
                    />
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => saveResult(match.id)}
                    >
                      {match.is_finished ? "Corregir" : "Guardar"}
                    </button>
                  </div>

                  <div className="team away">
                    <span className="name">{match.away_team?.name}</span>
                    <span className="flag">{match.away_team?.flag_emoji}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
