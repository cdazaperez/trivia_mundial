import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  getMatches,
  createPrediction,
  getMyPredictions,
  getGroupStandings,
} from "../services/api";
import { Match, Prediction } from "../types";

interface GroupStanding {
  team_id: number;
  team_name: string;
  team_code: string;
  team_flag: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
  position: number;
}

interface GroupData {
  group_name: string;
  standings: GroupStanding[];
}

export default function Today() {
  const [todayMatches, setTodayMatches] = useState<Match[]>([]);
  const [tomorrowMatches, setTomorrowMatches] = useState<Match[]>([]);
  const [predictions, setPredictions] = useState<Record<number, Prediction>>({});
  const [scores, setScores] = useState<
    Record<number, { home: string; away: string; homePen: string; awayPen: string }>
  >({});
  const [saving, setSaving] = useState<number | null>(null);
  const [msg, setMsg] = useState("");
  const [groups, setGroups] = useState<GroupData[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const toUTC = (d: string) =>
    d.endsWith("Z") || d.includes("+") ? d : d + "Z";

  const loadData = async () => {
    try {
      const [matchRes, predRes, standingsRes] = await Promise.all([
        getMatches(),
        getMyPredictions(),
        getGroupStandings(),
      ]);

      const allMatches: Match[] = matchRes.data;
      const now = new Date();
      const colombiaOffset = -5 * 60;
      const colombiaDate = new Date(now.getTime() + colombiaOffset * 60000);
      const todayStr = colombiaDate.toISOString().slice(0, 10);

      const tomorrow = new Date(colombiaDate);
      tomorrow.setDate(tomorrow.getDate() + 1);
      const tomorrowStr = tomorrow.toISOString().slice(0, 10);

      const getColombiaDate = (isoDate: string) => {
        const utc = new Date(toUTC(isoDate));
        const col = new Date(utc.getTime() + colombiaOffset * 60000);
        return col.toISOString().slice(0, 10);
      };

      const today = allMatches
        .filter((m) => getColombiaDate(m.match_date) === todayStr)
        .sort((a, b) => new Date(toUTC(a.match_date)).getTime() - new Date(toUTC(b.match_date)).getTime());

      const tmrw = allMatches
        .filter((m) => getColombiaDate(m.match_date) === tomorrowStr)
        .sort((a, b) => new Date(toUTC(a.match_date)).getTime() - new Date(toUTC(b.match_date)).getTime());

      setTodayMatches(today);
      setTomorrowMatches(tmrw);

      const predMap: Record<number, Prediction> = {};
      predRes.data.forEach((p: Prediction) => {
        predMap[p.match_id] = p;
      });
      setPredictions(predMap);

      const initScores: Record<number, { home: string; away: string; homePen: string; awayPen: string }> = {};
      [...today, ...tmrw].forEach((m) => {
        const pred = predMap[m.id];
        initScores[m.id] = {
          home: pred ? String(pred.home_score) : "",
          away: pred ? String(pred.away_score) : "",
          homePen: pred?.home_penalties != null ? String(pred.home_penalties) : "",
          awayPen: pred?.away_penalties != null ? String(pred.away_penalties) : "",
        };
      });
      setScores(initScores);

      setGroups(standingsRes.data);
    } catch {
      // handle silently
    }
  };

  const savePrediction = async (matchId: number) => {
    const s = scores[matchId];
    if (s.home === "" || s.away === "") return;

    const homeScore = parseInt(s.home);
    const awayScore = parseInt(s.away);
    const match = [...todayMatches, ...tomorrowMatches].find((m) => m.id === matchId);
    const isKnockout = match && match.phase !== "group";
    const isDraw = homeScore === awayScore;

    const payload: any = {
      match_id: matchId,
      home_score: homeScore,
      away_score: awayScore,
    };

    if (isKnockout && isDraw) {
      if (s.homePen === "" || s.awayPen === "") {
        setMsg("En eliminatoria con empate, debes ingresar los penales.");
        return;
      }
      payload.home_penalties = parseInt(s.homePen);
      payload.away_penalties = parseInt(s.awayPen);
    }

    setSaving(matchId);
    setMsg("");
    try {
      await createPrediction(payload);
      setMsg("Pronóstico guardado");
      loadData();
    } catch (err: any) {
      setMsg(err.response?.data?.detail || "Error al guardar");
    }
    setSaving(null);
  };

  const formatTime = (d: string) => {
    return new Date(toUTC(d)).toLocaleTimeString("es-CO", {
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "America/Bogota",
    });
  };

  const formatDateLabel = (d: string) => {
    return new Date(toUTC(d)).toLocaleDateString("es-CO", {
      weekday: "long",
      day: "numeric",
      month: "long",
      timeZone: "America/Bogota",
    });
  };

  const renderMatchCard = (match: Match) => {
    const pred = predictions[match.id];
    const s = scores[match.id] || { home: "", away: "", homePen: "", awayPen: "" };
    const matchTime = new Date(toUTC(match.match_date)).getTime();
    const now = Date.now();
    const isLocked = !match.is_finished && now >= matchTime - 10 * 60 * 1000;
    const hasPenalties = match.home_penalties != null && match.away_penalties != null;

    return (
      <div
        key={match.id}
        className={`match-card ${match.is_finished ? "finished" : ""} ${isLocked ? "locked" : ""}`}
      >
        <div className="match-date">
          <span className="match-number">#{match.match_number} </span>
          <span>Grupo {match.group_name} &middot; </span>
          {formatTime(match.match_date)}
          {match.venue && <span style={{ color: "#9ca3af" }}> &middot; {match.venue}</span>}
          {isLocked && !match.is_finished && (
            <span style={{ marginLeft: "0.5rem", color: "#dc2626", fontSize: "0.8rem" }}>
              Bloqueado
            </span>
          )}
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
              {hasPenalties && (
                <span style={{ fontSize: "0.75rem", color: "#6b7280" }}>
                  (Pen: {match.home_penalties}-{match.away_penalties})
                </span>
              )}
              {pred ? (
                <span className={`points ${pred.points_earned > 0 ? "earned" : ""}`}>
                  Tu pronóstico: {pred.home_score}-{pred.away_score}
                  {" "}({pred.points_earned} pts)
                </span>
              ) : (
                <span style={{ fontSize: "0.75rem", color: "#9ca3af", fontStyle: "italic" }}>
                  Sin pronóstico
                </span>
              )}
            </div>
          ) : isLocked ? (
            <div className="match-score-final">
              <span style={{ color: "#dc2626", fontSize: "0.85rem" }}>Cerrado</span>
              {pred && (
                <span className="points">
                  Tu pronóstico: {pred.home_score}-{pred.away_score}
                </span>
              )}
            </div>
          ) : (
            <div className="match-prediction-input">
              <input
                type="number" min="0" max="20" value={s.home}
                onChange={(e) => setScores({ ...scores, [match.id]: { ...s, home: e.target.value } })}
              />
              <span className="vs">-</span>
              <input
                type="number" min="0" max="20" value={s.away}
                onChange={(e) => setScores({ ...scores, [match.id]: { ...s, away: e.target.value } })}
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
      </div>
    );
  };

  const todayLabel = todayMatches.length > 0
    ? formatDateLabel(todayMatches[0].match_date)
    : "hoy";

  const tomorrowLabel = tomorrowMatches.length > 0
    ? formatDateLabel(tomorrowMatches[0].match_date)
    : "mañana";

  return (
    <div className="page">
      <h2>Partidos del Día</h2>
      <p className="hint">
        Partidos de hoy y mañana (hora Colombia). Para ver todos los partidos, ve a{" "}
        <Link to="/matches" style={{ color: "var(--primary)", fontWeight: 600 }}>Partidos</Link>.
      </p>

      {msg && <div className="success-msg">{msg}</div>}

      {/* Today's matches */}
      <div className="today-section">
        <h3 className="today-section-title">
          Hoy &middot; {todayLabel}
        </h3>
        {todayMatches.length === 0 ? (
          <p className="empty">No hay partidos hoy</p>
        ) : (
          <div className="matches-list">
            {todayMatches.map(renderMatchCard)}
          </div>
        )}
      </div>

      {/* Tomorrow's matches */}
      <div className="today-section" style={{ marginTop: "2rem" }}>
        <h3 className="today-section-title">
          Mañana &middot; {tomorrowLabel}
        </h3>
        {tomorrowMatches.length === 0 ? (
          <p className="empty">No hay partidos mañana</p>
        ) : (
          <div className="matches-list">
            {tomorrowMatches.map(renderMatchCard)}
          </div>
        )}
      </div>

      {/* Group standings */}
      <div style={{ marginTop: "2.5rem" }}>
        <h2 style={{ marginBottom: "0.5rem" }}>Tabla de Clasificación por Grupo</h2>
        <p className="hint">Posiciones actuales basadas en los resultados oficiales.</p>

        <div className="standings-grid">
          {groups.map((g) => (
            <div key={g.group_name} className="standings-card">
              <h4 className="standings-group-title">Grupo {g.group_name}</h4>
              <table className="standings-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Equipo</th>
                    <th>PJ</th>
                    <th>G</th>
                    <th>E</th>
                    <th>P</th>
                    <th>GF</th>
                    <th>GC</th>
                    <th>DG</th>
                    <th>Pts</th>
                  </tr>
                </thead>
                <tbody>
                  {g.standings.map((team, idx) => (
                    <tr key={team.team_id} className={idx < 2 ? "qualifier" : ""}>
                      <td className="pos">{team.position}</td>
                      <td className="team-cell">
                        <span className="team-flag-sm">{team.team_flag}</span>
                        <span className="team-code">{team.team_code}</span>
                      </td>
                      <td>{team.played}</td>
                      <td>{team.won}</td>
                      <td>{team.drawn}</td>
                      <td>{team.lost}</td>
                      <td>{team.goals_for}</td>
                      <td>{team.goals_against}</td>
                      <td>{team.goal_difference > 0 ? `+${team.goal_difference}` : team.goal_difference}</td>
                      <td className="pts-cell">{team.points}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
