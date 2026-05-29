# API REST Usuarios, Productos y Autenticación — Modo Bare-Metal

La base de datos corre en Docker y la API se ejecuta nativamente en el host.

## 1. Levantar la base de datos

```bash
docker-compose up -d
```

## 2. Crear y activar el entorno virtual (Python 3.12)

```bash
python3.12 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 4. Ejecutar las pruebas

Las pruebas se ejecutan directamente en el host, con el entorno virtual activo:

```bash
python -m tests.test_connection
python -m tests.test_models
python -m tests.test_db
```

## 5. Levantar la API

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

> **Nota:** `--reload-dir app` limita el watcher de hot-reload al directorio `app/`.
> Sin este parámetro, watchfiles intentaría vigilar `.data/postgres/` (propiedad de
> root) y lanzaría un `PermissionError`.

## 6. Verificación final

Con la API corriendo, acceder a la interfaz de Swagger en:

```
http://localhost:8000/docs
```
