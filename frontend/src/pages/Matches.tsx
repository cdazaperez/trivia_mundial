import { useState, useEffect } from "react";
import {
  getMatches,
  createPrediction,
  getMyPredictions,
  getKnockoutStatus,
} from "../services/api";
import { Match, Prediction } from "../types";

const GROUPS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"];

const PHASE_TABS = [
  { key: "group", label: "Fase de Grupos" },
  { key: "round_of_32", label: "32avos" },
  { key: "round_of_16", label: "Octavos" },
  { key: "quarter_final", label: "Cuartos" },
  { key: "semi_final", label: "Semis" },
  { key: "third_place", label: "3er Puesto" },
  { key: "final", label: "Final" },
];

export default function Matches() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [predictions, setPredictions] = useState<Record<number, Prediction>>(
    {}
  );
  const [selectedPhase, setSelectedPhase] = useState<string>("group");
  const [selectedGroup, setSelectedGroup] = useState<string>("A");
  const [scores, setScores] = useState<
    Record<number, { home: string; away: string }>
  >({});
  const [saving, setSaving] = useState<number | null>(null);
  const [msg, setMsg] = useState("");
  const [availablePhases, setAvailablePhases] = useState<string[]>(["group"]);

  useEffect(() => {
    loadKnockoutStatus();
  }, []);

  useEffect(() => {
    loadData();
  }, [selectedPhase, selectedGroup]);

  const loadKnockoutStatus = async () => {
    try {
      const res = await getKnockoutStatus();
      const status = res.data;
      const phases = ["group"];
      if (status.round_of_32?.exists) phases.push("round_of_32");
      if (status.round_of_16?.exists) phases.push("round_of_16");
      if (status.quarter_final?.exists) phases.push("quarter_final");
      if (status.semi_final?.exists) phases.push("semi_final");
      if (status.third_place?.exists) phases.push("third_place");
      if (status.final?.exists) phases.push("final");
      setAvailablePhases(phases);
    } catch {
      // fallback
    }
  };

  const loadData = async () => {
    try {
      const params: any =
        selectedPhase === "group"
          ? { group: selectedGroup, phase: "group" }
          : { phase: selectedPhase };

      const [matchRes, predRes] = await Promise.all([
        getMatches(params),
        getMyPredictions(selectedPhase),
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
      setMsg("Pronostico guardado");
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

  const phaseLabel =
    PHASE_TABS.find((p) => p.key === selectedPhase)?.label || "Partidos";

  return (
    <div className="page">
      <h2>Partidos</h2>

      {/* Phase tabs */}
      <div className="phase-tabs">
        {PHASE_TABS.filter((p) => availablePhases.includes(p.key)).map((p) => (
          <button
            key={p.key}
            className={`tab ${selectedPhase === p.key ? "active" : ""}`}
            onClick={() => setSelectedPhase(p.key)}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Group sub-tabs (only for group phase) */}
      {selectedPhase === "group" && (
        <div className="group-tabs">
          {GROUPS.map((g) => (
            <button
              key={g}
              className={`tab tab-sm ${selectedGroup === g ? "active" : ""}`}
              onClick={() => setSelectedGroup(g)}
            >
              {g}
            </button>
          ))}
        </div>
      )}

      {msg && <div className="success-msg">{msg}</div>}

      {/* Knockout info banner */}
      {selectedPhase === "group" && availablePhases.length === 1 && (
        <div className="info-banner" style={{
          background: "#eef2ff",
          border: "1px solid #c7d2fe",
          borderRadius: "8px",
          padding: "0.75rem 1rem",
          marginBottom: "1rem",
          fontSize: "0.9rem",
          color: "#4338ca",
        }}>
          Las fases eliminatorias (32avos, octavos, etc.) se habilitan una vez que termine la fase de grupos.
          Cuando se generen, aparecerán nuevas pestañas arriba para pronosticar esos partidos.
        </div>
      )}

      {selectedPhase !== "group" && (
        <div className="info-banner" style={{
          background: "#f0fdf4",
          border: "1px solid #bbf7d0",
          borderRadius: "8px",
          padding: "0.75rem 1rem",
          marginBottom: "1rem",
          fontSize: "0.9rem",
          color: "#166534",
        }}>
          Ingresa tus marcadores para cada partido de {phaseLabel}. Se bloquean 1 hora antes de cada partido.
        </div>
      )}

      {matches.length === 0 && (
        <p className="hint" style={{ textAlign: "center", marginTop: "2rem" }}>
          No hay partidos disponibles para {phaseLabel}.
        </p>
      )}

      <div className="matches-list">
        {matches.map((match) => {
          const pred = predictions[match.id];
          const s = scores[match.id] || { home: "", away: "" };

          return (
            <div
              key={match.id}
              className={`match-card ${match.is_finished ? "finished" : ""}`}
            >
              <div className="match-date">
                <span className="match-number">#{match.match_number} </span>
                {selectedPhase === "group" && (
                  <span>Grupo {match.group_name} &middot; </span>
                )}
                {formatDate(match.match_date)}
              </div>
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
                      <span
                        className={`points ${pred.points_earned > 0 ? "earned" : ""}`}
                      >
                        Tu pronostico: {pred.home_score}-{pred.away_score} (
                        {pred.points_earned} pts)
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
