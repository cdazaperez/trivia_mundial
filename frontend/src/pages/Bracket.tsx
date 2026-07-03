import { useState, useEffect } from "react";
import { getMatches, getKnockoutStatus } from "../services/api";
import { Match } from "../types";

interface BracketMatch {
  matchNumber: number;
  home: string;
  homeFlag: string;
  away: string;
  awayFlag: string;
  homeScore: number | null;
  awayScore: number | null;
  homePen: number | null;
  awayPen: number | null;
  isFinished: boolean;
  winner: "home" | "away" | null;
}

const BRACKET_STRUCTURE = {
  upper: {
    r32: [
      { match: 74, feedsInto: 89 },
      { match: 77, feedsInto: 89 },
      { match: 73, feedsInto: 90 },
      { match: 75, feedsInto: 90 },
      { match: 83, feedsInto: 93 },
      { match: 84, feedsInto: 93 },
      { match: 81, feedsInto: 94 },
      { match: 82, feedsInto: 94 },
    ],
    r16: [
      { match: 89, feedsInto: 97 },
      { match: 90, feedsInto: 97 },
      { match: 93, feedsInto: 98 },
      { match: 94, feedsInto: 98 },
    ],
    qf: [
      { match: 97, feedsInto: 101 },
      { match: 98, feedsInto: 101 },
    ],
    sf: [{ match: 101 }],
  },
  lower: {
    r32: [
      { match: 76, feedsInto: 91 },
      { match: 78, feedsInto: 91 },
      { match: 79, feedsInto: 92 },
      { match: 80, feedsInto: 92 },
      { match: 86, feedsInto: 95 },
      { match: 88, feedsInto: 95 },
      { match: 85, feedsInto: 96 },
      { match: 87, feedsInto: 96 },
    ],
    r16: [
      { match: 91, feedsInto: 99 },
      { match: 92, feedsInto: 99 },
      { match: 95, feedsInto: 100 },
      { match: 96, feedsInto: 100 },
    ],
    qf: [
      { match: 99, feedsInto: 102 },
      { match: 100, feedsInto: 102 },
    ],
    sf: [{ match: 102 }],
  },
};

const PHASE_LABELS: Record<string, string> = {
  round_of_32: "32avos",
  round_of_16: "Octavos",
  quarter_final: "Cuartos",
  semi_final: "Semis",
  third_place: "3er Puesto",
  final: "Final",
};

function getWinner(m: BracketMatch): "home" | "away" | null {
  if (!m.isFinished) return null;
  if (m.homeScore! > m.awayScore!) return "home";
  if (m.awayScore! > m.homeScore!) return "away";
  if (m.homePen != null && m.awayPen != null) {
    if (m.homePen > m.awayPen) return "home";
    if (m.awayPen > m.homePen) return "away";
  }
  return null;
}

function MatchCard({ m }: { m: BracketMatch | null }) {
  if (!m) {
    return (
      <div className="bracket-match bracket-match-tbd">
        <div className="bracket-team">
          <span className="bracket-team-name">Por definir</span>
        </div>
        <div className="bracket-team">
          <span className="bracket-team-name">Por definir</span>
        </div>
      </div>
    );
  }

  const winner = getWinner(m);
  const hasPen = m.homePen != null && m.awayPen != null;

  return (
    <div className={`bracket-match ${m.isFinished ? "bracket-finished" : ""}`}>
      <div className="bracket-match-header">#{m.matchNumber}</div>
      <div className={`bracket-team ${winner === "home" ? "bracket-winner" : ""} ${winner === "away" ? "bracket-loser" : ""}`}>
        <span className="bracket-flag">{m.homeFlag || ""}</span>
        <span className="bracket-team-name">
          {m.home || "Por definir"}
        </span>
        {m.isFinished && (
          <span className="bracket-score">{m.homeScore}</span>
        )}
        {hasPen && winner === "home" && (
          <span className="bracket-pen">({m.homePen})</span>
        )}
      </div>
      <div className={`bracket-team ${winner === "away" ? "bracket-winner" : ""} ${winner === "home" ? "bracket-loser" : ""}`}>
        <span className="bracket-flag">{m.awayFlag || ""}</span>
        <span className="bracket-team-name">
          {m.away || "Por definir"}
        </span>
        {m.isFinished && (
          <span className="bracket-score">{m.awayScore}</span>
        )}
        {hasPen && winner === "away" && (
          <span className="bracket-pen">({m.awayPen})</span>
        )}
      </div>
    </div>
  );
}

