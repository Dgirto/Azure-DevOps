"""Configuración del conector leída desde variables de entorno.

Convención de la plataforma: cada campo del formulario de configuración
llega como variable de entorno {ENV_PREFIX}{CAMPO} en mayúsculas.
Para este conector el prefijo es RUVIC_AZURE_DEVOPS_.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

ENV_PREFIX = "RUVIC_AZURE_DEVOPS_"


def _read_timeout(default: int = 10) -> int:
    """Lee CONNECT_TIMEOUT tratando el string vacío como ausente: la
    plataforma envía "" cuando el campo opcional queda en blanco."""
    raw = (os.environ.get(f"{ENV_PREFIX}CONNECT_TIMEOUT") or "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        raise ValueError(
            f"{ENV_PREFIX}CONNECT_TIMEOUT debe ser un número entero de segundos, no {raw!r}."
        ) from None
    if value <= 0:
        raise ValueError(f"{ENV_PREFIX}CONNECT_TIMEOUT debe ser mayor que 0, no {value}.")
    return value


@dataclass(frozen=True)
class AzureDevOpsConfig:
    """Parámetros de conexión a Azure DevOps vía Personal Access Token."""

    organization: str
    project: str
    personal_access_token: str
    connect_timeout: int = 10

    @classmethod
    def from_env(cls) -> "AzureDevOpsConfig":
        """Construye la configuración desde las variables RUVIC_AZURE_DEVOPS_*.

        Raises:
            ValueError: si falta alguna variable obligatoria.

        Ejemplo:
            >>> config = AzureDevOpsConfig.from_env()
            >>> config.organization
            'mi-organizacion'
        """
        missing = [
            f"{ENV_PREFIX}{name}"
            for name in ("ORGANIZATION", "PROJECT", "PERSONAL_ACCESS_TOKEN")
            if not os.environ.get(f"{ENV_PREFIX}{name}")
        ]
        if missing:
            raise ValueError(
                "Faltan variables de entorno del conector azure_devops: "
                + ", ".join(missing)
                + ". Configura el conector en Settings → Conectores."
            )
        return cls(
            organization=os.environ[f"{ENV_PREFIX}ORGANIZATION"],
            project=os.environ[f"{ENV_PREFIX}PROJECT"],
            personal_access_token=os.environ[f"{ENV_PREFIX}PERSONAL_ACCESS_TOKEN"],
            connect_timeout=_read_timeout(),
        )
