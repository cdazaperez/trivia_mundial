import { useState, useEffect } from "react";
import { getMyPredictions, getMyGroupPredictions, getMyBonusPredictions } from "../services/api";
import { Prediction, GroupPrediction, BonusPrediction } from "../types";

export default function Predictions() {
  const [matchPreds, setMatchPreds] = useState<Prediction[]>([]);
  const [groupPreds, setGroupPreds] = useState<GroupPrediction[]>([]);
  const [bonusPreds, setBonusPreds] = useState<BonusPrediction[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [mp, gp, bp] = await Promise.all([
        getMyPredictions(),
        getMyGroupPredictions(),
        getMyBonusPredictions(),
      ]);
      setMatchPreds(mp.data);
      setGroupPreds(gp.data);
      setBonusPreds(bp.data);
    } catch {
      // handle
    }
  };

  const totalPoints =
    matchPreds.reduce((sum, p) => sum + p.points_earned, 0) +
    groupPreds.reduce((sum, p) => sum + p.points_earned, 0) +
    bonusPreds.reduce((sum, p) => sum + p.points_earned, 0);

  return (
    <div className="page">
      <h2>Mis Pronósticos</h2>

      <div className="stats-summary">
        <div className="stat-card highlight">
          <h3>{totalPoints}</h3>
          <p>Puntos Totales</p>
        </div>
        <div className="stat-card">
          <h3>{matchPreds.length}</h3>
          <p>Partidos Pronosticados</p>
        </div>
        <div className="stat-card">
          <h3>{matchPreds.filter((p) => p.points_earned === 3).length}</h3>
          <p>Marcadores Exactos</p>
        </div>
        <div className="stat-card">
          <h3>{matchPreds.filter((p) => p.points_earned === 1).length}</h3>
          <p>Resultados Correctos</p>
        </div>
      </div>

      <h3>Pronósticos de Partidos</h3>
      <div className="predictions-list">
        {matchPreds.map((p) => (
          <div key={p.id} className={`pred-item ${p.points_earned > 0 ? "correct" : ""}`}>
            <span>
              {p.match?.home_team?.flag_emoji} {p.match?.home_team?.name} {p.home_score} - {p.away_score}{" "}
              {p.match?.away_team?.name} {p.match?.away_team?.flag_emoji}
            </span>
            {p.match?.is_finished && (
              <span className="result">
                Real: {p.match.home_score}-{p.match.away_score} |{" "}
                <strong>+{p.points_earned} pts</strong>
              </span>
            )}
          </div>
        ))}
        {matchPreds.length === 0 && <p className="empty">Aún no has hecho pronósticos de partidos</p>}
      </div>

      <h3>Pronósticos de Grupos</h3>
      <div className="predictions-list">
        {groupPreds.map((p) => (
          <div key={p.id} className="pred-item">
            <span>
              Grupo {p.group_name}: 1ro {p.first_place_team.flag_emoji} {p.first_place_team.name} | 2do{" "}
              {p.second_place_team.flag_emoji} {p.second_place_team.name}
            </span>
            {p.points_earned > 0 && <strong>+{p.points_earned} pts</strong>}
          </div>
        ))}
        {groupPreds.length === 0 && <p className="empty">Aún no has pronosticado clasificados</p>}
      </div>

      <h3>Apuestas Bonus</h3>
      <div className="predictions-list">
        {bonusPreds.map((p) => (
          <div key={p.id} className="pred-item">
            <span>
              {p.prediction_type === "champion" && "Campeón"}
              {p.prediction_type === "runner_up" && "Subcampeón"}
              {p.prediction_type === "top_scorer" && "Goleador"}
              {p.prediction_type === "mvp" && "MVP"}
              :{" "}
              {p.team ? `${p.team.flag_emoji} ${p.team.name}` : p.player_name}
            </span>
            {p.points_earned > 0 && <strong>+{p.points_earned} pts</strong>}
          </div>
        ))}
        {bonusPreds.length === 0 && <p className="empty">Aún no has hecho apuestas bonus</p>}
      </div>
    </div>
  );
}
