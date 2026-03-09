# FitHealth Backend

API REST desarrollada con **FastAPI + SQLAlchemy + PostgreSQL**.

## Arrancar el proyecto

```bash
cp .env.example .env
docker compose up --build
```

Swagger UI disponible en: `http://localhost:8000/docs`

---

## Probar con cURL

### Health check

```bash
curl http://localhost:8000/health
```

---

### Usuarios

**Crear usuario**
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "username": "alice", "password": "secret123"}'
```

**Listar usuarios**
```bash
curl http://localhost:8000/users/
```

**Obtener usuario por ID**
```bash
curl http://localhost:8000/users/1
```

**Actualizar usuario**
```bash
curl -X PATCH http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"username": "alice_updated"}'
```

**Eliminar usuario**
```bash
curl -X DELETE http://localhost:8000/users/1
```

---

### Entrenamientos

**Crear entrenamiento** (para el usuario con id=1)
```bash
curl -X POST http://localhost:8000/workouts/user/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Cardio matutino", "description": "Correr 5km", "duration_minutes": 30, "calories_burned": 300}'
```

**Listar entrenamientos de un usuario**
```bash
curl http://localhost:8000/workouts/user/1
```

**Obtener entrenamiento por ID**
```bash
curl http://localhost:8000/workouts/1
```

**Actualizar entrenamiento**
```bash
curl -X PATCH http://localhost:8000/workouts/1 \
  -H "Content-Type: application/json" \
  -d '{"duration_minutes": 45, "calories_burned": 420}'
```

**Eliminar entrenamiento**
```bash
curl -X DELETE http://localhost:8000/workouts/1
```

---

## Estructura del proyecto

```
Backend/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── app/
    ├── main.py          # Punto de entrada FastAPI
    ├── config.py        # Variables de entorno
    ├── database.py      # Conexión SQLAlchemy
    ├── models/          # Tablas de la BD
    │   ├── user.py
    │   └── workout.py
    ├── schemas/         # Validación con Pydantic
    │   ├── user.py
    │   └── workout.py
    ├── crud/            # Lógica de acceso a datos
    │   ├── user.py
    │   └── workout.py
    └── routers/         # Endpoints HTTP
        ├── users.py
        └── workouts.py
```

## Variables de entorno

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `POSTGRES_USER` | Usuario de PostgreSQL | `fithealth` |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL | `changeme` |
| `POSTGRES_DB` | Nombre de la base de datos | `fithealth_db` |
| `DATABASE_URL` | URL de conexión SQLAlchemy | *(construida con las anteriores)* |
