import sqlite3
from database.connection import DatabaseManager

def verificar_tablas():
    """
    Muestra los primeros registros de las tablas Materias y GruposMateria para verificar.
    """
    db_manager = DatabaseManager()
    try:
        with db_manager.cursor() as cursor:
            print("--- Verificando 10 primeros registros de 'Materias' ---")
            try:
                cursor.execute("SELECT codigo_materia, nombre_materia, creditos, semestre, es_electiva FROM Materias LIMIT 10")
                registros_materias = cursor.fetchall()
                if registros_materias:
                    print("(Código, Nombre, Créditos, Semestre, Electiva)")
                    for r in registros_materias:
                        print(r)
                else:
                    print("No se encontraron registros en Materias.")
            except sqlite3.OperationalError as e:
                print(f"Error al consultar Materias: {e}. ¿Se ejecutó la migración 002?")

            print("\n--- Verificando 5 primeros registros de 'GruposMateria' ---")
            cursor.execute("SELECT id_grupo_materia, codigo_materia_fk, nombre_grupo FROM GruposMateria LIMIT 5")
            registros_grupos = cursor.fetchall()
            if registros_grupos:
                print("(ID Grupo, Código Materia, Nombre Grupo)")
                for r in registros_grupos:
                    print(r)
            else:
                print("No se encontraron registros en GruposMateria.")

    except Exception as e:
        print(f"\nOcurrió un error al verificar la base de datos: {e}")
    finally:
        db_manager.cerrar_conexion()
        print("\nConexión cerrada.")

if __name__ == "__main__":
    verificar_tablas()
