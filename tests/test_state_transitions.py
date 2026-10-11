import pytest

from app.state_transitions import TRANSICIONES_RELEVO, TRANSICIONES_SOS


@pytest.mark.parametrize(
    ("transiciones", "actual", "siguiente"),
    [
        (TRANSICIONES_RELEVO, "pendiente", "aceptada"),
        (TRANSICIONES_RELEVO, "aceptada", "completada"),
        (TRANSICIONES_SOS, "activa", "atendida"),
        (TRANSICIONES_SOS, "atendida", "cerrada"),
    ],
)
def test_transiciones_validas(transiciones, actual, siguiente):
    assert siguiente in transiciones[actual]


@pytest.mark.parametrize(
    ("transiciones", "actual", "siguiente"),
    [
        (TRANSICIONES_RELEVO, "completada", "pendiente"),
        (TRANSICIONES_RELEVO, "completada", "aceptada"),
        (TRANSICIONES_SOS, "cerrada", "activa"),
        (TRANSICIONES_SOS, "cerrada", "atendida"),
    ],
)
def test_transiciones_invalidas(transiciones, actual, siguiente):
    assert siguiente not in transiciones[actual]