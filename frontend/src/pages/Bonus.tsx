import { useState, useEffect } from "react";
import {
  getTeams,
  createBonusPrediction,
  getMyBonusPredictions,
} from "../services/api";
import { Team, BonusPrediction } from "../types";

const BONUS_TYPES = [
  { key: "champion", label: "Campeón", type: "team" },
  { key: "runner_up", label: "Subcampeón", type: "team" },
  { key: "top_scorer", label: "Goleador del Torneo", type: "player" },
  { key: "mvp", label: "MVP del Torneo", type: "player" },
];

const POINTS_MAP: Record<string, number> = {
  champion: 10,
  runner_up: 5,
  top_scorer: 5,
  mvp: 5,
};

export default function Bonus() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [bonusPreds, setBonusPreds] = useState<Record<string, BonusPrediction>>({});
  const [formData, setFormData] = useState<Record<string, { team_id: number; player_name: string }>>({});
  const [msg, setMsg] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [teamsRes, predsRes] = await Promise.all([
        getTeams(),
        getMyBonusPredictions(),
      ]);
      setTeams(teamsRes.data);

      const predMap: Record<string, BonusPrediction> = {};
      const formMap: Record<string, { team_id: number; player_name: string }> = {};

      predsRes.data.forEach((p: BonusPrediction) => {
        predMap[p.prediction_type] = p;
        formMap[p.prediction_type] = {
          team_id: p.team?.id || 0,
          player_name: p.player_name || "",
        };
      });
      setBonusPreds(predMap);
      setFormData(formMap);
    } catch {
      // handle
    }
  };

  const saveBonusPrediction = async (type: string) => {
    const data = formData[type];
    const bonusType = BONUS_TYPES.find((b) => b.key === type);
    if (!bonusType) return;

    try {
      if (bonusType.type === "team") {
        await createBonusPrediction({
          prediction_type: type,
          team_id: data?.team_id || undefined,
        });
      } else {
        await createBonusPrediction({
          prediction_type: type,
          player_name: data?.player_name || undefined,
        });
      }
      setMsg(`Apuesta "${bonusType.label}" guardada`);
      loadData();
    } catch (err: any) {
      setMsg(err.response?.data?.detail || "Error");
    }
  };

  return (
    <div className="page">
      <h2>Apuestas Bonus</h2>
      <p className="hint">
        Apuestas adicionales con puntos extra. Se bloquean 24 horas antes del mundial.
      </p>

      {msg && <div className="success-msg">{msg}</div>}

      <div className="bonus-grid">
        {BONUS_TYPES.map((bonus) => {
          const pred = bonusPreds[bonus.key];
          const data = formData[bonus.key] || { team_id: 0, player_name: "" };

          return (
            <div key={bonus.key} className="bonus-card">
              <h3>
                {bonus.label}{" "}
                <span className="points-badge">+{POINTS_MAP[bonus.key]} pts</span>
              </h3>

              {pred && (
                <div className="existing-pred">
                  <small>
                    Actual: {pred.team ? `${pred.team.flag_emoji} ${pred.team.name}` : pred.player_name}
                    {pred.points_earned > 0 && ` (+${pred.points_earned} pts)`}
                  </small>
                </div>
              )}

              {bonus.type === "team" ? (
                <div className="form-group">
                  <select
                    value={data.team_id}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        [bonus.key]: { ...data, team_id: Number(e.target.value) },
                      })
                    }
                  >
                    <option value={0}>Seleccionar equipo...</option>
                    {teams.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.flag_emoji} {t.name}
                      </option>
                    ))}
                  </select>
                </div>
              ) : (
                <div className="form-group">
                  <input
                    type="text"
                    placeholder="Nombre del jugador"
                    value={data.player_name}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        [bonus.key]: { ...data, player_name: e.target.value },
                      })
                    }
                  />
                </div>
              )}

              <button
                className="btn btn-primary btn-sm"
                onClick={() => saveBonusPrediction(bonus.key)}
              >
                {pred ? "Actualizar" : "Guardar"}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
