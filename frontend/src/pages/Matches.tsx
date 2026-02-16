import { useState, useEffect } from "react";
import { getMatches, createPrediction, getMyPredictions } from "../services/api";
import { Match, Prediction } from "../types";

const GROUPS = ["A","B","C","D","E","F","G","H","I","J","K","L"];

export default function Matches() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [predictions, setPredictions] = useState<Record<number, Prediction>>({});
  const [selectedGroup, setSelectedGroup] = useState<string>("A");
  const [scores, setScores] = useState<Record<number, { home: string; away: string }>>({});
  const [saving, setSaving] = useState<number | null>(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    loadData();
  }, [selectedGroup]);

  const loadData = async () => {
    try {
      const [matchRes, predRes] = await Promise.all([
        getMatches({ group: selectedGroup, phase: "group" }),
        getMyPredictions("group"),
      ]);
      setMatches(matchRes.data);
      const predMap: Record<number, Prediction> = {};
      predRes.data.forEach((p: Prediction) => {
        predMap[p.match_id] = p;
      });
      setPredictions(predMap);

      const initScores: Record<number, { home: string; away: string }> = {};
      matchRes.data.forEach((m: Match) => {
        const pred = predMap[m.id];
        initScores[m.id] = {
          home: pred ? String(pred.home_score) : "",
          away: pred ? String(pred.away_score) : "",
        };
      });
      setScores(initScores);
    } catch {
      // handle silently
    }
  };

  const savePrediction = async (matchId: number) => {
    const s = scores[matchId];
    if (s.home === "" || s.away === "") return;

    setSaving(matchId);
    setMsg("");
    try {
      await createPrediction({
        match_id: matchId,
        home_score: parseInt(s.home),
        away_score: parseInt(s.away),
      });
      setMsg("Pronóstico guardado");
      loadData();
    } catch (err: any) {
      setMsg(err.response?.data?.detail || "Error al guardar");
    }
    setSaving(null);
  };

  const formatDate = (d: string) => {
    return new Date(d).toLocaleDateString("es", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="page">
      <h2>Partidos - Fase de Grupos</h2>

      <div className="group-tabs">
        {GROUPS.map((g) => (
          <button
            key={g}
            className={`tab ${selectedGroup === g ? "active" : ""}`}
            onClick={() => setSelectedGroup(g)}
          >
            Grupo {g}
          </button>
        ))}
      </div>

      {msg && <div className="success-msg">{msg}</div>}

      <div className="matches-list">
        {matches.map((match) => {
          const pred = predictions[match.id];
          const s = scores[match.id] || { home: "", away: "" };

          return (
            <div
              key={match.id}
              className={`match-card ${match.is_finished ? "finished" : ""}`}
            >
              <div className="match-date">{formatDate(match.match_date)}</div>
              <div className="match-teams">
                <div className="team home">
                  <span className="flag">{match.home_team?.flag_emoji}</span>
                  <span className="name">{match.home_team?.name}</span>
                </div>

                {match.is_finished ? (
                  <div className="match-score-final">
                    <span className="score">
                      {match.home_score} - {match.away_score}
                    </span>
                    {pred && (
                      <span className={`points ${pred.points_earned > 0 ? "earned" : ""}`}>
                        Tu pronóstico: {pred.home_score}-{pred.away_score} ({pred.points_earned} pts)
                      </span>
                    )}
                  </div>
                ) : (
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
                      className="btn btn-sm btn-primary"
                      onClick={() => savePrediction(match.id)}
                      disabled={saving === match.id}
                    >
                      {pred ? "Actualizar" : "Guardar"}
                    </button>
                  </div>
                )}

                <div className="team away">
                  <span className="name">{match.away_team?.name}</span>
                  <span className="flag">{match.away_team?.flag_emoji}</span>
                </div>
              </div>
              {match.venue && (
                <div className="match-venue">{match.venue}</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
