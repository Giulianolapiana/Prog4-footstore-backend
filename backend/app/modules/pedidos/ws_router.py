from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Cookie
from jose import jwt, JWTError
from app.core.config import settings
from app.core.websocket import ws_manager

router = APIRouter(tags=["WebSocket Pedidos"])

@router.websocket("/ws/pedidos")
async def websocket_pedidos(websocket: WebSocket, access_token: str | None = Cookie(default=None)):
    canal = None
    
    if not access_token:
        await websocket.close(code=1008)
        return
        
    try:
        #  Validar el token manualmente 
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # sub puede ser email o id
        usuario_id = payload.get("id") or payload.get("sub") 
        roles = payload.get("roles", [])

        if not usuario_id:
            await websocket.close(code=1008)
            return

        # Extraer solo los códigos de los roles si es una lista de diccionarios o strings
        roles_codigos = [r if isinstance(r, str) else r.get("codigo") for r in roles]

        #  Determinar a qué canal se suscribe según el RBAC
        if "ADMIN" in roles_codigos or "PEDIDOS" in roles_codigos:
            canal = "admin:pedidos"
        else:
            canal = f"cliente:{usuario_id}"

        # Conectar al manager
        await ws_manager.connect(websocket, canal)

        # Mantener la conexión
        while True:
            # El servidor no espera recibir comandos por acá, solo emitir. 
            # El receive_text() es bloqueante y mantiene viva la conexión hasta que el cliente cierre.
            await websocket.receive_text()

    except JWTError:
        # Código 4001: Señal específica para que el frontend sepa que debe hacer refresh del token
        await websocket.close(code=4001)
    except WebSocketDisconnect:
        # El cliente cerro la pestaña
        if canal:
            ws_manager.disconnect(websocket, canal)
    except Exception as e:
        print(f"Error WS: {e}")
        if canal:
            ws_manager.disconnect(websocket, canal)