import sqlite3
from database.connection import DatabaseManager

def verificar_datos_poblados():
    """
    Muestra los primeros 10 registros de la tabla GruposMateria para verificar los datos.
    """
    db_manager = DatabaseManager()
    try:
        print("--- Verificando datos poblados en 'GruposMateria' ---")
        with db_manager.cursor() as cursor:
            cursor.execute("SELECT id_grupo_materia, codigo_materia_fk, carrera, periodo_academico FROM GruposMateria LIMIT 10")
            registros = cursor.fetchall()
            
            if registros:
                print("(ID Grupo, Código Materia, Carrera, Periodo Académico)")
                for registro in registros:
                    print(registro)
            else:
                print("No se encontraron registros en la tabla GruposMateria.")
            print("-----------------------------------------------------")
            
    except Exception as e:
        print(f"\nOcurrió un error al verificar la base de datos: {e}")
    finally:
        db_manager.cerrar_conexion()
        print("\nConexión cerrada.")

if __name__ == "__main__":
    verificar_datos_poblados()