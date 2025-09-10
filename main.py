#!/usr/bin/env python3
"""
Generador de Horarios - Licenciatura en Informática
Punto de entrada principal de la aplicación

Este módulo inicializa la aplicación, configura la base de datos y lanza la interfaz gráfica.
"""

import sys
import os
import logging
from pathlib import Path

# Agregar el directorio raíz del proyecto al path de Python
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('horarios_app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal que inicializa y ejecuta la aplicación"""
    try:
        logger.info("Iniciando aplicación Generador de Horarios...")
        
        # Importar módulos necesarios
        from database.connection import DatabaseManager
        from database.migrations import DatabaseMigrator
        from interfaz.main_window import AplicacionHorarioModerna
        from config.app_config import AppConfig
        
        # Inicializar configuración
        config = AppConfig()
        
        # Inicializar y verificar base de datos
        logger.info("Inicializando base de datos...")
        db_manager = DatabaseManager()
        
        if not db_manager.verificar_conexion():
            logger.error("No se pudo conectar a la base de datos")
            return 1
        
        # Ejecutar migraciones si es necesario
        migrator = DatabaseMigrator(db_manager)
        if not migrator.ejecutar_migraciones():
            logger.error("Error ejecutando migraciones de base de datos")
            return 1
        
        # Inicializar interfaz gráfica
        logger.info("Iniciando interfaz gráfica...")
        import tkinter as tk
        
        root = tk.Tk()
        app = AplicacionHorarioModerna(root, db_manager)
        
        logger.info("Aplicación iniciada exitosamente")
        app.run()
        
        return 0
        
    except ImportError as e:
        logger.error(f"Error de importación: {e}")
        print(f"Error: No se pudo importar un módulo necesario: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        print(f"Error inesperado: {e}")
        return 1
    finally:
        logger.info("Aplicación finalizada")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
