import { useState, useEffect } from "react";
import { getLeaderboard, getPhaseWinners } from "../services/api";
import { LeaderboardEntry } from "../types";

const PHASES = [
  { key: "", label: "General" },
  { key: "group", label: "Fase de Grupos" },
  { key: "round_of_32", label: "Octavos (32avos)" },
  { key: "round_of_16", label: "Octavos de Final" },
  { key: "quarter_final", label: "Cuartos de Final" },
  { key: "semi_final", label: "Semifinales" },
  { key: "final", label: "Final" },
];

export default function Leaderboard() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [selectedPhase, setSelectedPhase] = useState("");
  const [phaseWinners, setPhaseWinners] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, [selectedPhase]);

  const loadData = async () => {
    try {
      const [lbRes, winnersRes] = await Promise.all([
        getLeaderboard(selectedPhase || undefined),
        getPhaseWinners(),
      ]);
      setEntries(lbRes.data);
      setPhaseWinners(winnersRes.data);
    } catch {
      // handle
    }
  };

  const getMedal = (index: number) => {
    if (index === 0) return "🥇";
    if (index === 1) return "🥈";
    if (index === 2) return "🥉";
    return `${index + 1}`;
  };

  return (
    <div className="page">
      <h2>Tabla de Posiciones</h2>

      <div className="phase-tabs">
        {PHASES.map((p) => (
          <button
            key={p.key}
            className={`tab ${selectedPhase === p.key ? "active" : ""}`}
            onClick={() => setSelectedPhase(p.key)}
          >
            {p.label}
          </button>
        ))}
      </div>

      {selectedPhase !== "" && (
        <div style={{
          background: "#eef2ff",
          border: "1px solid #c7d2fe",
          borderRadius: "8px",
          padding: "0.75rem 1rem",
          marginBottom: "1rem",
          fontSize: "0.9rem",
          color: "#4338ca",
        }}>
          Mostrando puntos solo de la fase: <strong>{PHASES.find(p => p.key === selectedPhase)?.label}</strong>.
          Selecciona "General" para ver el acumulado total y los premios.
        </div>
      )}

      {entries.length === 0 && selectedPhase !== "" && (
        <div style={{
          textAlign: "center",
          padding: "2rem",
          color: "#6b7280",
          fontSize: "0.95rem",
        }}>
          No hay puntos registrados para esta fase. Los participantes aún no tienen pronósticos calificados en esta fase.
        </div>
      )}

      <table className="leaderboard-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Jugador</th>
            <th>Puntos</th>
            <th>Exactos</th>
            <th>Resultados</th>
            <th>Grupos</th>
            <th>Bonus</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry, i) => (
            <tr key={entry.user_id} className={i < 3 ? "top-player" : ""}>
              <td className="rank">{getMedal(i)}</td>
              <td>
                <strong>{entry.full_name}</strong>
                <br />
                <small>@{entry.username}</small>
              </td>
              <td className="points-col">{entry.total_points}</td>
              <td>{entry.exact_scores}</td>
              <td>{entry.correct_results}</td>
              <td>{entry.group_points}</td>
              <td>{entry.bonus_points}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {phaseWinners && selectedPhase === "" && (
        <div className="phase-winners-section">
          <h3>Premios al Final del Mundial</h3>
          <div className="phase-winner-card">
            <p>Partidos finalizados: {phaseWinners.finished_matches || 0}/{phaseWinners.total_matches || 0}</p>
            <p>
              Participantes: {phaseWinners.active_participants || 0} |
              Pagados: {phaseWinners.paid_participants || 0} |
              Inscripción: ${(phaseWinners.entry_fee || 0).toLocaleString("es-CO")} |
              <strong> Pozo total: ${(phaseWinners.total_pool || 0).toLocaleString("es-CO")} pesos</strong>
            </p>
            {phaseWinners.tournament_finished && <p><strong>Torneo finalizado</strong></p>}

            {phaseWinners.prizes && (
              <div style={{ margin: "0.75rem 0", padding: "0.5rem", background: "#f0fdf4", borderRadius: "8px" }}>
                {phaseWinners.prizes.map((p: any) => (
                  <div key={p.place} style={{ fontSize: "0.85rem", padding: "2px 0" }}>
                    {getMedal(p.place - 1)} {p.pct} = <strong>${p.amount.toLocaleString("es-CO")} pesos</strong>
                  </div>
                ))}
                {phaseWinners.admin_fee != null && (
                  <div style={{ fontSize: "0.85rem", padding: "2px 0", color: "#6b7280", borderTop: "1px solid #d1fae5", marginTop: "4px", paddingTop: "4px" }}>
                    Administración: {phaseWinners.admin_fee_pct} = <strong>${(phaseWinners.admin_fee || 0).toLocaleString("es-CO")} pesos</strong>
                  </div>
                )}
              </div>
            )}

            <div style={{ marginTop: "0.5rem" }}>
              {phaseWinners.top_3?.map((w: any, i: number) => (
                <div key={i} className="winner-entry">
                  {getMedal(i)} {w.full_name} - {w.points} pts
                  {w.prize > 0 && (
                    <span style={{ marginLeft: "0.5rem", color: "#166534", fontWeight: "bold", fontSize: "0.85rem" }}>
                      (${w.prize.toLocaleString("es-CO")} pesos)
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
