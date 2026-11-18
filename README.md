# API de gestión de tareas

![CI](https://github.com/Drabenq/task-manager-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)

API REST para crear, filtrar y seguir tareas. Hecha con **FastAPI**, **SQLAlchemy 2.0** y **Pydantic v2**,
con tests en **pytest** que exigen 90 % de cobertura, y empaquetada como imagen de **Docker** que el CI prueba
en cada push.

## Funcionalidades

- CRUD completo de tareas con actualización parcial (`PATCH` solo cambia los campos que mandás)
- Filtros por estado y prioridad, búsqueda sin distinguir mayúsculas y paginación
- Endpoint `/tasks/stats` con cantidad de tareas por estado y tareas vencidas
- Validaciones: títulos vacíos, largos máximos, valores inválidos y fechas límite pasadas devuelven `422`
- Documentación interactiva en `/docs` (Swagger UI), generada a partir del código

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/tasks` | Crear una tarea |
| `GET` | `/tasks?status=&priority=&q=&skip=&limit=` | Listar y filtrar tareas |
| `GET` | `/tasks/stats` | Cantidades por estado y tareas vencidas |
| `GET` | `/tasks/{id}` | Ver una tarea |
| `PATCH` | `/tasks/{id}` | Modificar algunos campos |
| `DELETE` | `/tasks/{id}` | Borrar una tarea |

## Correrlo

```bash
python -m venv .venv && source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Abrí http://localhost:8000/docs

Con Docker:

```bash
docker build -t task-manager-api .
docker run -p 8000:8000 task-manager-api
```

## Tests

```bash
pytest
```

Cada test corre contra su propia base SQLite en memoria (`tests/conftest.py`), así que los tests están aislados
y se pueden correr en cualquier orden. Cubren los casos felices, errores de validación (parametrizados), 404,
filtros, paginación y la lógica de estadísticas.

## Estructura

```
app/
  main.py       # rutas y lo que es HTTP (códigos de estado, 404)
  crud.py       # consultas a la base, sin nada de HTTP
  schemas.py    # modelos de entrada/salida y reglas de validación
  models.py     # definición de la tabla con SQLAlchemy
  database.py   # engine, sesión y la dependencia get_db
tests/          # tests con pytest
```

Explicación más detallada, con preguntas típicas de entrevista: [docs/como-funciona.md](docs/como-funciona.md).

## CI

GitHub Actions corre los tests con cobertura, después arma la imagen de Docker, levanta el contenedor y
chequea `/health`.
