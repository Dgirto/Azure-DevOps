# Conector Azure DevOps (CON-073)

Conector Ruvic de gestión de trabajo en Azure DevOps. Permite crear
work items, consultar el estado de la ejecución más reciente de un
pipeline, y agregar comentarios a un work item existente.

## Instalación

```bash
pip install git+https://github.com/Dgirto/Azure-DevOps.git#subdirectory=lib
```

Python 3.10+. Dependencia: `requests`.

## Permisos requeridos en Azure DevOps

Generá un **Personal Access Token (PAT) dedicado** (User Settings →
Personal Access Tokens) con, como mínimo, estos scopes:

- **"Work Items (Read & Write)"**: necesario para `create_work_item`
  y `add_comment`.
- **"Build (Read)"**: necesario para `get_pipeline_status`.

No otorgues scopes de administración del proyecto ni de la
organización ("Project and Team", "Graph", etc.). Configurá una
expiración razonable para el PAT (máximo 1 año) y rotalo antes de
que venza.

## Variables de entorno (`RUVIC_AZURE_DEVOPS_*`)

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `RUVIC_AZURE_DEVOPS_ORGANIZATION` | Sí | Nombre de la organización de Azure DevOps |
| `RUVIC_AZURE_DEVOPS_PROJECT` | Sí | Nombre del proyecto |
| `RUVIC_AZURE_DEVOPS_PERSONAL_ACCESS_TOKEN` | Sí | Personal Access Token |
| `RUVIC_AZURE_DEVOPS_CONNECT_TIMEOUT` | No (default `10`) | Timeout de conexión en segundos |

## Pruebas locales

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ./lib

export RUVIC_AZURE_DEVOPS_ORGANIZATION=tu-organizacion
export RUVIC_AZURE_DEVOPS_PROJECT=tu-proyecto
export RUVIC_AZURE_DEVOPS_PERSONAL_ACCESS_TOKEN=tu-pat

python test_connection.py
python validate_local.py
```

Para probar también `get_pipeline_status`, exportá adicionalmente
`RUVIC_AZURE_DEVOPS_TEST_PIPELINE_ID` con el ID de un pipeline de
prueba.

## Notas de integración

- `get_pipeline_status` es de **solo lectura**. `create_work_item` y
  `add_comment` **SÍ escriben** datos reales en el proyecto
  configurado — no hay modo dry-run.
- `create_work_item` acepta cualquier tipo de work item válido en el
  proceso del proyecto (ej. `Task`, `Bug`, `User Story`); un tipo
  inexistente devuelve un error de datos.
- `get_pipeline_status` consulta únicamente la ejecución más reciente
  del pipeline indicado; si el pipeline nunca se ejecutó, retorna un
  error de datos.
- La autenticación usa HTTP Basic Auth con el PAT como contraseña y
  usuario vacío — es el esquema estándar de la API REST de Azure
  DevOps, no requiere `azure-identity`.
