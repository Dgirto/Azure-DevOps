"""Prueba de conexión estándar del conector azure_devops.

Firma estándar Ruvic: def test_connection() -> tuple[bool, str]
- Lee la configuración EXCLUSIVAMENTE de las env vars RUVIC_AZURE_DEVOPS_*.
- Nunca lanza excepciones; retorna (ok, mensaje).

Ejecutable también como script para pruebas locales:
    python test_connection.py
"""

from __future__ import annotations


def test_connection() -> tuple[bool, str]:
    """Conecta a Azure DevOps y consulta el proyecto configurado usando
    las env vars RUVIC_AZURE_DEVOPS_*."""
    try:
        from ruvic_azure_devops_connector import (
            AzureDevOpsAuthError,
            AzureDevOpsClient,
            AzureDevOpsDataError,
            AzureDevOpsNetworkError,
        )
    except ImportError:
        return (
            False,
            "La librería ruvic-azure-devops-connector no está instalada. "
            "Instala con: pip install git+https://github.com/Dgirto/"
            "Azure-DevOps.git#subdirectory=lib",
        )

    try:
        client = AzureDevOpsClient()  # valida que existan las env vars
    except ValueError as exc:
        return False, str(exc)

    try:
        client.ping()
    except AzureDevOpsAuthError as exc:
        return False, f"Autenticación fallida: {exc}"
    except AzureDevOpsNetworkError as exc:
        return False, f"Error de red: {exc}"
    except AzureDevOpsDataError as exc:
        return False, f"Error de datos: {exc}"
    except Exception as exc:  # red de seguridad: jamás propagar
        return False, f"Error inesperado: {exc}"

    return (
        True,
        f"Conexión exitosa a Azure DevOps ({client.config.organization}/{client.config.project})",
    )


if __name__ == "__main__":
    ok, message = test_connection()
    print(f"{'OK' if ok else 'FALLO'}: {message}")
    raise SystemExit(0 if ok else 1)
