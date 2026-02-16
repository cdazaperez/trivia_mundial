import { useState, useEffect } from "react";
import {
  getMatches,
  updateMatchResult,
  adminResetPassword,
  listUsers,
  resetAllResults,
  reseedData,
  getKnockoutStatus,
  generateKnockoutRound,
} from "../services/api";
import { Match, User } from "../types";
import { useAuth } from "../contexts/AuthContext";

const PHASE_LABELS: Record<string, string> = {
  round_of_32: "32avos de Final",
  round_of_16: "Octavos de Final",
  quarter_final: "Cuartos de Final",
  semi_final: "Semifinales",
  finals: "3er Puesto y Final",
};

const KNOCKOUT_PHASES = [
  { key: "round_of_32", label: "32avos de Final", reqKey: "group_phase_complete", blockKey: "round_of_32" },
  { key: "round_of_16", label: "Octavos de Final", reqKey: "round_of_32", blockKey: "round_of_16" },
  { key: "quarter_final", label: "Cuartos de Final", reqKey: "round_of_16", blockKey: "quarter_final" },
  { key: "semi_final", label: "Semifinales", reqKey: "quarter_final", blockKey: "semi_final" },
  { key: "finals", label: "3er Puesto y Final", reqKey: "semi_final", blockKey: "final" },
];

const ADMIN_PHASE_FILTER = [
  { key: "all", label: "Todos" },
  { key: "group", label: "Grupos" },
  { key: "round_of_32", label: "32avos" },
  { key: "round_of_16", label: "Octavos" },
  { key: "quarter_final", label: "Cuartos" },
  { key: "semi_final", label: "Semis" },
  { key: "third_place", label: "3er Puesto" },
  { key: "final", label: "Final" },
];

