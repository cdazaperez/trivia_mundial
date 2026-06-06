export default function Disclaimer() {
  return (
    <div className="disclaimer-section" style={{
      marginTop: "2rem",
      padding: "1.25rem",
      background: "#f9fafb",
      border: "1px solid #e5e7eb",
      borderRadius: "8px",
      fontSize: "0.8rem",
      color: "#6b7280",
      lineHeight: "1.6",
    }}>
      {/* Scoring */}
      <h4 style={{ color: "#374151", marginBottom: "0.5rem", fontSize: "0.9rem" }}>
        Sistema de Puntuación
      </h4>
      <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: "1rem" }}>
        <tbody>
          {[
            ["Marcador exacto", "+3 pts"],
            ["Resultado correcto (ganador/empate)", "+1 pt"],
            ["Acertar ganador de penales (eliminatoria)", "+1 pt"],
            ["Acertar posición exacta en grupo (1ro o 2do)", "+3 pts"],
            ["Acertar clasificado de grupo (posición incorrecta)", "+2 pts"],
            ["Acertar campeón", "+10 pts"],
            ["Acertar subcampeón", "+5 pts"],
            ["Acertar goleador", "+5 pts"],
            ["Acertar MVP", "+5 pts"],
          ].map(([label, pts]) => (
            <tr key={label}>
              <td style={{ padding: "0.3rem 0", borderBottom: "1px solid #e5e7eb" }}>{label}</td>
              <td style={{
                padding: "0.3rem 0",
                borderBottom: "1px solid #e5e7eb",
                textAlign: "right",
                fontWeight: 700,
                color: "#1a472a",
                whiteSpace: "nowrap",
              }}>{pts}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Rules */}
      <h4 style={{ color: "#374151", marginBottom: "0.5rem", fontSize: "0.9rem" }}>
        Reglas
      </h4>
      <ul style={{ paddingLeft: "1.25rem", margin: "0 0 1rem 0" }}>
        <li style={{ marginBottom: "0.35rem" }}>Los pronósticos de marcadores se bloquean <strong>10 minutos antes</strong> de cada partido</li>
        <li style={{ marginBottom: "0.35rem" }}>Los pronósticos de grupos se bloquean <strong>10 minutos antes</strong> del inicio del mundial</li>
        <li style={{ marginBottom: "0.35rem" }}>Las apuestas bonus se pueden modificar hasta antes de la fase eliminatoria</li>
        <li style={{ marginBottom: "0.35rem" }}>En eliminatorias se puede apostar en los nuevos partidos generados</li>
        <li style={{ marginBottom: "0.35rem" }}>En eliminatorias, si pronosticas empate debes incluir <strong>resultado de penales</strong></li>
        <li style={{ marginBottom: "0.35rem" }}>Los puntos se <strong>acumulan</strong> durante todo el mundial</li>
        <li style={{ marginBottom: "0.35rem" }}>Los pronósticos de otros jugadores se ven después de que termine el partido</li>
      </ul>

      {/* Prizes */}
      <h4 style={{ color: "#374151", marginBottom: "0.5rem", fontSize: "0.9rem" }}>
        Premios
      </h4>
      <ul style={{ paddingLeft: "1.25rem", margin: "0 0 1rem 0" }}>
        <li style={{ marginBottom: "0.35rem" }}>Los ganadores se definen al <strong>terminar el mundial</strong></li>
        <li style={{ marginBottom: "0.35rem" }}>Inscripción: <strong>$50.000 pesos</strong> por participante</li>
        <li style={{ marginBottom: "0.35rem" }}>1er lugar: <strong>60%</strong> del pozo recaudado</li>
        <li style={{ marginBottom: "0.35rem" }}>2do lugar: <strong>25%</strong> del pozo recaudado</li>
        <li style={{ marginBottom: "0.35rem" }}>3er lugar: <strong>10%</strong> del pozo recaudado</li>
        <li style={{ marginBottom: "0.35rem" }}>Administración: <strong>5%</strong> del pozo recaudado</li>
      </ul>

      {/* Legal */}
      <h4 style={{ color: "#374151", marginBottom: "0.5rem", fontSize: "0.9rem" }}>
        Aviso Legal y Condiciones de Participación
      </h4>
      <p style={{ marginBottom: "0.5rem" }}>
        Esta plataforma es con fines de <strong>entretenimiento entre amigos</strong>. No constituye un sitio de apuestas profesional ni está regulada como tal.
      </p>
      <ul style={{ paddingLeft: "1.25rem", margin: "0.5rem 0" }}>
        <li style={{ marginBottom: "0.4rem" }}>
          La plataforma se reserva el derecho de <strong>bloquear cuentas y retener premios</strong> si se detecta fraude, suplantación de identidad o uso de múltiples cuentas para manipular el concurso.
        </li>
        <li style={{ marginBottom: "0.4rem" }}>
          El pago de la inscripción (<strong>$50.000 pesos</strong>) es definitivo. <strong>No se realizarán reembolsos</strong> bajo ninguna circunstancia una vez que el usuario haya ingresado sus predicciones y el torneo o partido haya comenzado.
        </li>
        <li style={{ marginBottom: "0.4rem" }}>
          El pago debe realizarse por <strong>Nequi</strong> al número <strong>3107789035</strong> o con la llave <strong>@NEQUIHER215</strong>, a más tardar <strong>un día antes del inicio del mundial (10 de junio de 2026)</strong>. Sin pago confirmado no se habilitará la participación.
        </li>
        <li style={{ marginBottom: "0.4rem" }}>
          Los resultados válidos para calcular los puntajes serán única y exclusivamente los publicados por la entidad oficial organizadora del evento (<strong>FIFA</strong>).
        </li>
        <li style={{ marginBottom: "0.4rem" }}>
          La plataforma <strong>no se hace responsable</strong> si un usuario no puede ingresar sus predicciones a tiempo debido a fallas en su conexión a internet o caídas temporales del servidor. Las predicciones tienen una <strong>hora de cierre estricta</strong>.
        </li>
      </ul>
    </div>
  );
}
