# Cómo funciona (guía para explicarlo en una entrevista)

## El recorrido de un request
1. Llega `POST /tasks` a `main.py`.
2. FastAPI valida el JSON con `TaskCreate` (`schemas.py`). Si algo está mal devuelve **422** sin tocar la base.
3. `Depends(get_db)` abre una sesión de base de datos y la cierra al terminar.
4. `crud.create_task` guarda la tarea y la devuelve.
5. FastAPI la convierte en JSON con `TaskOut` y responde **201**.

## Decisiones que te pueden preguntar
- **¿Por qué separar `main.py` y `crud.py`?** `main.py` sabe de HTTP (códigos, 404). `crud.py` solo sabe de la base. Así cada parte se prueba y se cambia por separado.
- **¿Por qué PATCH y no PUT?** PATCH cambia solo lo que mandás. Se logra con `model_dump(exclude_unset=True)`.
- **¿Por qué `/tasks/stats` está antes que `/tasks/{task_id}`?** FastAPI evalúa las rutas en orden. Si estuviera después, "stats" se interpretaría como un id y daría 422.
- **¿Cómo aislás los tests?** Cada test usa una base SQLite en memoria nueva y reemplazo la dependencia `get_db` con `app.dependency_overrides`.
- **¿Qué es la "cobertura"?** El porcentaje de líneas que ejecutan los tests. El CI falla si baja de 90%.
- **¿Por qué una fecha vencida se rechaza al crear pero no al editar?** Regla de negocio: no tiene sentido crear algo ya vencido, pero sí reprogramar. Está documentado en el test de stats.

## Para practicar
- Agregá un campo `tags` y escribí sus tests antes del código (TDD).
- Cambiá SQLite por PostgreSQL con `DATABASE_URL` y un `docker-compose.yml`.
