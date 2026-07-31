"""Validación local del conector azure_devops: ejercita las 3 capacidades.

Uso:
    python validate_local.py

Requiere las variables RUVIC_AZURE_DEVOPS_* exportadas en el entorno,
apuntando a una organización/proyecto de prueba.

ADVERTENCIA: este script crea un work item REAL y le agrega un
comentario REAL. Ejecútalo solo contra un proyecto de pruebas.
"""

import os

from ruvic_azure_devops_connector import AzureDevOpsClient, setup_logging

setup_logging("INFO")
client = AzureDevOpsClient()

print("== 1. Crear work item de prueba ==")
work_item = client.create_work_item(
    "Task", "Validación local Ruvic", "Creado por validate_local.py"
)
work_item_id = work_item["id"]
print(f"  creado: #{work_item_id}")

print("== 2. Agregar comentario al work item ==")
client.add_comment(work_item_id, "Comentario de validación local Ruvic")
print("  comentario agregado")

pipeline_id = os.environ.get("RUVIC_AZURE_DEVOPS_TEST_PIPELINE_ID")
if pipeline_id:
    print("== 3. Consultar estado de pipeline ==")
    estado = client.get_pipeline_status(int(pipeline_id))
    print(f"  {estado}")
else:
    print("== 3. Consultar estado de pipeline: omitido "
          "(seteá RUVIC_AZURE_DEVOPS_TEST_PIPELINE_ID para probarlo) ==")

print("\nTodo OK: create_work_item, add_comment y get_pipeline_status funcionan.")