export default function Admin() {
  const { user } = useAuth();
  const [matches, setMatches] = useState<Match[]>([]);
  const [scores, setScores] = useState<Record<number, { home: string; away: string }>>({});
  const [msg, setMsg] = useState("");
  const [filter, setFilter] = useState<"pending" | "finished">("pending");
  const [phaseFilter, setPhaseFilter] = useState<string>("all");

  // Password reset
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [pwdMsg, setPwdMsg] = useState("");

  // Reset confirmation
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [resetMsg, setResetMsg] = useState("");

  // Knockout generation
  const [knockoutStatus, setKnockoutStatus] = useState<any>(null);
  const [knockoutMsg, setKnockoutMsg] = useState("");
  const [generating, setGenerating] = useState(false);

  // Reseed
  const [showReseedConfirm, setShowReseedConfirm] = useState(false);
  const [reseedMsg, setReseedMsg] = useState("");

  useEffect(() => {
    loadMatches();
    loadUsers();
    loadKnockoutStatus();
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

  const loadKnockoutStatus = async () => {
    try {
      const res = await getKnockoutStatus();
      setKnockoutStatus(res.data);
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

  const filteredMatches = matches
    .filter((m) => (filter === "pending" ? !m.is_finished : m.is_finished))
    .filter((m) => (phaseFilter === "all" ? true : m.phase === phaseFilter));

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
      loadKnockoutStatus();
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
      loadKnockoutStatus();
    } catch (err: any) {
      setResetMsg(err.response?.data?.detail || "Error al reiniciar");
    }
  };

  const handleGenerateKnockout = async (phase: string) => {
    setGenerating(true);
    setKnockoutMsg("");
    try {
      const res = await generateKnockoutRound(phase);
      setKnockoutMsg(res.data.message);
      loadMatches();
      loadKnockoutStatus();
    } catch (err: any) {
      setKnockoutMsg(err.response?.data?.detail || "Error al generar fase");
    }
    setGenerating(false);
  };

  const handleReseed = async () => {
    try {
      const res = await reseedData();
      setReseedMsg(res.data.detail);
      setShowReseedConfirm(false);
      loadMatches();
      loadKnockoutStatus();
    } catch (err: any) {
      setReseedMsg(err.response?.data?.detail || "Error al re-seedear");
    }
  };

  const isPhaseReady = (reqKey: string) => {
    if (!knockoutStatus) return false;
    if (reqKey === "group_phase_complete") return knockoutStatus.group_phase_complete;
    return knockoutStatus[reqKey]?.complete;
  };

  const isPhaseGenerated = (blockKey: string) => {
    if (!knockoutStatus) return false;
    return knockoutStatus[blockKey]?.exists;
  };

  return (
    <div className="page">
      <h2>Panel de Administracion</h2>

      {/* === KNOCKOUT GENERATION === */}
      <div className="admin-section">
        <h3>Generar Fases Eliminatorias</h3>
        <p className="hint">
          Genera los partidos de la siguiente fase una vez completada la fase anterior.
        </p>
        {knockoutMsg && <div className="success-msg">{knockoutMsg}</div>}

        <div className="knockout-buttons">
          {KNOCKOUT_PHASES.map((phase) => {
            const ready = isPhaseReady(phase.reqKey);
            const generated = isPhaseGenerated(phase.blockKey);
            return (
              <button
                key={phase.key}
                className={`btn ${ready && !generated ? "btn-primary" : ""}`}
                onClick={() => handleGenerateKnockout(phase.key)}
                disabled={!ready || generated || generating}
              >
                {generated ? `${phase.label} (generado)` : `Generar ${phase.label}`}
              </button>
            );
          })}
        </div>
      </div>

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
              placeholder="Minimo 6 caracteres"
            />
          </div>
          <button className="btn btn-primary" onClick={handleResetPassword}>
            Resetear
          </button>
        </div>
      </div>

      {/* === RESET / RESEED === */}
      <div className="admin-section">
        <h3>Reiniciar (Pruebas)</h3>

        <div style={{ marginBottom: "1rem" }}>
          <p className="hint">
            <strong>Reiniciar marcadores:</strong> Borra resultados y puntos. Pronosticos se mantienen.
          </p>
          {resetMsg && <div className="success-msg">{resetMsg}</div>}
          {!showResetConfirm ? (
            <button className="btn btn-danger" onClick={() => setShowResetConfirm(true)}>
              Reiniciar Marcadores
            </button>
          ) : (
            <div className="confirm-box">
              <p><strong>¿Seguro?</strong> Se borran resultados, puntos y partidos eliminatorios.</p>
              <button className="btn btn-danger" onClick={handleResetAll}>Si, Reiniciar</button>
              <button className="btn" onClick={() => setShowResetConfirm(false)}
                style={{ marginLeft: "0.5rem", background: "#6b7280", color: "white" }}>
                Cancelar
              </button>
            </div>
          )}
        </div>

        <div>
          <p className="hint">
            <strong>Re-seedear equipos:</strong> Borra todo y recarga equipos/partidos del sorteo oficial.
            Solo funciona si no hay pronosticos.
          </p>
          {reseedMsg && <div className="success-msg">{reseedMsg}</div>}
          {!showReseedConfirm ? (
            <button className="btn btn-danger" onClick={() => setShowReseedConfirm(true)}>
              Re-seedear Equipos
            </button>
          ) : (
            <div className="confirm-box">
              <p><strong>¿Seguro?</strong> Se borran todos los equipos y partidos y se recargan.</p>
              <button className="btn btn-danger" onClick={handleReseed}>Si, Re-seedear</button>
              <button className="btn" onClick={() => setShowReseedConfirm(false)}
                style={{ marginLeft: "0.5rem", background: "#6b7280", color: "white" }}>
                Cancelar
              </button>
            </div>
          )}
        </div>
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

        <div className="group-tabs" style={{ marginTop: "0.5rem" }}>
          {ADMIN_PHASE_FILTER.map((p) => (
            <button
              key={p.key}
              className={`tab tab-sm ${phaseFilter === p.key ? "active" : ""}`}
              onClick={() => setPhaseFilter(p.key)}
            >
              {p.label}
            </button>
          ))}
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
                <div className="match-date" style={{ fontSize: "0.75rem", color: "#6b7280" }}>
                  #{match.match_number} | {match.phase !== "group" ? match.phase.replace(/_/g, " ") : `Grupo ${match.group_name}`}
                </div>
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
