import { useState, useEffect } from "react";
import { getTeams, createGroupPrediction, getMyGroupPredictions } from "../services/api";
import { Team, GroupPrediction } from "../types";

const GROUPS = ["A","B","C","D","E","F","G","H","I","J","K","L"];

export default function Groups() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [groupPreds, setGroupPreds] = useState<Record<string, GroupPrediction>>({});
  const [selections, setSelections] = useState<Record<string, { first: number; second: number }>>({});
  const [msg, setMsg] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [teamsRes, predsRes] = await Promise.all([
        getTeams(),
        getMyGroupPredictions(),
      ]);
      setTeams(teamsRes.data);

      const predMap: Record<string, GroupPrediction> = {};
      const selMap: Record<string, { first: number; second: number }> = {};

      predsRes.data.forEach((p: GroupPrediction) => {
        predMap[p.group_name] = p;
        selMap[p.group_name] = {
          first: p.first_place_team.id,
          second: p.second_place_team.id,
        };
      });
      setGroupPreds(predMap);
      setSelections(selMap);
    } catch {
      // handle silently
    }
  };

  const saveGroupPrediction = async (group: string) => {
    const sel = selections[group];
    if (!sel?.first || !sel?.second) {
      setMsg("Selecciona primero y segundo lugar");
      return;
    }
    if (sel.first === sel.second) {
      setMsg("Selecciona equipos diferentes");
      return;
    }

    try {
      await createGroupPrediction({
        group_name: group,
        first_place_team_id: sel.first,
        second_place_team_id: sel.second,
      });
      setMsg(`Pronóstico del Grupo ${group} guardado`);
      loadData();
    } catch (err: any) {
      setMsg(err.response?.data?.detail || "Error");
    }
  };

  const getGroupTeams = (group: string) => teams.filter((t) => t.group_name === group);

  return (
    <div className="page">
      <h2>Pronóstico de Clasificados por Grupo</h2>
      <p className="hint">Selecciona quién quedará 1ro y 2do en cada grupo</p>

      {msg && <div className="success-msg">{msg}</div>}

      <div className="groups-grid">
        {GROUPS.map((group) => {
          const groupTeams = getGroupTeams(group);
          const sel = selections[group] || { first: 0, second: 0 };
          const pred = groupPreds[group];

          return (
            <div key={group} className="group-card">
              <h3>Grupo {group}</h3>
              {pred && (
                <div className="existing-pred">
                  <small>
                    1ro: {pred.first_place_team.flag_emoji} {pred.first_place_team.name} |
                    2do: {pred.second_place_team.flag_emoji} {pred.second_place_team.name}
                    {pred.points_earned > 0 && ` (+${pred.points_earned} pts)`}
                  </small>
                </div>
              )}

              <div className="form-group">
                <label>1er Lugar</label>
                <select
                  value={sel.first}
                  onChange={(e) =>
                    setSelections({
                      ...selections,
                      [group]: { ...sel, first: Number(e.target.value) },
                    })
                  }
                >
                  <option value={0}>Seleccionar...</option>
                  {groupTeams.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.flag_emoji} {t.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>2do Lugar</label>
                <select
                  value={sel.second}
                  onChange={(e) =>
                    setSelections({
                      ...selections,
                      [group]: { ...sel, second: Number(e.target.value) },
                    })
                  }
                >
                  <option value={0}>Seleccionar...</option>
                  {groupTeams.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.flag_emoji} {t.name}
                    </option>
                  ))}
                </select>
              </div>

              <button
                className="btn btn-primary btn-sm"
                onClick={() => saveGroupPrediction(group)}
              >
                Guardar
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