export default function Bracket() {
  const [matchMap, setMatchMap] = useState<Record<number, BracketMatch>>({});
  const [loading, setLoading] = useState(true);
  const [hasKnockout, setHasKnockout] = useState(false);
  const [view, setView] = useState<"bracket" | "list">("bracket");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const statusRes = await getKnockoutStatus();
      const status = statusRes.data;
      const phases = ["round_of_32", "round_of_16", "quarter_final", "semi_final", "third_place", "final"];
      const existingPhases = phases.filter(p => status[p]?.exists);
      setHasKnockout(existingPhases.length > 0);

      if (existingPhases.length === 0) {
        setLoading(false);
        return;
      }

      const allMatches: Match[] = [];
      for (const phase of existingPhases) {
        const res = await getMatches({ phase });
        allMatches.push(...res.data);
      }

      const map: Record<number, BracketMatch> = {};
      for (const m of allMatches) {
        const bm: BracketMatch = {
          matchNumber: m.match_number,
          home: m.home_team?.name || "Por definir",
          homeFlag: m.home_team?.flag_emoji || "",
          away: m.away_team?.name || "Por definir",
          awayFlag: m.away_team?.flag_emoji || "",
          homeScore: m.home_score,
          awayScore: m.away_score,
          homePen: m.home_penalties,
          awayPen: m.away_penalties,
          isFinished: m.is_finished,
          winner: null,
        };
        bm.winner = getWinner(bm);
        map[m.match_number] = bm;
      }
      setMatchMap(map);
    } catch {
      // handle silently
    }
    setLoading(false);
  };

  if (loading) return <div className="loading">Cargando...</div>;

  if (!hasKnockout) {
    return (
      <div className="page">
        <h2>Llaves del Mundial</h2>
        <div className="empty">
          Las llaves se generan cuando finaliza la fase de grupos.
        </div>
      </div>
    );
  }

  const finalMatch = matchMap[104] || null;
  const thirdPlaceMatch = matchMap[103] || null;

  const renderBracketColumn = (
    matches: { match: number }[],
    label: string,
  ) => (
    <div className="bracket-column">
      <div className="bracket-column-header">{label}</div>
      <div className="bracket-column-matches">
        {matches.map((entry) => (
          <MatchCard
            key={entry.match}
            m={matchMap[entry.match] || null}
          />
        ))}
      </div>
    </div>
  );

  const renderHalfBracket = (
    half: typeof BRACKET_STRUCTURE.upper,
    title: string,
  ) => (
    <div className="bracket-half">
      <h3 className="bracket-half-title">{title}</h3>
      <div className="bracket-flow">
        {renderBracketColumn(half.r32, "32avos")}
        <div className="bracket-connector" />
        {renderBracketColumn(half.r16, "Octavos")}
        <div className="bracket-connector" />
        {renderBracketColumn(half.qf, "Cuartos")}
        <div className="bracket-connector" />
        {renderBracketColumn(half.sf, "Semis")}
      </div>
    </div>
  );

  const renderListView = () => {
    const phases = [
      { key: "round_of_32", numbers: [73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88] },
      { key: "round_of_16", numbers: [89,90,91,92,93,94,95,96] },
      { key: "quarter_final", numbers: [97,98,99,100] },
      { key: "semi_final", numbers: [101,102] },
      { key: "third_place", numbers: [103] },
      { key: "final", numbers: [104] },
    ];

    return (
      <div className="bracket-list-view">
        {phases.map(phase => {
          const phaseMatches = phase.numbers
            .map(n => matchMap[n])
            .filter(Boolean);
          if (phaseMatches.length === 0) return null;
          return (
            <div key={phase.key} className="bracket-list-phase">
              <h3>{PHASE_LABELS[phase.key]}</h3>
              <div className="bracket-list-matches">
                {phaseMatches.map(m => (
                  <MatchCard key={m.matchNumber} m={m} />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="page">
      <h2>Llaves del Mundial</h2>
      <p className="hint">Avance del cuadro eliminatorio con resultados en vivo</p>

      <div className="phase-tabs" style={{ marginBottom: "1rem" }}>
        <button
          className={`tab ${view === "bracket" ? "active" : ""}`}
          onClick={() => setView("bracket")}
        >
          Vista Cuadro
        </button>
        <button
          className={`tab ${view === "list" ? "active" : ""}`}
          onClick={() => setView("list")}
        >
          Vista Lista
        </button>
      </div>

      {view === "list" ? (
        renderListView()
      ) : (
        <div className="bracket-container">
          {renderHalfBracket(BRACKET_STRUCTURE.upper, "Cuadro Superior")}

          {(finalMatch || thirdPlaceMatch) && (
            <div className="bracket-finals">
              {finalMatch && (
                <div className="bracket-final-section">
                  <h3 className="bracket-half-title">Final</h3>
                  <MatchCard m={finalMatch} />
                </div>
              )}
              {thirdPlaceMatch && (
                <div className="bracket-final-section">
                  <h3 className="bracket-half-title">Tercer Puesto</h3>
                  <MatchCard m={thirdPlaceMatch} />
                </div>
              )}
            </div>
          )}

          {renderHalfBracket(BRACKET_STRUCTURE.lower, "Cuadro Inferior")}
        </div>
      )}
    </div>
  );
}
