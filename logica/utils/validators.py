# logica/validators.py

# El error común es tener una función mal indentada, como la comentada abajo:
#
# def validar_nombre_materia(nombre):
# return len(nombre) > 3 and len(nombre) < 50  <-- ERROR: Indentación incorrecta

def validar_nombre_materia(nombre: str) -> bool:
    """
    Valida que el nombre de una materia tenga una longitud adecuada.
    Toda la lógica está correctamente indentada dentro de la función.
    """
    if not isinstance(nombre, str):
        return False
    
    longitud_valida = 3 <= len(nombre.strip()) <= 50
    return longitud_valida

def validar_codigo_semestre(codigo: str) -> bool:
    """
    Valida que el código de un semestre tenga el formato correcto (ej: '2025-1').
    """
    if not isinstance(codigo, str):
        return False
        
    parts = codigo.split('-')
    if len(parts) != 2:
        return False
        
    year, period = parts
    return year.isdigit() and len(year) == 4 and period.isdigit()

# Puedes añadir más clases o funciones de validación aquí.
# class UserValidator:
#     def is_valid_email(self, email):
#         # Lógica de validación...
#         pass
