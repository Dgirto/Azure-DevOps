"""Cliente de Azure DevOps para work items, pipelines y comentarios.

Capacidades:
- create_work_item():   crea un work item (Bug, Task, User Story, etc).
- get_pipeline_status(): consulta el estado de la última ejecución de un pipeline.
- add_comment():         agrega un comentario a un work item existente.

Las credenciales SIEMPRE provienen de variables de entorno
RUVIC_AZURE_DEVOPS_* (ver config.AzureDevOpsConfig.from_env). Prohibido
hardcodearlas.

Autenticación: Personal Access Token (PAT) vía HTTP Basic Auth, con
usuario vacío y el PAT como contraseña — es el esquema estándar de la
API REST de Azure DevOps.
"""

from __future__ import annotations

from typing import Any

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError, Timeout

from .config import AzureDevOpsConfig
from .exceptions import (
    AzureDevOpsAuthError,
    AzureDevOpsDataError,
    AzureDevOpsNetworkError,
)
from .logging_utils import get_logger

API_VERSION = "7.1"


class AzureDevOpsClient:
    """Cliente de Azure DevOps sobre la organización y proyecto configurados.

    Args:
        config: configuración de conexión. Si se omite, se lee de las
            variables de entorno RUVIC_AZURE_DEVOPS_* (comportamiento
            estándar en el runtime de la plataforma).

    Ejemplo:
        >>> client = AzureDevOpsClient()  # lee RUVIC_AZURE_DEVOPS_* del entorno
        >>> client.create_work_item("Task", "Revisar deploy")
    """

    def __init__(self, config: AzureDevOpsConfig | None = None) -> None:
        self.config = config or AzureDevOpsConfig.from_env()
        self._logger = get_logger()
        self._base_url = (
            f"https://dev.azure.com/{self.config.organization}/{self.config.project}/_apis"
        )
        self._auth = HTTPBasicAuth("", self.config.personal_access_token)

    # ------------------------------------------------------------------ #
    # Conexión
    # ------------------------------------------------------------------ #

    def _request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        try:
            response = requests.request(
                method,
                url,
                auth=self._auth,
                timeout=self.config.connect_timeout,
                **kwargs,
            )
        except Timeout as exc:
            raise AzureDevOpsNetworkError(f"Timeout conectando a Azure DevOps: {exc}") from exc
        except RequestsConnectionError as exc:
            raise AzureDevOpsNetworkError(f"No se pudo conectar a Azure DevOps: {exc}") from exc

        if response.status_code in (401, 403):
            raise AzureDevOpsAuthError(
                f"Credenciales inválidas o PAT sin permiso suficiente ({response.status_code})."
            )
        if response.status_code == 404:
            raise AzureDevOpsDataError(f"Recurso no encontrado: {url}")
        try:
            response.raise_for_status()
        except HTTPError as exc:
            raise AzureDevOpsDataError(f"Error de Azure DevOps: {exc}") from exc
        return response

    def ping(self) -> bool:
        """Verifica la conexión consultando los metadatos del proyecto.

        Returns:
            True si la conexión funciona.

        Raises:
            AzureDevOpsAuthError / AzureDevOpsNetworkError / AzureDevOpsDataError.
        """
        url = (
            f"https://dev.azure.com/{self.config.organization}/_apis/projects/"
            f"{self.config.project}?api-version={API_VERSION}"
        )
        self._request("GET", url)
        self._logger.info("Ping exitoso al proyecto %s", self.config.project)
        return True

    # ------------------------------------------------------------------ #
    # Capacidad 1: crear un work item
    # ------------------------------------------------------------------ #

    def create_work_item(self, work_item_type: str, title: str, description: str = "") -> dict[str, Any]:
        """Crea un work item en el proyecto configurado.

        Args:
            work_item_type: tipo de work item (ej. "Task", "Bug", "User Story").
            title: título del work item.
            description: descripción opcional.

        Returns:
            Dict con los datos del work item creado (incluye "id" y "url").

        Ejemplo:
            >>> client.create_work_item("Task", "Revisar deploy", "Ver logs de prod")
        """
        if not title:
            raise AzureDevOpsDataError("title no puede estar vacío.")
        url = (
            f"{self._base_url}/wit/workitems/${work_item_type}"
            f"?api-version={API_VERSION}"
        )
        patch = [{"op": "add", "path": "/fields/System.Title", "value": title}]
        if description:
            patch.append(
                {"op": "add", "path": "/fields/System.Description", "value": description}
            )
        response = self._request(
            "POST",
            url,
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )
        data = response.json()
        self._logger.info("Work item creado: #%s", data.get("id"))
        return data

    # ------------------------------------------------------------------ #
    # Capacidad 2: estado de un pipeline
    # ------------------------------------------------------------------ #

    def get_pipeline_status(self, pipeline_id: int) -> dict[str, Any]:
        """Consulta el estado de la ejecución más reciente de un pipeline.

        Args:
            pipeline_id: ID numérico del pipeline.

        Returns:
            Dict con: run_id, state, result, created_date.

        Ejemplo:
            >>> client.get_pipeline_status(42)
            {'run_id': 100, 'state': 'completed', 'result': 'succeeded', ...}
        """
        url = (
            f"{self._base_url}/pipelines/{pipeline_id}/runs"
            f"?api-version={API_VERSION}&$top=1"
        )
        response = self._request("GET", url)
        runs = response.json().get("value", [])
        if not runs:
            raise AzureDevOpsDataError(
                f"El pipeline {pipeline_id} no tiene ejecuciones registradas."
            )
        run = runs[0]
        result = {
            "run_id": run.get("id"),
            "state": run.get("state"),
            "result": run.get("result"),
            "created_date": run.get("createdDate"),
        }
        self._logger.info(
            "Estado del pipeline %s: %s", pipeline_id, result["state"]
        )
        return result

    # ------------------------------------------------------------------ #
    # Capacidad 3: comentar un work item
    # ------------------------------------------------------------------ #

    def add_comment(self, work_item_id: int, text: str) -> dict[str, Any]:
        """Agrega un comentario a un work item existente.

        Args:
            work_item_id: ID numérico del work item.
            text: contenido del comentario.

        Returns:
            Dict con los datos del comentario creado.

        Ejemplo:
            >>> client.add_comment(123, "Verificado en staging")
        """
        if not text:
            raise AzureDevOpsDataError("text no puede estar vacío.")
        url = (
            f"{self._base_url}/wit/workItems/{work_item_id}/comments"
            f"?api-version={API_VERSION}-preview.4"
        )
        response = self._request("POST", url, json={"text": text})
        data = response.json()
        self._logger.info("Comentario agregado al work item #%s", work_item_id)
        return data
