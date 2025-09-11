"""
Punto de entrada principal de la aplicación Generador de Horarios.
"""
import sys
import traceback
import logging
from logging.handlers import RotatingFileHandler

from config.app_config import AppConfig
from database.connection import DatabaseManager
from database.migrations import DatabaseMigrator
from interfaz.main_window import MainWindow

def setup_logging(config: AppConfig):
    """Configura el sistema de logging para la aplicación."""
    log_config = config.LOGGING_CONFIG
    log_file = config.log_file_path

    # Configurar el logger raíz
    logging.basicConfig(
        level=log_config['level'],
        format=log_config['format'],
        handlers=[
            logging.StreamHandler(sys.stdout) # Para ver logs en la consola
        ]
    )

    # Añadir un handler para rotar archivos de log
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=log_config['file_max_size'],
        backupCount=log_config['backup_count']
    )
    file_handler.setFormatter(logging.Formatter(log_config['format']))
    logging.getLogger().addHandler(file_handler)

    logging.info("Logging configurado exitosamente.")

def main():
    """Función principal que inicia la aplicación."""
    config = AppConfig()
    setup_logging(config)

    try:
        # 1. Inicializar la base de datos y ejecutar migraciones
        db_manager = DatabaseManager()
        migrator = DatabaseMigrator(db_manager)
        if not migrator.ejecutar_migraciones():
            raise RuntimeError("No se pudieron ejecutar las migraciones de la base de datos.")

        # 2. Iniciar la aplicación
        app = MainWindow(db_manager)
        app.mainloop()

    except Exception as e:
        logging.critical("--- OCURRIÓ UN ERROR GRAVE AL INICIAR ---")
        logging.critical(f"ERROR: {e}", exc_info=True)
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)

try:
    if __name__ == "__main__":
        main()
except Exception as e:
    # Este bloque es por si hay un error en el if __name__ == "__main__":
    logging.critical("Error fatal en el bloque de ejecución principal.", exc_info=True)
    input("\nPresiona Enter para salir...")
