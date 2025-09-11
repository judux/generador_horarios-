"""
Ventana principal de la aplicación de horarios - Refactorizada
"""

import customtkinter as ctk
import logging

from database.connection import DatabaseManager
from interfaz.controllers.main_controller import MainController
from interfaz.components.sidebar_materias import SidebarMaterias
from interfaz.components.grilla_horario import GrillaHorario
from interfaz.components.notification_toast import NotificationToast
from interfaz.styles.modern_theme import ModernTheme
from config.app_config import AppConfig

logger = logging.getLogger(__name__)

class MainWindow(ctk.CTk):
    """
    Ventana principal de la aplicación que organiza la interfaz de usuario.
    """
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.config = AppConfig()
        self.theme = ModernTheme()

        # El controlador se pasa ahora desde fuera, pero para este ejemplo lo creamos aquí.
        # En una app real, se inyectaría.
        self.controller = MainController(self.db_manager)

        self._configurar_ventana()
        self._crear_widgets()
        self._vincular_eventos()

    def _configurar_ventana(self):
        """Configura los parámetros principales de la ventana."""
        self.title(self.config.UI_CONFIG["window_title"])
        self.geometry(self.config.UI_CONFIG["default_geometry"])
        self.minsize(self.config.UI_CONFIG["min_width"], self.config.UI_CONFIG["min_height"])
        
        # Usando los colores de AppConfig para consistencia
        self.configure(fg_color=self.config.COLORS['bg_principal'])
        
        # Configurar el tema global de customtkinter
        ctk.set_appearance_mode("Dark") # O "Dark" o "System"
        ctk.set_default_color_theme("blue") # O "green", "dark-blue"

    def _crear_widgets(self):
        """Crea y posiciona los componentes principales de la UI."""
        # Frame principal que contendrá todo
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Crear el sidebar de materias
        # Nota: El SidebarMaterias usa tkinter, habría que refactorizarlo a ctk
        self.sidebar = SidebarMaterias(
            parent=main_frame,
            controller=self.controller,
            theme=self.theme,
            config=self.config,
            on_materia_seleccionada=self.on_materia_seleccionada
        )

        # Crear la grilla de horario
        # Nota: GrillaHorario también usa tkinter, necesita refactorización a ctk
        self.grilla_horario = GrillaHorario(
            parent=main_frame,
            controller=self.controller,
            theme=self.theme,
            config=self.config
        )

    def _vincular_eventos(self):
        """Vincula los callbacks del controlador a los eventos de la UI."""
        self.controller.on_horario_changed = self.grilla_horario.actualizar_grilla
        self.controller.on_creditos_changed = self._actualizar_resumen_horario
        
        # Vincular los nuevos callbacks de notificación
        self.controller.on_success = lambda title, msg: self.show_notification(title, msg, "success")
        self.controller.on_warning = lambda title, msg: self.show_notification(title, msg, "warning")
        self.controller.on_error = lambda title, msg: self.show_notification(title, msg, "error")

    def on_materia_seleccionada(self, codigo_materia: str, nombre_grupo: str):
        """Maneja la selección de una materia desde el sidebar."""
        logger.info(f"Materia seleccionada para agregar: {codigo_materia}, Grupo: {nombre_grupo}")
        self.controller.agregar_grupo_al_horario(codigo_materia, nombre_grupo)

    def _actualizar_resumen_horario(self):
        """Obtiene estadísticas y actualiza el resumen en la grilla."""
        stats = self.controller.obtener_estadisticas_horario()
        self.grilla_horario.actualizar_resumen(stats)

    def show_notification(self, title: str, message: str, notification_type: str):
        """Muestra una notificación tipo toast."""
                # NotificationToast(
        #     parent=self,
        #     title=title,
        #     message=message,
        #     notification_type=notification_type
        # )
        pass
