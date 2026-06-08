# ParteAdmin

Un módulo administrativo (frontend + backend) para el parcial. Esta carpeta contiene una API en Python (FastAPI) y la UI administrativa (React/Vite).

Resumen rápido
- **Backend:** servicio FastAPI en `backend/`.
- **Frontend:** aplicación React en `Frontend/`.

Requisitos
- Python 3.10+ (recomendado)
- `pnpm` (para frontend) o `npm`/`yarn` como alternativa
- Entorno virtual para Python (venv, pipenv, etc.)

Estructura principal

- `backend/` – código del backend (FastAPI), configuraciones y utilidades.
- `Frontend/` – aplicación frontend (Vite + React + TypeScript).

Instalación y ejecución (rápido)

1) Backend

- Crear y activar un entorno virtual:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1  # PowerShell
# o en bash: source .venv/bin/activate
```

- Instalar dependencias:

```powershell
cd backend
pip install -r requirements.txt
```

- Configurar variables de entorno: copiar `.env.example` a `.env` y ajustar según tu entorno.

- Iniciar el servidor (modo desarrollo):

```powershell
cd ..\\backend
python run_uvicorn.py
```

Esto ejecuta el servidor (por defecto en `http://127.0.0.1:8000`). También podés usar directamente `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

2) Frontend

- Instalar dependencias y levantar el servidor de desarrollo:

```powershell
cd Frontend
pnpm install    # si no tenés pnpm, podés usar `npm install` o `yarn`
pnpm run dev
```

- Abrir la app en el navegador en la URL que muestre Vite (por defecto `http://localhost:5173`).

Configuración

- `backend/.env` contiene configuración sensible (database URL, secret keys). No subirlo al repo.
- `Frontend/.env` (si existe) contiene variables para la app cliente.

Seeds y datos de prueba

- Si querés precargar datos, revisá `backend/app/modules/seed/seed.py` y los scripts de inicialización.

Desarrollo y pruebas

- Backend: sigue la convención de FastAPI; las rutas principales están en `backend/app/modules/`.
- Frontend: los componentes y páginas están en `Frontend/src/features`.

Contribuir

- Hacé forks o ramas, abrí PRs con cambios pequeños y documentá el propósito.
- Antes de commitear, confirmá que no incluís secretos en `.env` y que pasás linters básicos del frontend si aplican.

Contacto

- Si necesitás ayuda con el setup, podés dejar un issue o escribirme directamente.

Notas

- Este README ofrece un resumen para arrancar rápido; si querés, puedo agregar secciones separadas con instrucciones más detalladas (deploy, tests automatizados, Docker, CI/CD).

Detalles técnicos (alineado a la especificación del Parcial)

- Autenticación y autorización:
	- Endpoints en `/api/v1/auth/`.
	- Registro de usuarios y login por `email/password` que genera cookie `access token` (JWT, 30 min).
	- Endpoint `GET /api/v1/auth/me` para obtener el usuario autenticado.

- Roles (RBAC):
	- `ADMIN`: CRUD completo del sistema (usuarios, productos, categorías, pedidos).
	- `STOCK`: lectura de productos, actualización de stock y disponibilidad.
	- `PEDIDOS`: ver y avanzar estados de pedidos.
	- `CLIENT`: catálogo, carrito y pedidos propios.

- Módulos principales (rutas aproximadas y ubicación de código):
	- `auth` — `backend/app/modules/auth/` (login, registro, dependencias, modelos y service).
	- `productos` — `backend/app/modules/productos/` (listado, filtros, detalle, gestión de ingredientes, PATCH `/disponibilidad`).
	- `categorias` — `backend/app/modules/categorias/` (CRUD jerárquico, soft delete, filtros por `parent_id`).
	- `pedidos` — `backend/app/modules/pedidos/` (creación atómica, máquina de estados, historial de transiciones).
	- `direcciones` — `backend/app/modules/direcciones/` (CRUD del usuario autenticado, marcar principal).
	- `admin` — `backend/app/modules/admin/` (panel de administración: gestión de usuarios, asignación de roles).

- Patrones y arquitectura backend:
	- Unit of Work: gestión transaccional atómica; los servicios no hacen `session.commit()` directamente.
	- Repository Pattern: `BaseRepository[T]` genérico y repositorios por módulo.
	- Service Layer: lógica de negocio stateless implementada en `service.py` de cada módulo.
	- Soft Delete: entidades con `deleted_at` (TIMESTAMPTZ) y validaciones en cascada.
	- Snapshot Pattern: `DetallePedido` guarda precio y nombre inmutables al momento de crear el pedido.
	- Audit Trail append-only: `HistorialEstadoPedido` solo INSERTs (nunca UPDATE/DELETE).

- Gestión de Pedidos (resumen):
	- Máquina de estados con transiciones validadas en la capa servicio (no en router): PENDIENTE → CONFIRMADO → EN_PREP → EN_CAMINO → ENTREGADO / CANCELADO.
	- Cancelación permitida por cliente solo desde PENDIENTE o CONFIRMADO.
	- El cliente ve solo sus pedidos; ADMIN/PEDIDOS ven todos.

- Persistencia y migraciones:
	- Conexión a PostgreSQL (config en `backend/app/core/config.py`).
	- Usar `alembic` para migraciones (archivo `alembic.ini` presente).

- Seed obligatorio:
	- El seed debe precargar roles, estados de pedido, formas de pago y un usuario admin por defecto. Revisá `backend/app/modules/seed/seed.py`.

- Documentación API:
	- Swagger UI en `/docs` y Redoc en `/redoc` cuando el servidor está en ejecución.

Dónde mirar en el repo

- Código backend: `backend/app/` (módulos: `auth`, `productos`, `categorias`, `pedidos`, `direcciones`, `admin`, `seed`).
- Archivo de arranque: `run_uvicorn.py` y `main.py` dentro de `backend/`.

Checklist de arranque rápido (recomendado para evaluación)

1. Crear entorno y activar.
2. Instalar dependencias: `pip install -r backend/requirements.txt`.
3. Configurar `backend/.env` desde `.env.example` (poner DB URL y secrets).
4. Ejecutar seed obligatorio: `python backend/app/modules/seed/seed.py` o el script provisto.
5. Levantar servidor: `python backend/run_uvicorn.py`.

Si querés, actualizo este README con ejemplos de endpoints (paths y payloads), comandos para correr seeds automáticos y un checklist para la grabación del video del parcial.

