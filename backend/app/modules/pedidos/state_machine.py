# app/modules/pedidos/state_machine.py

# Diccionario con los estados y hacia dónde pueden avanzar
VALID_TRANSITIONS: dict[str, list[str]] = {
    "PENDIENTE":   ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO":  ["EN_PREP", "CANCELADO"],
    "EN_PREP":     ["ENTREGADO", "EN_CAMINO"],
    "EN_CAMINO":   ["ENTREGADO"],
    "ENTREGADO":   [],
    "CANCELADO":   [],
}

def can_transition(estado_actual: str, nuevo_estado: str) -> bool:
    """Valida si el salto de un estado a otro está permitido."""
    return nuevo_estado in VALID_TRANSITIONS.get(estado_actual, [])

def can_client_cancel(estado_actual: str) -> bool:
    """El cliente solo puede cancelar si el pedido no empezó a prepararse."""
    return estado_actual in ("PENDIENTE", "CONFIRMADO")
