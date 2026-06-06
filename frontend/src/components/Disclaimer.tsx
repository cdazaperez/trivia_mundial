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
      <h4 style={{ color: "#374151", marginBottom: "0.75rem", fontSize: "0.9rem" }}>
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
