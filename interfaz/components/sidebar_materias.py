"""
Componente de barra lateral para mostrar y buscar materias.
"""

import customtkinter as ctk
import logging
from typing import Callable, Optional, Dict, Any

from interfaz.controllers.main_controller import MainController
from interfaz.styles.modern_theme import ModernTheme
from config.app_config import AppConfig

logger = logging.getLogger(__name__)

class SidebarMaterias:
    """Barra lateral que muestra una lista de materias y permite la interacción."""

    def __init__(self, parent: ctk.CTkFrame, controller: MainController, theme: ModernTheme, 
                 config: AppConfig, on_materia_seleccionada: Optional[Callable[[str, str], None]] = None):
        self.parent = parent
        self.controller = controller
        self.theme = theme
        self.config = config
        self.on_materia_seleccionada = on_materia_seleccionada

        self.busqueda_var = ctk.StringVar()
        self.busqueda_var.trace_add("write", lambda *args: self._filtrar_y_mostrar_materias())
        
        self.widgets_grupos_expandidos: Dict[str, ctk.CTkFrame] = {}
        
        # Crear la UI del sidebar
        self._crear_sidebar()

    def _crear_sidebar(self):
        """Crea el frame principal que contendrá todos los elementos del sidebar."""
        self.sidebar_frame = ctk.CTkFrame(
            self.parent,
            width=320,
            fg_color=self.config.COLORS['bg_sidebar'],
            corner_radius=8
        )
        self.sidebar_frame.pack(fill="y", side="left", padx=(0, 5))
        self.sidebar_frame.pack_propagate(False)

        self._crear_header()
        self._crear_barra_busqueda()
        self._crear_area_scroll()
        
        self._filtrar_y_mostrar_materias() # Carga inicial

    def _crear_header(self):
        """Crea el título o header visual del sidebar."""
        header_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent", height=50)
        header_frame.pack(fill="x", padx=20, pady=(10, 5))
        header_frame.pack_propagate(False)

        label_titulo = ctk.CTkLabel(
            header_frame,
            text="Materias Disponibles",
            font=("Segoe UI", 16, "bold"),
            text_color=self.config.COLORS['text_primary'],
            anchor="w"
        )
        label_titulo.pack(side="left", fill="both", expand=True)

    def _crear_barra_busqueda(self):
        """Crea el campo de búsqueda."""
        search_entry = ctk.CTkEntry(
            self.sidebar_frame,
            textvariable=self.busqueda_var,
            placeholder_text="Buscar por nombre o código...",
            height=35,
            border_width=1,
            corner_radius=8
        )
        search_entry.pack(fill="x", padx=20, pady=(5, 10))

    def _crear_area_scroll(self):
        """Crea un área scrolleable para la lista de materias."""
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.sidebar_frame,
            fg_color="transparent"
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def _filtrar_y_mostrar_materias(self):
        """Filtra las materias según el término de búsqueda y las muestra."""
        termino_busqueda = self.busqueda_var.get()
        try:
            materias = self.controller.obtener_materias_filtradas(termino_busqueda)
            self._poblar_lista_materias(materias)
        except Exception as e:
            logger.error(f"Error al cargar/filtrar materias: {e}")
            self._mostrar_error_carga("No se pudieron cargar las materias.")

    def _poblar_lista_materias(self, materias: Dict[str, Any]):
        """Limpia el frame y lo llena con los widgets de las materias."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not materias:
            self._mostrar_mensaje_vacio("No se encontraron materias.")
            return

        for codigo, data in materias.items():
            self._crear_widget_materia(codigo, data)

    def _crear_widget_materia(self, codigo: str, data: Dict[str, Any]):
        """Crea el widget expandible para una materia."""
        materia_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        materia_frame.pack(fill="x", pady=(0, 5))

        # Header de la materia (clickable para expandir/colapsar)
        header = ctk.CTkFrame(materia_frame, fg_color=self.config.COLORS['hover'], height=40, corner_radius=6, cursor="hand2")
        header.pack(fill="x")

        nombre_materia = data['nombre']
        if len(nombre_materia) > 30:
            nombre_materia = nombre_materia[:28] + "..."

        label_nombre = ctk.CTkLabel(header, text=nombre_materia, font=("Segoe UI", 11, "bold"), anchor="w")
        label_nombre.pack(side="left", padx=10)

        label_expandir = ctk.CTkLabel(header, text="▼", font=("Segoe UI", 10))
        label_expandir.pack(side="right", padx=10)

        # Contenedor para los grupos (inicialmente oculto)
        grupos_container = ctk.CTkFrame(materia_frame, fg_color="transparent")
        self.widgets_grupos_expandidos[codigo] = grupos_container

        # Lógica para expandir/colapsar
        def toggle_grupos(event):
            if grupos_container.winfo_ismapped():
                grupos_container.pack_forget()
                label_expandir.configure(text="▼")
            else:
                self._poblar_grupos(grupos_container, codigo, data['grupos'])
                grupos_container.pack(fill="x", padx=(15, 0), pady=5)
                label_expandir.configure(text="▲")

        header.bind("<Button-1>", toggle_grupos)
        label_nombre.bind("<Button-1>", toggle_grupos)
        label_expandir.bind("<Button-1>", toggle_grupos)

    def _poblar_grupos(self, container: ctk.CTkFrame, codigo_materia: str, grupos: Dict[str, Any]):
        """Llena el contenedor con los grupos de una materia."""
        # Limpiar por si se repite el click
        for widget in container.winfo_children():
            widget.destroy()

        if not grupos:
            ctk.CTkLabel(container, text="No hay grupos disponibles.", text_color=self.config.COLORS['text_secondary'], font=("Segoe UI", 10, "italic")).pack(anchor="w", pady=5)
            return

        for nombre_grupo, data_grupo in grupos.items():
            self._crear_widget_grupo(container, codigo_materia, nombre_grupo, data_grupo)

    def _crear_widget_grupo(self, parent: ctk.CTkFrame, codigo_materia: str, nombre_grupo: str, data_grupo: Dict[str, Any]):
        """Crea el widget para un grupo específico, que es clickeable."""
        grupo_frame = ctk.CTkFrame(parent, fg_color="transparent", cursor="hand2")
        grupo_frame.pack(fill="x", pady=3)

        # Círculo de color para identificar
        color_materia = self.controller.obtener_color_materia(codigo_materia)
        color_indicator = ctk.CTkFrame(grupo_frame, width=10, height=10, fg_color=color_materia, corner_radius=5, border_width=0)
        color_indicator.pack(side="left", padx=(0, 8), pady=4)

        # Información del grupo
        info_text = f"{nombre_grupo} - {data_grupo.get('docente', 'N/A')}"
        label_grupo = ctk.CTkLabel(grupo_frame, text=info_text, font=("Segoe UI", 10), anchor="w")
        label_grupo.pack(side="left", fill="x", expand=True)

        # Evento de click para agregar al horario
        def agregar_al_horario(event):
            if self.on_materia_seleccionada:
                logger.info(f"Click en grupo: {codigo_materia} - {nombre_grupo}")
                self.on_materia_seleccionada(codigo_materia, nombre_grupo)

        grupo_frame.bind("<Button-1>", agregar_al_horario)
        label_grupo.bind("<Button-1>", agregar_al_horario)
        color_indicator.bind("<Button-1>", agregar_al_horario)

        # Efecto hover
        def on_enter(e):
            grupo_frame.configure(fg_color=self.config.COLORS['hover'])
        def on_leave(e):
            grupo_frame.configure(fg_color="transparent")

        grupo_frame.bind("<Enter>", on_enter)
        grupo_frame.bind("<Leave>", on_leave)

    def _mostrar_error_carga(self, mensaje):
        """Muestra un mensaje de error en el área de materias."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        error_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=mensaje,
            text_color=self.config.COLORS['danger'],
            font=("Segoe UI", 11, "italic"),
            wraplength=250
        )
        error_label.pack(pady=20, padx=10, fill="x")

    def _mostrar_mensaje_vacio(self, mensaje: str):
        """Muestra un mensaje cuando no hay materias que mostrar."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        empty_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=mensaje,
            text_color=self.config.COLORS['text_secondary'],
            font=("Segoe UI", 11, "italic"),
            wraplength=250
        )
        empty_label.pack(pady=20, padx=10, fill="x")
