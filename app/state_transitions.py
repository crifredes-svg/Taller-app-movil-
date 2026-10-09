"""Transiciones permitidas para los estados de relevos y alertas SOS."""

TRANSICIONES_RELEVO = {
    "pendiente": {"aceptada"},
    "aceptada": {"completada"},
    "completada": set(),
}

TRANSICIONES_SOS = {
    "activa": {"atendida"},
    "atendida": {"cerrada"},
    "cerrada": set(),
}