"""Configuración del conector leída desde variables de entorno.

Convención de la plataforma: cada campo del formulario de configuración
llega como variable de entorno {ENV_PREFIX}{CAMPO} en mayúsculas.
Para este conector el prefijo es RUVIC_AZURE_DEVOPS_.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

ENV_PREFIX = "RUVIC_AZURE_DEVOPS_"


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
            connect_timeout=int(os.environ.get(f"{ENV_PREFIX}CONNECT_TIMEOUT", "10")),
        )
