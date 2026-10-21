"""Domain transitions allowed for relief requests and SOS alerts."""

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