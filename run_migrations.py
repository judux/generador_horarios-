
import logging
from database.connection import DatabaseManager
from database.migrations import DatabaseMigrator

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Ejecuta el proceso de migración de la base de datos utilizando DatabaseMigrator.
    """
    logging.info("Iniciando el proceso de migraciones...")
    
    db_manager = DatabaseManager()
    migrator = DatabaseMigrator(db_manager)
    
    success = migrator.ejecutar_migraciones()
    
    if success:
        logging.info("Todas las migraciones pendientes se han ejecutado exitosamente.")
    else:
        logging.error("El proceso de migración encontró un error.")
    
    db_manager.cerrar_conexion()
    logging.info("Proceso de migraciones finalizado. Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    main()
