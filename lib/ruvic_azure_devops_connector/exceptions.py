"""Jerarquía de excepciones del conector Azure DevOps."""

from __future__ import annotations


class AzureDevOpsConnectorError(Exception):
    """Error base del conector Azure DevOps."""


class AzureDevOpsAuthError(AzureDevOpsConnectorError):
    """Credenciales inválidas o Personal Access Token sin permiso suficiente."""


class AzureDevOpsNetworkError(AzureDevOpsConnectorError):
    """Error de red o timeout al conectar con Azure DevOps."""


class AzureDevOpsDataError(AzureDevOpsConnectorError):
    """Recurso inexistente u otro error de datos devuelto por la API."""
