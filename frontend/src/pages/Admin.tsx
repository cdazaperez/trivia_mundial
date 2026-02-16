import { useState, useEffect } from "react";
import { getMatches, updateMatchResult } from "../services/api";
import { Match } from "../types";
import { useAuth } from "../contexts/AuthContext";

export default function Admin() {
  const { user } = useAuth();
  const [matches, setMatches] = useState<Match[]>([]);
  const [scores, setScores] = useState<Record<number, { home: string; away: string }>>({});
  const [msg, setMsg] = useState("");
  const [filter, setFilter] = useState<"pending" | "finished">("pending");

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    try {
      const res = await getMatches();
      setMatches(res.data);
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

  return (
    <div className="page">
      <h2>Panel de Administración</h2>
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
                  {!match.is_finished && (
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => saveResult(match.id)}
                    >
                      Guardar Resultado
                    </button>
                  )}
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
  );
}
