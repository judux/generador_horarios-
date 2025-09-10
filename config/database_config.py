"""
Configuración específica de la base de datos
"""

import os
from pathlib import Path

class DatabaseConfig:
    """Configuración de la base de datos SQLite"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.database_dir = self.project_root / "database"
    
    # Nombre de la base de datos
    DATABASE_NAME = "horarios.db"
    
    # Configuración de conexión
    CONNECTION_CONFIG = {
        'timeout': 20.0,
        'check_same_thread': False,
        'isolation_level': None  # Para control manual de transacciones
    }
    
    # Configuración de SQLite específica
    PRAGMA_SETTINGS = [
        "PRAGMA foreign_keys = ON;",
        "PRAGMA journal_mode = WAL;",
        "PRAGMA synchronous = NORMAL;",
        "PRAGMA cache_size = 10000;",
        "PRAGMA temp_store = MEMORY;"
    ]
    
    @property
    def database_path(self):
        """Ruta completa a la base de datos"""
        return self.database_dir / self.DATABASE_NAME
    
    @property
    def database_url(self):
        """URL de conexión a la base de datos"""
        return f"sqlite:///{self.database_path}"
    
    def ensure_database_dir(self):
        """Asegura que el directorio de la base de datos existe"""
        self.database_dir.mkdir(parents=True, exist_ok=True)
