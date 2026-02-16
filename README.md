# Trivia Mundial 2026

Aplicacion de pronosticos para el Mundial de Futbol FIFA 2026. Compite con tus amigos pronosticando marcadores, clasificados y mas.

## Stack

- **Backend**: Python + FastAPI + SQLAlchemy + SQLite
- **Frontend**: React + TypeScript + Vite

## Inicio Rapido

```bash
# 1. Instalar dependencias del backend
cd backend
pip install -r requirements.txt

# 2. Instalar dependencias del frontend
cd ../frontend
npm install

# 3. Iniciar ambos servicios
cd ..
./start.sh
```

- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

## Sistema de Puntuacion

| Acierto | Puntos |
|---------|--------|
| Marcador exacto | 3 pts |
| Resultado correcto (ganador/empate) | 1 pt |
| Acertar clasificado de grupo | 2 pts |
| Acertar 1ro del grupo | 3 pts |
| Acertar campeon | 10 pts |
| Acertar subcampeon | 5 pts |
| Acertar goleador | 5 pts |
| Acertar MVP | 5 pts |

## Reglas

- Los pronosticos de marcadores se bloquean 1 hora antes de cada partido
- Las apuestas bonus (campeon, subcampeon, goleador, MVP) se bloquean 24 horas antes del mundial
- Ganan los 2 primeros en puntos al terminar la fase de grupos
- En eliminatorias se puede volver a apostar
- Los pronosticos de otros jugadores se ven despues de que termine el partido

## Funcionalidades

- Autenticacion con JWT (registro/login)
- Pronostico de marcadores para todos los partidos
- Pronostico de clasificados por grupo (1ro y 2do)
- Apuestas bonus: campeon, subcampeon, goleador, MVP
- Tabla de posiciones general y por fase
- Panel de administracion para ingresar resultados reales
- Calculo automatico de puntos
- Responsive (funciona en movil)

## Primer Usuario Admin

El primer usuario registrado puede ser promovido a admin manualmente:

```bash
cd backend
python3 -c "
from app.models.user import User
from app.core.database import SessionLocal
db = SessionLocal()
user = db.query(User).first()
if user:
    user.is_admin = True
    db.commit()
    print(f'{user.username} es ahora admin')
"
```
