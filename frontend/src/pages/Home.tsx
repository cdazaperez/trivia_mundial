import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="page home-page">
      <div className="hero">
        <h1>Trivia Mundial 2026</h1>
        <p className="subtitle">
          ¡Pronostica los resultados del Mundial FIFA 2026 y compite con tus amigos!
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
            <tr><td>Acertar clasificado de grupo</td><td className="pts">+2 pts</td></tr>
            <tr><td>Acertar 1ro del grupo</td><td className="pts">+3 pts</td></tr>
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
          <li>Los pronósticos de marcadores se bloquean 1 hora antes de cada partido</li>
          <li>Las apuestas bonus se bloquean 24 horas antes del inicio del mundial</li>
          <li>Ganan los <strong>2 primeros</strong> en puntos al terminar la fase de grupos</li>
          <li>En eliminatorias se puede volver a apostar, gana el que más puntos sume</li>
          <li>Los pronósticos de otros jugadores se ven después de que termine el partido</li>
        </ul>
      </div>
    </div>
  );
}
