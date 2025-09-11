"""
Configuración general de la aplicación
"""

import os
from pathlib import Path

class AppConfig:
    """Configuración centralizada de la aplicación"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self._setup_paths()
    
    def _setup_paths(self):
        """Configura las rutas del proyecto"""
        self.DATABASE_DIR = self.project_root / "database"
        self.DATA_DIR = self.project_root / "data"
        self.LOG_DIR = self.project_root / "logs"
        
        # Crear directorios si no existen
        self.LOG_DIR.mkdir(exist_ok=True)
    
    # Configuración de la aplicación
    APP_NAME = "Generador de Horarios - Lic. en Informática"
    APP_VERSION = "2.0.0"
    
    # Configuración de la interfaz
    UI_CONFIG = {
        "window_title": APP_NAME,
        "default_geometry": "1600x900",
        "min_width": 1200,
        "min_height": 700,
        "theme": "modern"
    }
    
    # Configuración de colores modernos
    COLORS = {
        'bg_principal': '#F8F9FA',
        'bg_sidebar': '#FFFFFF',
        'bg_card': '#FFFFFF',
        'primary': '#00834D',          # Verde Udenar
        'primary_light': '#D9F9E6',   # Verde claro
        'secondary': '#FBBF24',       # Amarillo Udenar
        'success': '#10B981',
        'warning': '#F59E0B',
        'danger': '#EF4444',
        'text_primary': '#111827',
        'text_secondary': '#6B7280',
        'border': '#E5E7EB',
        'hover': '#F3F4F6'
    }
    
    # Configuración del horario
    SCHEDULE_CONFIG = {
        'days': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
        'hours': [f"{h:02d}:00" for h in range(7, 20)],
        'default_credits': 2,
        'max_credits_normal': 18,
        'max_credits_warning': 22
    }
    
    # Configuración de logging
    LOGGING_CONFIG = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file_max_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5
    }
    
    @property
    def database_path(self):
        """Ruta completa a la base de datos"""
        return self.DATABASE_DIR / "horarios.db"
    
    @property
    def log_file_path(self):
        """Ruta al archivo de log principal"""
        return self.LOG_DIR / "horarios_app.log"
