import logging
from database.connection import DatabaseManager

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_migration():
    """
    Añade las columnas 'carrera' y 'periodo_academico' a la tabla GruposMateria.
    """
    logging.info("Iniciando migración de la base de datos...")
    db_manager = DatabaseManager()
    
    try:
        with db_manager.cursor() as cursor:
            # 1. Verificar si la columna 'carrera' existe
            cursor.execute("PRAGMA table_info(GruposMateria)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'carrera' not in columns:
                logging.info("Añadiendo columna 'carrera' a la tabla GruposMateria.")
                cursor.execute("ALTER TABLE GruposMateria ADD COLUMN carrera TEXT")
            else:
                logging.info("La columna 'carrera' ya existe.")

            # 2. Verificar si la columna 'periodo_academico' existe
            if 'periodo_academico' not in columns:
                logging.info("Añadiendo columna 'periodo_academico' a la tabla GruposMateria.")
                cursor.execute("ALTER TABLE GruposMateria ADD COLUMN periodo_academico TEXT")
            else:
                logging.info("La columna 'periodo_academico' ya existe.")
        
        logging.info("Migración completada exitosamente.")
        
    except Exception as e:
        logging.error(f"Ocurrió un error durante la migración: {e}")
    finally:
        db_manager.cerrar_conexion()
        logging.info("Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    run_migration()
