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
            <tr key={entry.user_id} className={i < 2 ? "top-player" : ""}>
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

      {phaseWinners && Object.keys(phaseWinners).length > 0 && (
        <div className="phase-winners-section">
          <h3>Ganadores por Fase</h3>
          {Object.entries(phaseWinners).map(([phase, data]: [string, any]) => (
            <div key={phase} className="phase-winner-card">
              <h4>
                {PHASES.find((p) => p.key === phase)?.label || phase}
                {data.all_completed && " ✓"}
              </h4>
              <p>
                Partidos: {data.completed_matches}/{data.total_matches}
              </p>
              {data.top_2?.map((w: any, i: number) => (
                <div key={i} className="winner-entry">
                  {getMedal(i)} {w.full_name} - {w.points} pts
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
