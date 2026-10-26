---
name: azure-devops
description: Crear work items en Azure DevOps, consultar el estado de pipelines y agregar comentarios
---

# Azure DevOps

Conector para gestión de trabajo en Azure DevOps sobre la
organización y proyecto configurados.

## Credenciales

Usa un Personal Access Token (PAT) autenticado vía HTTP Basic Auth
(usuario vacío, PAT como contraseña). Nunca hardcodees ni loguees el
PAT. El PAT debe tener asignados, como mínimo:

- **"Work Items (Read & Write)"** — requerido para
  `create_work_item` y `add_comment`.
- **"Build (Read)"** — requerido para `get_pipeline_status`.

No uses un PAT con scopes de administración de proyecto u
organización.

## Capacidades

### `create_work_item(work_item_type: str, title: str, description: str = "") -> dict`

Crea un work item real en el proyecto configurado. Valida el tipo antes
de crear: si no existe en el proceso del proyecto, lanza
`AzureDevOpsDataError` con los tipos disponibles y no crea nada.
Devuelve `id`, `type`, `title`, `state` y `url`.

```python
work_item = client.create_work_item("Task", "Revisar deploy", "Ver logs de prod")
print(work_item["id"], work_item["url"])
```

### `list_work_item_types() -> list[str]`

Lista los tipos habilitados en el proyecto (Basic: Epic, Issue, Task;
Agile: User Story, Bug, Task, etc.).

```python
tipos = client.list_work_item_types()
```

### `get_pipeline_status(pipeline_id: int) -> dict`

Consulta el estado (`state`, `result`) de la ejecución más reciente
de un pipeline. Solo lectura.

```python
estado = client.get_pipeline_status(42)
```

### `add_comment(work_item_id: int, text: str) -> dict`

Agrega un comentario real a un work item existente.

```python
client.add_comment(123, "Verificado en staging")
```

## Manejo de errores

Todas las excepciones heredan de `AzureDevOpsConnectorError`:

- `AzureDevOpsAuthError`: PAT inválido, expirado o sin scope
  suficiente.
- `AzureDevOpsNetworkError`: organización/proyecto inalcanzable,
  timeout de red.
- `AzureDevOpsDataError`: work item, pipeline o tipo de work item
  inexistente, u otro error de datos.

Nunca dejes propagar excepciones crudas de `requests`
(`requests.exceptions.*`) — siempre se traducen a estas.

## Buenas prácticas

- Tratá `create_work_item` y `add_comment` como operaciones con
  efectos secundarios reales; no las ejecutes contra un proyecto de
  producción sin confirmar con el usuario.
- `get_pipeline_status` es segura de ejecutar libremente (solo
  lectura).
- Si el usuario no especifica un tipo de work item, preguntá o usá
  "Task" como default razonable — no asumas "Bug" sin que lo pida.
- **Si el tipo pedido no existe en el proyecto, NO lo sustituyas por
  otro "equivalente"** (ej. User Story → Issue). Informa el error con
  los tipos disponibles y pregunta al usuario cuál quiere usar.
- Muestra al usuario solo los campos relevantes (número, tipo, título,
  estado, enlace); no vuelques respuestas JSON completas de la API.
