import sqlite3
from database.connection import DatabaseManager

def verificar_tablas():
    """
    Se conecta a la base de datos y lista todas las tablas existentes.
    """
    db_manager = DatabaseManager()
    try:
        print("Conexión exitosa a la base de datos.")
        with db_manager.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = cursor.fetchall()
        
        if tablas:
            print("Tablas en la base de datos:")
            for tabla in tablas:
                print(f"- {tabla[0]}")
        else:
            print("La base de datos está vacía (no contiene tablas).")
            
    except Exception as e:
        print(f"Ocurrió un error al verificar la base de datos: {e}")
    finally:
        db_manager.cerrar_conexion()
        print("Conexión cerrada.")

if __name__ == "__main__":
    verificar_tablas()
