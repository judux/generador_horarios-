from db_manager import obtener_detalles_materia
import json

# Código de la materia que quieres ver
codigo = "INF101"

detalles = obtener_detalles_materia(codigo)
if detalles:
    print(json.dumps(detalles, indent=4, ensure_ascii=False))
