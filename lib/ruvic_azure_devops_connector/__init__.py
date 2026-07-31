"""Conector Ruvic para Azure DevOps: work items, pipelines y comentarios."""

from .client import AzureDevOpsClient
from .config import AzureDevOpsConfig, ENV_PREFIX
from .exceptions import (
    AzureDevOpsAuthError,
    AzureDevOpsConnectorError,
    AzureDevOpsDataError,
    AzureDevOpsNetworkError,
)
from .logging_utils import setup_logging

__all__ = [
    "ENV_PREFIX",
    "AzureDevOpsAuthError",
    "AzureDevOpsClient",
    "AzureDevOpsConfig",
    "AzureDevOpsConnectorError",
    "AzureDevOpsDataError",
    "AzureDevOpsNetworkError",
    "setup_logging",
]

__version__ = "1.0.0"
