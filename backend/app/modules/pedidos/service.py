from typing import List, Optional
from decimal import Decimal
from fastapi import status
from sqlmodel import Session
from app.modules.pedidos.models import Pedido, DetallePedido, HistorialEstadoPedido
from app.modules.pedidos.schemas import PedidoCreate
from app.modules.pedidos.unit_of_work import PedidoUnitOfWork
from app.modules.pedidos.state_machine import can_transition, can_client_cancel
from app.core.exceptions.custom_exceptions import (
    ResourceNotFoundError,
    BusinessRuleError,
    AuthorizationError,
    AppError
)
from app.core.websocket import ws_manager

class PedidoService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def listar_pedidos(self, usuario_id: Optional[int] = None, skip: int = 0, limit: int = 50) -> List[Pedido]:
        with PedidoUnitOfWork(self._session) as uow:
            return uow.pedidos.get_all_filtered(skip=skip, limit=limit, usuario_id=usuario_id)

    def obtener_por_id(self, pedido_id: int, usuario_id_actual: int, es_admin_o_gestor: bool) -> Pedido:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if not pedido:
                raise ResourceNotFoundError(resource="pedido", identifier=pedido_id)
            # Validación de seguridad: el cliente solo ve sus propios pedidos
            if not es_admin_o_gestor and pedido.usuario_id != usuario_id_actual:
                raise AuthorizationError("No tienes permiso para ver este pedido.")
            return pedido

    async def crear_pedido(self, usuario_id: int, data: PedidoCreate) -> Pedido:
        with PedidoUnitOfWork(self._session) as uow:
            # 1. Validar Dirección
            direccion = uow.direcciones.get_by_id(data.direccion_entrega_id)
            if not direccion or direccion.usuario_id != usuario_id:
                raise BusinessRuleError("Dirección de entrega inválida o no pertenece al usuario.")

            # 2. Validar Estado Inicial
            estado_inicial = uow.estados.get_by_codigo("PENDIENTE")
            if not estado_inicial:
                raise AppError("Estado PENDIENTE no configurado en la DB.", status_code=500)

            # 3. Snapshot Pattern: Leer productos y calcular totales inmutables
            total_pedido = Decimal('0.00')
            detalles_a_guardar = []

            for item in data.detalles:
                producto = uow.productos.get_by_id(item.producto_id)
                if not producto or not producto.disponible:
                    raise BusinessRuleError(f"El producto con ID {item.producto_id} no está disponible.")

                if producto.stock_cantidad < item.cantidad:
                    raise BusinessRuleError(
                        f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_cantidad}."
                    )

                # Reducir stock
                producto.stock_cantidad -= item.cantidad
                uow._session.add(producto)

                subtotal = producto.precio_base * Decimal(str(item.cantidad))
                total_pedido += subtotal

                # Creamos el detalle congelando el nombre y el precio
                detalles_a_guardar.append(DetallePedido(
                    producto_id=producto.id,
                    nombre_snapshot=producto.nombre, # Snapshot
                    precio_snapshot=producto.precio_base, # Snapshot
                    cantidad=item.cantidad,
                    subtotal_snap=subtotal
                ))

            # 4. Crear el Pedido Cabecera
            descuento = Decimal('0.00')
            costo_envio = Decimal('50.00')
            
            nuevo_pedido = Pedido(
                usuario_id=usuario_id,
                estado_actual_id=estado_inicial.id,
                forma_pago_id=data.forma_pago_id,
                direccion_entrega_id=data.direccion_entrega_id,
                subtotal=total_pedido,
                descuento=descuento,
                costo_envio=costo_envio,
                total=total_pedido - descuento + costo_envio
            )
            uow.pedidos.add(nuevo_pedido)
            uow._session.flush() # Forzamos la asignación del ID del pedido

            # 5. Guardar Detalles
            for det in detalles_a_guardar:
                det.pedido_id = nuevo_pedido.id
                uow.detalles.add(det)

            # 6. Audit Trail: Registrar paso a PENDIENTE
            historial = HistorialEstadoPedido(
                pedido_id=nuevo_pedido.id,
                estado_desde=None,
                estado_hacia=estado_inicial.codigo,
                usuario_id=usuario_id
            )
            uow.historiales.add(historial)

            # Copiamos datos necesarios para el WS antes de salir del UoW
            pedido_id = nuevo_pedido.id

        await ws_manager.broadcast_pedido_update(
            pedido_id=pedido_id,
            usuario_id=usuario_id,
            evento="pedido_creado",
            estado_nuevo="PENDIENTE"
        )
        return nuevo_pedido

    async def avanzar_estado(self, pedido_id: int, nuevo_estado_codigo: str, usuario_id: int) -> Pedido:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if not pedido:
                raise ResourceNotFoundError(resource="pedido", identifier=pedido_id)

            estado_actual = uow.estados.get_by_id(pedido.estado_actual_id)
            
            # Validación con State Machine
            if not can_transition(estado_actual.codigo, nuevo_estado_codigo):
                raise BusinessRuleError(
                    f"Transición inválida de {estado_actual.codigo} a {nuevo_estado_codigo}."
                )

            nuevo_estado = uow.estados.get_by_codigo(nuevo_estado_codigo)
            
            # Actualizamos la cabecera
            pedido.estado_actual_id = nuevo_estado.id
            uow.pedidos.update(pedido)

            # Audit Trail: Insertar el registro del salto
            historial = HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_desde=estado_actual.codigo,
                estado_hacia=nuevo_estado.codigo,
                usuario_id=usuario_id
            )
            uow.historiales.add(historial)

            pedido_usuario_id = pedido.usuario_id

        await ws_manager.broadcast_pedido_update(
            pedido_id=pedido_id,
            usuario_id=pedido_usuario_id,
            evento="estado_cambiado",
            estado_nuevo=nuevo_estado_codigo
        )
        return pedido

    async def cancelar_pedido(self, pedido_id: int, usuario_id: int, es_cliente: bool) -> Pedido:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if not pedido:
                raise ResourceNotFoundError(resource="pedido", identifier=pedido_id)

            if es_cliente and pedido.usuario_id != usuario_id:
                raise AuthorizationError("No puedes cancelar un pedido ajeno.")

            estado_actual = uow.estados.get_by_id(pedido.estado_actual_id)

            # Validación de cancelación para clientes
            if es_cliente and not can_client_cancel(estado_actual.codigo):
                raise BusinessRuleError("El pedido ya está en preparación o en camino. Contacte soporte.")

            if estado_actual.codigo in ["ENTREGADO", "CANCELADO"]:
                raise BusinessRuleError("El pedido ya finalizó su ciclo.")

            # Reponer stock al cancelar el pedido
            for detalle in pedido.detalles:
                producto = uow.productos.get_by_id(detalle.producto_id)
                if producto:
                    producto.stock_cantidad += detalle.cantidad
                    uow._session.add(producto)

            estado_cancelado = uow.estados.get_by_codigo("CANCELADO")
            pedido.estado_actual_id = estado_cancelado.id
            uow.pedidos.update(pedido)

            historial = HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_desde=estado_actual.codigo,
                estado_hacia=estado_cancelado.codigo,
                usuario_id=usuario_id
            )
            uow.historiales.add(historial)

            pedido_usuario_id = pedido.usuario_id

        await ws_manager.broadcast_pedido_update(
            pedido_id=pedido_id,
            usuario_id=pedido_usuario_id,
            evento="pedido_cancelado",
            estado_nuevo="CANCELADO"
        )
        return pedido