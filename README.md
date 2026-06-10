# Food Store - Backend (FastAPI)

Backend del TPI de Programacion 4 (UTN), basado en FastAPI + SQLModel + PostgreSQL.
Este README esta adaptado al backend real del repo y alineado con la especificacion de Food Store v6.0.

## 1) Resumen

La API provee:

- Autenticacion y autorizacion con JWT + RBAC.
- CRUD de categorias, ingredientes, productos e imagenes.
- Gestion de direcciones de entrega.
- Gestion de pedidos con flujo de estados.
- Notificaciones en tiempo real por WebSocket para pedidos.
- Seed inicial automatico (roles, estados, formas de pago y admin).
- Documentacion OpenAPI en `/docs` y `/redoc`.

## 2) Stack backend

- Python 3.10+
- FastAPI
- SQLModel
- PostgreSQL
- python-jose (JWT)
- Passlib/bcrypt
- Cloudinary SDK

## 3) Estructura de carpetas (backend)

```text
Backend/
  README.md
  backend/
    main.py
    run_uvicorn.py
    requirements.txt
    .env.example
    app/
      core/
        config.py
        database.py
        security.py
        websocket.py
        unit_of_work.py
      modules/
        auth/
        admin/
        categorias/
        direcciones/
        ingredientes/
        productos/
        pedidos/
        images/
        usuarios/
        seed/
```

## 4) Requisitos previos

- Python 3.10 o superior.
- PostgreSQL en ejecucion.
- (Opcional) cuenta Cloudinary para upload de imagenes.

## 5) Configuracion e instalacion

### 5.1 Crear y activar entorno virtual

PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Bash:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
```

### 5.2 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5.3 Variables de entorno

Copiar `backend/.env.example` a `backend/.env` y completar:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sistema_pedidos
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

SECRET_KEY=una_clave_larga_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Cloudinary (opcionales, pero recomendadas si usas uploads)
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

## 6) Ejecucion

Desde `Backend/backend/`:

```bash
python run_uvicorn.py
```

La API levanta en:

- `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

Nota: al iniciar, `lifespan` ejecuta `create_db_and_tables()`, `run_seed()` e `init_cloudinary()`.

## 7) Seed inicial

El seed se ejecuta automaticamente en el arranque y crea (si no existen):

- Roles: `ADMIN`, `STOCK`, `PEDIDOS`, `CLIENT`.
- Estados de pedido.
- Formas de pago.
- Usuario admin por defecto.

Credenciales seed (default):

- Email: `admin@foodstore.com`
- Password: `admin123`

Archivo: `backend/app/modules/seed/seed.py`.

## 8) Arquitectura y convenciones

El backend sigue una arquitectura por capas y por features:

- Flujo de dependencias: Router -> Service -> UnitOfWork -> Repository -> Model.
- `Service`: contiene la logica de negocio.
- `Unit of Work`: controla la transaccion (commit/rollback).
- `Repository`: encapsula acceso a datos.
- `WS Manager`: emite eventos post-commit para tiempo real.

Principio clave: la logica de negocio vive en servicios, no en routers.

## 9) Modulos principales

- `auth/`: login, registro, refresh, logout, usuario actual.
- `usuarios/`: gestion de usuarios y roles.
- `categorias/`: CRUD de categorias.
- `ingredientes/`: CRUD de ingredientes.
- `productos/`: CRUD de productos, disponibilidad y relaciones.
- `direcciones/`: CRUD de direcciones del usuario.
- `pedidos/`: alta/listado de pedidos, cambios de estado e historial.
- `images/`: upload/listado/eliminacion de imagenes.
- `admin/`: endpoints de gestion para panel admin.

## 10) Endpoints clave (resumen)

Todos los endpoints REST usan prefijo `/api/v1`.

### Auth

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

### Productos y catalogo

- `GET /api/v1/productos`
- `GET /api/v1/productos/{id}`
- `POST /api/v1/productos`
- `PUT /api/v1/productos/{id}`
- `PATCH /api/v1/productos/{id}/disponibilidad`

### Pedidos

- `GET /api/v1/pedidos`
- `GET /api/v1/pedidos/{id}`
- `POST /api/v1/pedidos`
- `PATCH /api/v1/pedidos/{id}/estado`
- `GET /api/v1/pedidos/{id}/historial`

### Direcciones

- `GET /api/v1/direcciones`
- `POST /api/v1/direcciones`
- `PUT /api/v1/direcciones/{id}`
- `PATCH /api/v1/direcciones/{id}/principal`
- `DELETE /api/v1/direcciones/{id}`

### Imagenes

- `GET /api/v1/images`
- `GET /api/v1/images/{image_id}`
- `POST /api/v1/images/upload`
- `DELETE /api/v1/images/{image_id}`

## 11) WebSocket

Canal implementado:

- `WS /ws/pedidos?token=<jwt>`

Comportamiento:

- Si el usuario tiene rol `ADMIN` o `PEDIDOS`, se conecta al canal admin de pedidos.
- Si no, se conecta al canal de cliente segun su `usuario_id`.
- El token JWT se valida al conectar.

## 12) CORS

Actualmente configurado para frontends locales:

- `http://localhost:5173` (admin)
- `http://localhost:5174` (store)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:5174`

Si cambias puertos o dominios, actualizalo en `backend/main.py`.

## 13) Checklist de arranque (para correccion)

1. Crear y activar entorno virtual.
2. Instalar dependencias con `pip install -r requirements.txt`.
3. Configurar `backend/.env` desde `.env.example`.
4. Verificar PostgreSQL activo y accesible.
5. Levantar API con `python run_uvicorn.py`.
6. Probar `/docs` y flujo de login.
7. Verificar rol admin seed (`admin@foodstore.com`).

## 14) Notas de alineacion con la especificacion v6.0

- Este backend sigue el enfoque feature-first y la base de arquitectura del documento.
- La especificacion del TPI incluye ademas integracion de pagos y uploads avanzados; esta version documenta lo que esta presente en este repo actualmente.
- Si se agregan nuevos modulos (por ejemplo pagos MercadoPago dedicados), actualizar este README para mantener trazabilidad con la entrega.

