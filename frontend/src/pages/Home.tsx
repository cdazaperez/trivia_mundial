import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import Disclaimer from "../components/Disclaimer";

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="page home-page">
      <div className="hero">
        <h1>Trivia Mundial 2026 - Amigos</h1>
        <p className="subtitle">
          ¡Pronostica los resultados del Mundial FIFA 2026 y compite con tus amigos!
        </p>
        <p style={{ fontSize: "0.85rem", color: "#6b7280", marginTop: "0.25rem" }}>
          Plataforma de entretenimiento entre amigos. No es un sitio de apuestas profesional.
        </p>
      </div>

      <div className="home-grid">
        <Link to="/matches" className="home-card">
          <div className="card-icon">⚽</div>
          <h3>Pronosticar Partidos</h3>
          <p>Ingresa tus marcadores para cada partido de la fase de grupos</p>
        </Link>

        <Link to="/groups" className="home-card">
          <div className="card-icon">🏆</div>
          <h3>Clasificados por Grupo</h3>
          <p>Predice quién pasará 1ro y 2do en cada grupo</p>
        </Link>

        <Link to="/bonus" className="home-card">
          <div className="card-icon">⭐</div>
          <h3>Apuestas Bonus</h3>
          <p>Campeón, subcampeón, goleador y MVP</p>
        </Link>

        <Link to="/leaderboard" className="home-card">
          <div className="card-icon">📊</div>
          <h3>Tabla de Posiciones</h3>
          <p>Revisa quién va ganando en la trivia</p>
        </Link>

        <Link to="/predictions" className="home-card">
          <div className="card-icon">📋</div>
          <h3>Mis Pronósticos</h3>
          <p>Revisa todos tus pronósticos y puntos acumulados</p>
        </Link>
      </div>

      <div className="scoring-info">
        <h3>Sistema de Puntuación</h3>
        <table className="scoring-table">
          <tbody>
            <tr><td>Marcador exacto</td><td className="pts">+3 pts</td></tr>
            <tr><td>Resultado correcto (ganador/empate)</td><td className="pts">+1 pt</td></tr>
            <tr><td>Acertar ganador de penales (eliminatoria)</td><td className="pts">+1 pt</td></tr>
            <tr><td>Acertar clasificado de grupo (posición incorrecta)</td><td className="pts">+2 pts</td></tr>
            <tr><td>Acertar posición exacta en grupo (1ro o 2do)</td><td className="pts">+3 pts</td></tr>
            <tr><td>Acertar campeón</td><td className="pts">+10 pts</td></tr>
            <tr><td>Acertar subcampeón</td><td className="pts">+5 pts</td></tr>
            <tr><td>Acertar goleador</td><td className="pts">+5 pts</td></tr>
            <tr><td>Acertar MVP</td><td className="pts">+5 pts</td></tr>
          </tbody>
        </table>
      </div>

      <div className="rules-info">
        <h3>Reglas</h3>
        <ul>
          <li>Los pronósticos de marcadores se bloquean <strong>10 minutos antes</strong> de cada partido</li>
          <li>Los pronósticos de grupos se bloquean <strong>10 minutos antes</strong> del inicio del mundial</li>
          <li>Las apuestas bonus se pueden modificar hasta antes de la fase eliminatoria</li>
          <li>En eliminatorias se puede apostar en los nuevos partidos generados</li>
          <li>En eliminatorias, si pronosticas empate debes incluir <strong>resultado de penales</strong></li>
          <li>Los puntos se <strong>acumulan</strong> durante todo el mundial</li>
          <li>Los pronósticos de otros jugadores se ven después de que termine el partido</li>
        </ul>
      </div>

      <div className="rules-info">
        <h3>Premios</h3>
        <ul>
          <li>Los ganadores se definen al <strong>terminar el mundial</strong> (no por fase)</li>
          <li>Inscripción: <strong>$50.000 pesos</strong> por participante</li>
          <li>1er lugar: <strong>60%</strong> del pozo recaudado</li>
          <li>2do lugar: <strong>25%</strong> del pozo recaudado</li>
          <li>3er lugar: <strong>10%</strong> del pozo recaudado</li>
          <li>Administración: <strong>5%</strong> del pozo recaudado</li>
        </ul>
      </div>

      <Disclaimer />
    </div>
  );
}
