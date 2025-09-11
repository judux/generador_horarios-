"""
Componente de grilla para mostrar el horario semanal
"""
import tkinter as tk # Se mantiene para Toplevel (tooltips)
import customtkinter as ctk
import logging
from typing import Dict, Any, Optional, Callable, Tuple
from interfaz.controllers.main_controller import MainController
from interfaz.styles.modern_theme import ModernTheme
from config.app_config import AppConfig

logger = logging.getLogger(__name__)

class GrillaHorario:
    """Componente de grilla para mostrar y gestionar el horario semanal"""
    
    def __init__(self, parent: ctk.CTkFrame, controller: MainController, 
                 theme: ModernTheme, config: AppConfig):
        self.parent = parent
        self.controller = controller
        self.theme = theme
        self.config = config
        
        # Variables de estado
        self.grilla_widgets = {}
        self.hover_celda = None
        self.tooltips_activos = {}
        self.horario_mostrado_actualmente = {} # Para optimizar updates
        
        # Callbacks
        self.on_celda_seleccionada: Optional[Callable] = None
        self.on_horario_modificado: Optional[Callable] = None
        
        # Crear la grilla
        self._crear_area_grilla()
        self._crear_grilla()
    
    def _crear_area_grilla(self):
        """Crea el área principal de la grilla"""
        self.horario_frame = ctk.CTkFrame(
            self.parent, 
            fg_color=self.config.COLORS['bg_card']
        )
        self.horario_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        self._crear_header_horario()
        self._crear_area_scrollable_grilla()
    
    def _crear_header_horario(self):
        """Crea el header del área de horario usando CTk."""
        header_horario = ctk.CTkFrame(self.horario_frame, fg_color="transparent", height=50)
        header_horario.pack(fill="x", padx=20, pady=(10, 0))
        header_horario.grid_columnconfigure(0, weight=1)
        header_horario.grid_columnconfigure(1, weight=0)
        header_horario.grid_columnconfigure(2, weight=1)

        title_horario = self.theme.crear_label_subtitulo(
            parent=header_horario,
            text="Horario Semanal",
            text_color=self.config.COLORS['secondary'],
            font=("Segoe UI", 22, "bold")
        )
        title_horario.grid(row=0, column=1)

        self.resumen_label = ctk.CTkLabel(header_horario, text="0 materias • 0 créditos", font=("Segoe UI", 12), text_color=self.config.COLORS['text_secondary'])
        self.resumen_label.grid(row=0, column=2, sticky="e")

    def _crear_label_hora(self, hora: str, fila: int):
        """Crea el label para una hora específica"""
        label_hora = ctk.CTkLabel(
            self.frame_grilla,
            text=hora,
            font=("Segoe UI", 12, "bold"),
            fg_color=self.config.COLORS['bg_sidebar'],
            text_color=self.config.COLORS['text_primary']
        )
        label_hora.grid(row=fila, column=0, sticky="nsew", padx=(0, 2), pady=(0, 2))
    
    def _crear_area_scrollable_grilla(self):
        """Crea el contenedor con canvas para scroll usando CTk."""
        canvas_container = ctk.CTkFrame(self.horario_frame, fg_color="transparent")
        canvas_container.pack(fill="both", expand=True, padx=20, pady=10)
        self.canvas_horario = ctk.CTkCanvas(canvas_container, background=self.config.COLORS['bg_card'], highlightthickness=0, bd=0)
        self.scrollbar_v = ctk.CTkScrollbar(canvas_container, orientation="vertical", command=self.canvas_horario.yview)
        self.scrollbar_h = ctk.CTkScrollbar(canvas_container, orientation="horizontal", command=self.canvas_horario.xview)
        self.canvas_horario.configure(yscrollcommand=self.scrollbar_v.set, xscrollcommand=self.scrollbar_h.set)
        self.scrollbar_v.pack(side="right", fill="y")
        self.scrollbar_h.pack(side="bottom", fill="x")
        self.canvas_horario.pack(side="left", fill="both", expand=True)
        self.frame_grilla = ctk.CTkFrame(self.canvas_horario, fg_color=self.config.COLORS['bg_card'], corner_radius=0)
        self.canvas_horario.create_window((0, 0), window=self.frame_grilla, anchor="nw")
        self._configurar_scroll()

    def _configurar_scroll(self):
        """Configura el comportamiento del scroll"""
        def _on_frame_configure(event):
            self.canvas_horario.configure(scrollregion=self.canvas_horario.bbox("all"))
        def _on_canvas_configure(event):
            self.canvas_horario.itemconfig(self.canvas_horario.create_window((0, 0), window=self.frame_grilla, anchor="nw"), width=event.width)
        def _on_mousewheel(event):
            self.canvas_horario.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.frame_grilla.bind("<Configure>", _on_frame_configure)
        self.canvas_horario.bind("<Configure>", _on_canvas_configure)
        self.canvas_horario.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _crear_grilla(self):
        """Crea la estructura de la grilla de horarios"""
        for widget in self.frame_grilla.winfo_children():
            widget.destroy()
        self.grilla_widgets.clear()
        dias = self.config.SCHEDULE_CONFIG['days']
        horas = self.config.SCHEDULE_CONFIG['hours']
        self._crear_celda_esquina()
        self._crear_headers_dias(dias)
        self._crear_celdas_horario(dias, horas)
        self._configurar_grid_weights(len(dias), len(horas))
    
    def _crear_celda_esquina(self):
        """Crea la celda de esquina superior izquierda"""
        header_esquina = ctk.CTkLabel(self.frame_grilla, text="Hora", font=("Segoe UI", 11, "bold"), fg_color=self.config.COLORS['primary'], text_color="white")
        header_esquina.grid(row=0, column=0, sticky="nsew", padx=(0,1), pady=(0,1))
    
    def _crear_headers_dias(self, dias: list):
        """Crea los headers para cada día de la semana"""
        for i, dia in enumerate(dias):
            header_dia = ctk.CTkLabel(self.frame_grilla, text=f"{dia}", font=("Segoe UI", 11, "bold"), fg_color=self.config.COLORS['primary'], text_color="white")
            header_dia.grid(row=0, column=i+1, sticky="nsew", padx=(0,1), pady=(0,1))
    
    def _crear_celdas_horario(self, dias: list, horas: list):
        """Crea las celdas de horario para cada día y hora"""
        for i, hora in enumerate(horas):
            self._crear_label_hora(hora, i + 1)
            for j, dia in enumerate(dias):
                self._crear_celda_horario(dia, hora, i + 1, j + 1)
    
    def _crear_label_hora(self, hora: str, fila: int):
        """Crea el label para una hora específica"""
        label_hora = ctk.CTkLabel(
            self.frame_grilla,
            text=hora,
            font=("Segoe UI", 12, "bold"),
            fg_color=self.config.COLORS['border'],
            text_color=self.config.COLORS['text_primary']
        )
        label_hora.grid(row=fila, column=0, sticky="nsew", padx=(0, 2), pady=(0, 2))
    
    def _crear_celda_horario(self, dia: str, hora: str, fila: int, columna: int):
        """Crea una celda individual del horario"""
        celda_frame = ctk.CTkFrame(self.frame_grilla, fg_color=self.config.COLORS['bg_card'], border_color=self.config.COLORS['border'], border_width=1, corner_radius=0, height=65)
        celda_frame.grid(row=fila, column=columna, sticky="nsew")
        celda_frame.grid_propagate(False)
        self.grilla_widgets[(dia, hora)] = celda_frame
        label_vacio = ctk.CTkLabel(celda_frame, text="", fg_color="transparent", text_color=self.config.COLORS['text_secondary'], font=("Segoe UI", 8))
        label_vacio.pack(fill="both", expand=True)
        self._configurar_eventos_celda(celda_frame, dia, hora)
    
    def _configurar_eventos_celda(self, celda_frame: ctk.CTkFrame, dia: str, hora: str):
        """Configura los eventos de una celda"""
        def on_enter(event):
            self._on_celda_hover(dia, hora)
        def on_leave(event):
            self._on_celda_leave()
        def on_click(event):
            if self.on_celda_seleccionada:
                self.on_celda_seleccionada(dia, hora)
        def on_right_click(event):
            if (dia, hora) in self.controller.obtener_horario_actual():
                self.controller.eliminar_del_horario(dia, hora)
        widgets_celda = [celda_frame] + list(celda_frame.winfo_children())
        for widget in widgets_celda:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
            widget.bind("<Button-3>", on_right_click)
    
    def _configurar_grid_weights(self, num_dias: int, num_horas: int):
        """Configura los pesos del grid para redimensionamiento"""
        self.frame_grilla.grid_columnconfigure(0, weight=0)
        for i in range(num_horas + 1):
            self.frame_grilla.grid_rowconfigure(i, weight=1)
        for j in range(1, num_dias + 1):
            self.frame_grilla.grid_columnconfigure(j, weight=1)
    
    def actualizar_grilla(self):
        """Actualiza la grilla con el horario actual del controlador de forma eficiente."""
        try:
            horario_nuevo = self.controller.obtener_horario_actual()
            celdas_a_poblar = set(horario_nuevo.keys())
            celdas_a_limpiar = set(self.horario_mostrado_actualmente.keys()) - celdas_a_poblar

            for dia, hora in celdas_a_poblar:
                if (dia, hora) in self.grilla_widgets:
                    self._poblar_celda(dia, hora, horario_nuevo[(dia, hora)])

            for dia, hora in celdas_a_limpiar:
                if (dia, hora) in self.grilla_widgets:
                    self._limpiar_celda(self.grilla_widgets[(dia, hora)])

            self.horario_mostrado_actualmente = horario_nuevo
            logger.debug(f"Grilla actualizada. {len(celdas_a_poblar)} celdas pobladas, {len(celdas_a_limpiar)} celdas limpiadas.")

        except Exception as e:
            logger.error(f"Error actualizando grilla: {e}", exc_info=True)

    def _limpiar_celda(self, celda_frame: ctk.CTkFrame):
        """Limpia una celda individual de la grilla."""
        for widget in celda_frame.winfo_children():
            widget.destroy()
        
        label_vacio = ctk.CTkLabel(celda_frame, text="", fg_color="transparent", text_color=self.config.COLORS['text_secondary'], font=("Segoe UI", 8))
        label_vacio.pack(fill="both", expand=True)
        celda_frame.configure(fg_color=self.config.COLORS['bg_card'])
        
        dia, hora = None, None
        for (d, h), frame in self.grilla_widgets.items():
            if frame == celda_frame:
                dia, hora = d, h
                break
        
        if dia and hora:
            self._configurar_eventos_celda(celda_frame, dia, hora)

    def _poblar_celda(self, dia: str, hora: str, data: Dict[str, Any]):
        """Puebla una celda específica con datos de materia"""
        celda_frame = self.grilla_widgets[(dia, hora)]
        color_materia = self.controller.obtener_color_materia(data['codigo'])
        for widget in celda_frame.winfo_children():
            widget.destroy()
        container = ctk.CTkFrame(celda_frame, fg_color=color_materia, corner_radius=4)
        container.pack(fill="both", expand=True, padx=2, pady=2)
        self._crear_info_materia(container, data)
        self._configurar_eventos_celda(container, dia, hora)
    
    def _crear_info_materia(self, parent: ctk.CTkFrame, data: Dict[str, Any]):
        """Crea la información visual de la materia en la celda"""
        info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=5, pady=3)
        nombre_display = data['info']['nombre']
        if len(nombre_display) > 18:
            nombre_display = nombre_display[:16] + "..."
        label_materia = ctk.CTkLabel(info_frame, text=nombre_display, fg_color="transparent", font=("Segoe UI", 9, "bold"), text_color=self.config.COLORS['text_primary'], justify="center", wraplength=180)
        label_materia.pack(pady=(2,0))
        info_adicional = f"{data['nombre_grupo']}\n{data['horario_sesion']['tipo_sesion'][:4]}"
        label_info = ctk.CTkLabel(info_frame, text=info_adicional, fg_color="transparent", font=("Segoe UI", 7), text_color=self.config.COLORS['text_secondary'], justify="center")
        label_info.pack()
        self._crear_tooltip(info_frame, self._generar_texto_tooltip(data))
    
    def _generar_texto_tooltip(self, data: Dict[str, Any]) -> str:
        """Genera el texto del tooltip con información completa"""
        horario = data['horario_sesion']
        return (f"{data['info']['nombre']}\n" f"Código: {data['codigo']}\n" f"Grupo: {data['nombre_grupo']}\n" f"Docente: {horario.get('docente', 'N/A')}\n" f"Tipo: {horario['tipo_sesion']}\n" f"Horario: {horario['hora_inicio']}-{horario['hora_fin']}\n" f"Salón: {horario.get('salon', 'N/A')}\n" f"Créditos: {data['info']['creditos']}")
    
    def _crear_tooltip(self, widget: ctk.CTkFrame, texto: str):
        """Crea un tooltip para un widget"""
        def mostrar_tooltip(event):
            if hasattr(self, 'tooltip_window'): return
            self.tooltip_window = tk.Toplevel()
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ctk.CTkLabel(self.tooltip_window, text=texto, justify='left', fg_color=self.config.COLORS['text_primary'], text_color='white', corner_radius=4, font=("Segoe UI", 9), padx=10, pady=8)
            label.pack()
            def ocultar_tooltip():
                if hasattr(self, 'tooltip_window'):
                    self.tooltip_window.destroy()
                    delattr(self, 'tooltip_window')
            self.tooltip_window.after(3000, ocultar_tooltip)
        def ocultar_tooltip_inmediato(event):
            if hasattr(self, 'tooltip_window'):
                self.tooltip_window.destroy()
                delattr(self, 'tooltip_window')
        widget.bind("<Enter>", mostrar_tooltip)
        widget.bind("<Leave>", ocultar_tooltip_inmediato)
    
    def actualizar_resumen(self, estadisticas: Dict[str, Any]):
        """Actualiza el resumen mostrado en el header"""
        try:
            total_materias = estadisticas.get('total_materias', 0)
            total_creditos = estadisticas.get('total_creditos', 0)
            texto_resumen = f"{total_materias} materias • {total_creditos} créditos"
            self.resumen_label.configure(text=texto_resumen)
        except Exception as e:
            logger.error(f"Error actualizando resumen: {e}")
    
    def _on_celda_hover(self, dia: str, hora: str):
        """Maneja el evento hover sobre una celda"""
        self.hover_celda = (dia, hora)
        horario_actual = self.controller.obtener_horario_actual()
        if (dia, hora) not in horario_actual:
            celda = self.grilla_widgets.get((dia, hora))
            if celda:
                celda.configure(fg_color=self.config.COLORS['hover'])
    
    def _on_celda_leave(self):
        """Maneja cuando el mouse sale de una celda"""
        if self.hover_celda:
            dia, hora = self.hover_celda
            horario_actual = self.controller.obtener_horario_actual()
            if (dia, hora) not in horario_actual:
                celda = self.grilla_widgets.get((dia, hora))
                if celda:
                    celda.configure(fg_color=self.config.COLORS['bg_card'])
        self.hover_celda = None
    
    def obtener_celda_seleccionada(self) -> Optional[Tuple[str, str]]:
        """Obtiene la celda actualmente seleccionada"""
        return self.hover_celda
    
    def resaltar_conflictos(self, conflictos: list):
        """Resalta celdas donde hay conflictos potenciales"""
        for conflicto in conflictos:
            dia = conflicto.get('dia')
            hora = conflicto.get('hora')
            if (dia, hora) in self.grilla_widgets:
                celda = self.grilla_widgets[(dia, hora)]
                celda.configure(border_color=self.config.COLORS['danger'], border_width=2)
    
    def limpiar_resaltados(self):
        """Limpia todos los resaltados de conflictos"""
        for celda in self.grilla_widgets.values():
            celda.configure(border_color=self.config.COLORS['border'], border_width=1)