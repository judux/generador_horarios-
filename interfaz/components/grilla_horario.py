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
        
        # Callbacks
        self.on_celda_seleccionada: Optional[Callable] = None
        self.on_horario_modificado: Optional[Callable] = None
        
        # Crear la grilla
        self._crear_area_grilla()
        self._crear_grilla()
    
    def _crear_area_grilla(self):
        """Crea el área principal de la grilla"""
        # Frame principal del horario
        self.horario_frame = ctk.CTkFrame(
            self.parent, 
            fg_color=self.config.COLORS['bg_card']
        )
        self.horario_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Header del área de horario
        self._crear_header_horario()
        
        # Canvas container para scroll
        self._crear_area_scrollable_grilla()
    
    def _crear_header_horario(self):
        """Crea el header del área de horario usando CTk."""
        header_horario = ctk.CTkFrame(
            self.horario_frame,
            fg_color="transparent",
            height=50
        )
        header_horario.pack(fill="x", padx=20, pady=(10, 0))
        
        # Título
        title_horario = self.theme.crear_label_subtitulo(
            parent=header_horario,
            text="Horario Semanal"
        )
        title_horario.pack(side="left", pady=10)
        
        # Resumen dinámico
        self.resumen_label = ctk.CTkLabel(
            header_horario,
            text="0 materias • 0 créditos",
            font=("Segoe UI", 12),
            text_color=self.config.COLORS['text_secondary']
        )
        self.resumen_label.pack(side="right", pady=10)
    
    def _crear_area_scrollable_grilla(self):
        """Crea el contenedor con canvas para scroll usando CTk."""
        canvas_container = ctk.CTkFrame(
            self.horario_frame, 
            fg_color="transparent"
        )
        canvas_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Canvas principal
        self.canvas_horario = ctk.CTkCanvas(
            canvas_container,
            background=self.config.COLORS['bg_card'],
            highlightthickness=0,
            bd=0
        )
        
        # Scrollbars
        self.scrollbar_v = ctk.CTkScrollbar(
            canvas_container, 
            orientation="vertical", 
            command=self.canvas_horario.yview
        )
        
        self.scrollbar_h = ctk.CTkScrollbar(
            canvas_container, 
            orientation="horizontal", 
            command=self.canvas_horario.xview
        )
        
        # Configurar canvas
        self.canvas_horario.configure(
            yscrollcommand=self.scrollbar_v.set,
            xscrollcommand=self.scrollbar_h.set
        )
        
        # Empaquetar scrollbars y canvas
        self.scrollbar_v.pack(side="right", fill="y")
        self.scrollbar_h.pack(side="bottom", fill="x")
        self.canvas_horario.pack(side="left", fill="both", expand=True)
        
        # Frame interno para la grilla
        self.frame_grilla = ctk.CTkFrame(
            self.canvas_horario, 
            fg_color=self.config.COLORS['bg_card'],
            corner_radius=0
        )
        self.canvas_horario.create_window((0, 0), window=self.frame_grilla, anchor="nw")

        # Configurar eventos de scroll
        self._configurar_scroll()

    def _configurar_scroll(self):
        """Configura el comportamiento del scroll"""
        def _on_frame_configure(event):
            self.canvas_horario.configure(scrollregion=self.canvas_horario.bbox("all"))

        def _on_canvas_configure(event):
            self.canvas_horario.itemconfig(self.canvas_horario.create_window((0, 0), window=self.frame_grilla, anchor="nw"), width=event.width)
        
        def _on_mousewheel(event):
            self.canvas_horario.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Vincular eventos
        self.frame_grilla.bind("<Configure>", _on_frame_configure)
        self.canvas_horario.bind("<Configure>", _on_canvas_configure)
        self.canvas_horario.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _crear_grilla(self):
        """Crea la estructura de la grilla de horarios"""
        # Limpiar grilla anterior
        for widget in self.frame_grilla.winfo_children():
            widget.destroy()
        
        self.grilla_widgets.clear()
        
        # Obtener configuración de horarios
        dias = self.config.SCHEDULE_CONFIG['days']
        horas = self.config.SCHEDULE_CONFIG['hours']
        
        # Crear header de esquina
        self._crear_celda_esquina()
        
        # Crear headers de días
        self._crear_headers_dias(dias)
        
        # Crear labels de horas y celdas
        self._crear_celdas_horario(dias, horas)
        
        # Configurar pesos de grid
        self._configurar_grid_weights(len(dias), len(horas))
    
    def _crear_celda_esquina(self):
        """Crea la celda de esquina superior izquierda"""
        header_esquina = ctk.CTkLabel(
            self.frame_grilla,
            text="Hora",
            font=("Segoe UI", 11, "bold"),
            fg_color=self.config.COLORS['primary'], # Usará el nuevo verde
            text_color="white"
        )
        header_esquina.grid(row=0, column=0, sticky="nsew", padx=(0,1), pady=(0,1))
    
    def _crear_headers_dias(self, dias: list):
        """Crea los headers para cada día de la semana"""
        for i, dia in enumerate(dias):
            header_dia = ctk.CTkLabel(
                self.frame_grilla,
                text=f"{dia}",
                font=("Segoe UI", 11, "bold"),
                fg_color=self.config.COLORS['primary'], # Usará el nuevo verde
                text_color="white"
            )
            header_dia.grid(row=0, column=i+1, sticky="nsew", padx=(0,1), pady=(0,1))
    
    def _crear_celdas_horario(self, dias: list, horas: list):
        """Crea las celdas de horario para cada día y hora"""
        for i, hora in enumerate(horas):
            # Label de hora
            self._crear_label_hora(hora, i + 1)
            
            # Celdas para cada día
            for j, dia in enumerate(dias):
                self._crear_celda_horario(dia, hora, i + 1, j + 1)
    
    def _crear_label_hora(self, hora: str, fila: int):
        """Crea el label para una hora específica"""
        label_hora = ctk.CTkLabel(
            self.frame_grilla,
            text=hora,
            font=("Segoe UI", 10, "bold"),
            fg_color=self.config.COLORS['primary_light'], # Usará el nuevo verde claro
            text_color=self.config.COLORS['primary']
        )
        label_hora.grid(row=fila, column=0, sticky="nsew", padx=(0,1), pady=(0,1))
    
    def _crear_celda_horario(self, dia: str, hora: str, fila: int, columna: int):
        """Crea una celda individual del horario"""
        celda_frame = ctk.CTkFrame(
            self.frame_grilla,
            fg_color=self.config.COLORS['bg_card'],
            border_color=self.config.COLORS['border'],
            border_width=1,
            corner_radius=0,
            height=65  # Aumentamos un poco la altura para mejor visualización
        )
        celda_frame.grid(row=fila, column=columna, sticky="nsew")
        celda_frame.grid_propagate(False)
        
        # Guardar referencia
        clave_celda = (dia, hora)
        self.grilla_widgets[clave_celda] = celda_frame
        
        # Label inicial vacío
        label_vacio = ctk.CTkLabel(
            celda_frame,
            text="",
            fg_color="transparent",
            text_color=self.config.COLORS['text_secondary'],
            font=("Segoe UI", 8)
        )
        label_vacio.pack(fill="both", expand=True)
        
        # Configurar eventos de la celda
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
            # Solo eliminar si la celda está ocupada
            if (dia, hora) in self.controller.obtener_horario_actual():
                self.controller.eliminar_del_horario(dia, hora)
        
        # Aplicar eventos al frame y sus hijos
        widgets_celda = [celda_frame] + list(celda_frame.winfo_children())
        
        for widget in widgets_celda:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click) # Clic izquierdo
            widget.bind("<Button-3>", on_right_click) # Clic derecho
    
    def _configurar_grid_weights(self, num_dias: int, num_horas: int):
        """Configura los pesos del grid para redimensionamiento"""
        # Columna de horas con peso 0 para que no se expanda
        self.frame_grilla.grid_columnconfigure(0, weight=0)
        
        # Configurar filas
        for i in range(num_horas + 1):  # +1 por el header
            self.frame_grilla.grid_rowconfigure(i, weight=1)
        
        # Configurar columnas de los días para que se expandan
        for j in range(1, num_dias + 1):  # Desde 1 para omitir la columna de horas
            self.frame_grilla.grid_columnconfigure(j, weight=1)
    
    def actualizar_grilla(self):
        """Actualiza la grilla con el horario actual del controlador"""
        try:
            # Obtener horario actual
            horario_actual = self.controller.obtener_horario_actual()
            
            # Limpiar celdas existentes
            self._limpiar_celdas()
            
            # Poblar con nuevos datos
            for (dia, hora), data in horario_actual.items():
                if (dia, hora) in self.grilla_widgets:
                    self._poblar_celda(dia, hora, data)
            
            logger.debug(f"Grilla actualizada con {len(horario_actual)} asignaciones")
            
        except Exception as e:
            logger.error(f"Error actualizando grilla: {e}")
    
    def _limpiar_celdas(self):
        """Limpia todas las celdas de la grilla"""
        for celda_frame in self.grilla_widgets.values():
            # Remover widgets existentes
            for widget in celda_frame.winfo_children():
                widget.destroy()
            
            # Agregar label vacío
            label_vacio = ctk.CTkLabel(
                celda_frame,
                text="",
                fg_color="transparent",
                text_color=self.config.COLORS['text_secondary'],
                font=("Segoe UI", 8)
            )
            label_vacio.pack(fill="both", expand=True)
            celda_frame.configure(fg_color=self.config.COLORS['bg_card'])
            
            # Reconfigurar eventos
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
        
        # Limpiar celda
        for widget in celda_frame.winfo_children():
            widget.destroy()
        
        # Container principal
        container = ctk.CTkFrame(celda_frame, fg_color=color_materia, corner_radius=4)
        container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Información de la materia
        self._crear_info_materia(container, data)
        
        # Reconfigurar eventos
        self._configurar_eventos_celda(container, dia, hora)
    
    def _crear_info_materia(self, parent: ctk.CTkFrame, data: Dict[str, Any]):
        """Crea la información visual de la materia en la celda"""
        info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=5, pady=3)
        
        # Nombre de la materia (truncado si es necesario)
        nombre_display = data['info']['nombre']
        if len(nombre_display) > 18:
            nombre_display = nombre_display[:16] + "..."
        
        label_materia = ctk.CTkLabel(
            info_frame,
            text=nombre_display,
            fg_color="transparent",
            font=("Segoe UI", 9, "bold"),
            text_color=self.config.COLORS['text_primary'],
            justify="center",
            wraplength=180
        )
        label_materia.pack(pady=(2,0))
        
        # Información adicional
        info_adicional = f"{data['nombre_grupo']}\n{data['horario_sesion']['tipo_sesion'][:4]}"
        label_info = ctk.CTkLabel(
            info_frame,
            text=info_adicional,
            fg_color="transparent",
            font=("Segoe UI", 7),
            text_color=self.config.COLORS['text_secondary'],
            justify="center"
        )
        label_info.pack()
        
        # Agregar tooltip con información completa
        self._crear_tooltip(info_frame, self._generar_texto_tooltip(data))
    
    def _generar_texto_tooltip(self, data: Dict[str, Any]) -> str:
        """Genera el texto del tooltip con información completa"""
        horario = data['horario_sesion']
        return (
            f"{data['info']['nombre']}\n"
            f"Código: {data['codigo']}\n"
            f"Grupo: {data['nombre_grupo']}\n"
            f"Docente: {horario.get('docente', 'N/A')}\n"
            f"Tipo: {horario['tipo_sesion']}\n"
            f"Horario: {horario['hora_inicio']}-{horario['hora_fin']}\n"
            f"Salón: {horario.get('salon', 'N/A')}\n"
            f"Créditos: {data['info']['creditos']}"
        )
    
    def _crear_tooltip(self, widget: ctk.CTkFrame, texto: str):
        """Crea un tooltip para un widget"""
        def mostrar_tooltip(event):
            # Evitar múltiples tooltips
            if hasattr(self, 'tooltip_window'):
                return
            
            self.tooltip_window = tk.Toplevel()
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            # Contenido del tooltip
            label = ctk.CTkLabel(
                self.tooltip_window,
                text=texto,
                justify='left',
                fg_color=self.config.COLORS['text_primary'],
                text_color='white',
                corner_radius=4,
                font=("Segoe UI", 9),
                padx=10, pady=8
            )
            label.pack()
            
            # Auto-hide después de 3 segundos
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
        
        # Solo cambiar color si la celda está vacía
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
            
            # Solo restaurar color si la celda está vacía
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
        # Implementar lógica para resaltar conflictos
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
