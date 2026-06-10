from typing import Dict, List
from fastapi import WebSocket
from datetime import datetime, timezone

class WSManager:
    def __init__(self):
        # Diccionario para mapear canales ("admin:pedidos" o "cliente:1") con listas de WebSockets
        self._connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, canal: str):
        await websocket.accept()
        if canal not in self._connections:
            self._connections[canal] = []
        self._connections[canal].append(websocket)

    def disconnect(self, websocket: WebSocket, canal: str):
        if canal in self._connections:
            if websocket in self._connections[canal]:
                self._connections[canal].remove(websocket)
            if not self._connections[canal]:
                del self._connections[canal]

    async def broadcast(self, canal: str, data: dict):
        """Envía un mensaje a todos los websockets conectados a un canal específico."""
        if canal in self._connections:
            # Copiamos la lista para evitar errores si alguien se desconecta mientras iteramos
            for connection in list(self._connections[canal]):
                try:
                    await connection.send_json(data)
                except Exception:
                    # Si falla el envío (ej: cerró el navegador), lo desconectamos
                    self.disconnect(connection, canal)

    async def broadcast_pedido_update(self, pedido_id: int, usuario_id: int, evento: str, estado_nuevo: str, estado_anterior: str = None, motivo: str = None):
        """
        Helper específico que cumple con el contrato JSON del frontend.
        Avisa al cliente dueño del pedido y a todos los administradores.
        """
        payload = {
            "event": evento,
            "pedido_id": pedido_id,
            "usuario_id": usuario_id,
            "estado_nuevo": estado_nuevo,
            "estado_anterior": estado_anterior,
            "motivo": motivo,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

        # Avisar al canal de administradores
        await self.broadcast("admin:pedidos", payload)
        
        # Avisar al canal cliente 
        if usuario_id:
            await self.broadcast(f"cliente:{usuario_id}", payload)

ws_manager = WSManager()