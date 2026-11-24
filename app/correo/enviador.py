"""Envío de códigos de verificación mediante SMTP."""

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage

logger = logging.getLogger(__name__)

SMTP_TIMEOUT_SEGUNDOS = 15


class CorreoNoEnviadoError(RuntimeError):
    """El servidor SMTP no está configurado o rechazó el envío."""


def _autenticar_y_enviar(
    smtp: smtplib.SMTP,
    usuario: str,
    password: str,
    mensaje: EmailMessage,
) -> None:
    if usuario:
        smtp.login(usuario, password)
    smtp.send_message(mensaje)


def enviar_codigo_verificacion(
    destinatario: str,
    codigo: str,
    minutos_validez: int,
) -> None:
    host = os.getenv("SMTP_HOST", "")
    usuario = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    remitente = os.getenv("SMTP_FROM") or usuario
    if not host or not remitente:
        logger.error("SMTP no está configurado; no se pudo enviar el código")
        raise CorreoNoEnviadoError("SMTP no configurado")
    try:
        puerto = int(os.getenv("SMTP_PORT", "587"))
    except ValueError as exc:
        logger.error("SMTP_PORT no es un número válido")
        raise CorreoNoEnviadoError("SMTP_PORT inválido") from exc

    mensaje = EmailMessage()
    mensaje["Subject"] = "Tu código de verificación de RedCuidadora"
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje.set_content(
        f"Tu código de verificación es: {codigo}\n\n"
        f"Vence en {minutos_validez} minutos.\n"
        "Si no intentaste crear una cuenta en RedCuidadora, ignora este correo.\n"
    )

    contexto = ssl.create_default_context()
    try:
        if puerto == 465:
            with smtplib.SMTP_SSL(
                host,
                puerto,
                timeout=SMTP_TIMEOUT_SEGUNDOS,
                context=contexto,
            ) as smtp:
                _autenticar_y_enviar(smtp, usuario, password, mensaje)
        else:
            with smtplib.SMTP(host, puerto, timeout=SMTP_TIMEOUT_SEGUNDOS) as smtp:
                smtp.starttls(context=contexto)
                _autenticar_y_enviar(smtp, usuario, password, mensaje)
    except (smtplib.SMTPException, OSError) as exc:
        logger.error(
            "No se pudo enviar el código de verificación (%s)",
            type(exc).__name__,
        )
        raise CorreoNoEnviadoError("No se pudo enviar el correo") from exc
