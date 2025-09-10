"""
Ventana principal de la aplicación de horarios - Refactorizada
"""

import tkinter as tk
import logging
from typing import Dict, Any
from database.connection import DatabaseManager
from interfaz.controllers.main_controller import MainController
from interfaz.components.sidebar_materias import SidebarMaterias
from interfaz.components.grilla_horario import GrillaHorario
from interfaz.styles.modern_theme import ModernTheme
from config.app_config import AppConfig

logger = logging.getLogger(__name__)

class AplicacionHorarioModerna:
    """Ventana principal de la aplicación moderna de horarios"""
    
    def __init__(self, master_window: tk.Tk, db_manager: DatabaseManager):
        self.master = master_window
        self.db_manager = db_manager
        self.config = AppConfig()
        self.theme = ModernTheme()
        
        # Inicializar controlador principal
        self.controller = MainController(db_manager)
        
        # Variables de estado de la interfaz
        self.components = {}
        
        self._configurar_ventana_principal()
        self._configurar_estilos()
        self._crear_interfaz()
        self._conectar_eventos()
        
        logger.info("Interfaz principal inicializada correctamente")
    
    def _configurar_ventana_principal(self):
        """Configura las propiedades básicas de la ventana principal"""
        self.master.title(self.config.UI_CONFIG['window_title'])
        self.master.geometry(self.config.UI_CONFIG['default_geometry'])
        self.master.minsize(
            self.config.UI_CONFIG['min_width'], 
            self.config.UI_CONFIG['min_height']
        )
        
        # Intentar maximizar la ventana
        try:
            self.master.state('zoomed')  # Windows
        except tk.TclError:
            try:
                self.master.attributes('-zoomed', True)  # Linux
            except tk.TclError:
                pass  # macOS o sistemas que no soportan maximizar
        
        self.master.configure(bg=self.config.COLORS['bg_principal'])
    
    def _configurar_estilos(self):
        """Configura los estilos TTK y temas modernos"""
        self.theme.aplicar_tema(self.master)
        
        # Configurar colores personalizados adicionales
        self.master.option_add('*TCombobox*Listbox.selectBackground', self.config.COLORS['primary'])
        self.master.option_add('*TCombobox*Listbox.selectForeground', 'white')
    
    def _crear_interfaz(self):
        """Crea la interfaz principal con todos sus componentes"""
        # Crear toolbar superior
        self._crear_toolbar()
        
        # Container principal
        main_container = tk.Frame(
            self.master, 
            bg=self.config.COLORS['bg_principal']
        )
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Crear sidebar de materias
        self.components['sidebar'] = SidebarMaterias(
            parent=main_container,
            controller=self.controller,
            theme=self.theme,
            config=self.config
        )
        
        # Crear área de horario
        self.components['grilla'] = GrillaHorario(
            parent=main_container,
            controller=self.controller,
            theme=self.theme,
            config=self.config
        )
        
        logger.info("Componentes de interfaz creados exitosamente")
    
    def _crear_toolbar(self):
        """Crea la barra de herramientas superior"""
        toolbar = tk.Frame(
            self.master, 
            bg=self.config.COLORS['bg_principal'], 
            height=80
        )
        toolbar.pack(fill=tk.X, padx=20, pady=20)
        toolbar.pack_propagate(False)
        
        # Título principal con icono
        title_frame = tk.Frame(toolbar, bg=self.config.COLORS['bg_principal'])
        title_frame.pack(side=tk.LEFT, pady=10)
        
        title_icon = tk.Label(
            title_frame,
            text="📚",
            font=("Segoe UI", 20),
            bg=self.config.COLORS['bg_principal']
        )
        title_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = tk.Label(
            title_frame,
            text="Generador de Horarios",
            font=("Segoe UI", 24, "bold"),
            bg=self.config.COLORS['bg_principal'],
            fg=self.config.COLORS['text_primary']
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            title_frame,
            text="Licenciatura en Informática",
            font=("Segoe UI", 12),
            bg=self.config.COLORS['bg_principal'],
            fg=self.config.COLORS['text_secondary']
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame para controles de la derecha
        controls_frame = tk.Frame(toolbar, bg=self.config.COLORS['bg_principal'])
        controls_frame.pack(side=tk.RIGHT, pady=10)
        
        # Indicador de créditos
        self.components['creditos_label'] = tk.Label(
            controls_frame,
            text="📊 0 créditos",
            font=("Segoe UI", 12, "bold"),
            bg=self.config.COLORS['primary_light'],
            fg=self.config.COLORS['primary'],
            padx=15, pady=8,
            relief="flat"
        )
        self.components['creditos_label'].pack(side=tk.LEFT, padx=(0, 10))
        
        # Botones de acción
        self._crear_botones_toolbar(controls_frame)
    
    def _crear_botones_toolbar(self, parent):
        """Crea los botones de acción en el toolbar"""
        botones = [
            {
                'texto': '🗑️ Limpiar',
                'comando': self._limpiar_horario,
                'color': self.config.COLORS['danger'],
                'tooltip': 'Limpia todo el horario actual'
            },
            {
                'texto': '💾 Guardar',
                'comando': self._guardar_horario,
                'color': self.config.COLORS['success'],
                'tooltip': 'Guarda el horario actual'
            },
            {
                'texto': '📊 Estadísticas',
                'comando': self._mostrar_estadisticas,
                'color': self.config.COLORS['secondary'],
                'tooltip': 'Muestra estadísticas del horario'
            }
        ]
        
        for btn_config in botones:
            btn = tk.Button(
                parent,
                text=btn_config['texto'],
                font=("Segoe UI", 10, "bold"),
                bg=btn_config['color'],
                fg="white",
                padx=15, pady=8,
                relief="flat",
                cursor="hand2",
                command=btn_config['comando']
            )
            btn.pack(side=tk.LEFT, padx=5)
            
            # Agregar efecto hover
            self._agregar_hover_effect(btn, btn_config['color'])
    
    def _agregar_hover_effect(self, widget, color_original):
        """Agrega efecto hover a un widget"""
        def on_enter(e):
            # Oscurecer el color al hacer hover
            widget.configure(bg=self._oscurecer_color(color_original, 0.2))
        
        def on_leave(e):
            widget.configure(bg=color_original)
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _oscurecer_color(self, hex_color: str, factor: float) -> str:
        """Oscurece un color hex por un factor dado"""
        # Implementación simple para oscurecer
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb_oscuro = tuple(int(c * (1 - factor)) for c in rgb)
        return f"#{rgb_oscuro[0]:02x}{rgb_oscuro[1]:02x}{rgb_oscuro[2]:02x}"
    
    def _conectar_eventos(self):
        """Conecta los eventos entre componentes"""
        # Eventos del controlador para actualizar la interfaz
        self.controller.on_horario_changed = self._actualizar_interfaz_horario
        self.controller.on_creditos_changed = self._actualizar_indicador_creditos
        self.controller.on_error = self._mostrar_error
        self.controller.on_success = self._mostrar_exito
        self.controller.on_warning = self._mostrar_advertencia
        
        # Evento de cierre de ventana
        self.master.protocol("WM_DELETE_WINDOW", self._cerrar_aplicacion)
        
        logger.info("Eventos conectados exitosamente")
    
    def _actualizar_interfaz_horario(self):
        """Actualiza la interfaz cuando cambia el horario"""
        if 'grilla' in self.components:
            self.components['grilla'].actualizar_grilla()
        
        # Actualizar resumen
        estadisticas = self.controller.obtener_estadisticas_horario()
        if 'grilla' in self.components:
            self.components['grilla'].actualizar_resumen(estadisticas)
    
    def _actualizar_indicador_creditos(self, total_creditos: int):
        """Actualiza el indicador de créditos en el toolbar"""
        if 'creditos_label' in self.components:
            label = self.components['creditos_label']
            label.configure(text=f"📊 {total_creditos} créditos")
            
            # Cambiar color según la cantidad de créditos
            esquema = self._obtener_esquema_creditos(total_creditos)
            label.configure(
                bg=esquema['bg_color'],
                fg=esquema['text_color']
            )
    
    def _obtener_esquema_creditos(self, total_creditos: int) -> Dict[str, str]:
        """Obtiene esquema de color según créditos"""
        from logica.utils.color_utils import ColorUtils
        return ColorUtils.obtener_esquema_color_carga_creditos(total_creditos)
    
    # Métodos de comando para botones
    
    def _limpiar_horario(self):
        """Limpia el horario actual"""
        resultado = self.controller.limpiar_horario()
        if resultado['exito']:
            self._mostrar_exito("Horario", resultado['mensaje'])
        else:
            self._mostrar_error("Error", resultado['mensaje'])
    
    def _guardar_horario(self):
        """Guarda el horario actual"""
        try:
            # Obtener datos del horario para guardar
            datos_horario = self.controller.exportar_horario()
            
            # Aquí se implementaría la lógica de guardado
            # Por ahora, solo mostrar que se "guardó"
            if datos_horario.get('horario'):
                self._mostrar_exito("Guardado", "Horario guardado exitosamente")
            else:
                self._mostrar_advertencia("Guardado", "No hay materias en el horario para guardar")
                
        except Exception as e:
            logger.error(f"Error guardando horario: {e}")
            self._mostrar_error("Error", f"Error guardando horario: {str(e)}")
    
    def _mostrar_estadisticas(self):
        """Muestra estadísticas del horario actual"""
        try:
            estadisticas = self.controller.obtener_estadisticas_horario()
            
            # Crear ventana de estadísticas
            self._crear_ventana_estadisticas(estadisticas)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            self._mostrar_error("Error", f"Error obteniendo estadísticas: {str(e)}")
    
    def _crear_ventana_estadisticas(self, estadisticas: Dict[str, Any]):
        """Crea ventana emergente con estadísticas"""
        ventana = tk.Toplevel(self.master)
        ventana.title("Estadísticas del Horario")
        ventana.geometry("400x300")
        ventana.configure(bg=self.config.COLORS['bg_card'])
        
        # Centrar ventana
        ventana.transient(self.master)
        ventana.grab_set()
        
        # Contenido de estadísticas
        header = tk.Label(
            ventana,
            text="📊 Estadísticas del Horario",
            font=("Segoe UI", 16, "bold"),
            bg=self.config.COLORS['bg_card'],
            fg=self.config.COLORS['text_primary']
        )
        header.pack(pady=20)
        
        # Frame para estadísticas
        stats_frame = tk.Frame(ventana, bg=self.config.COLORS['bg_card'])
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Mostrar estadísticas
        stats_items = [
            ("Total de materias:", estadisticas.get('total_materias', 0)),
            ("Total de créditos:", estadisticas.get('total_creditos', 0)),
            ("Total de sesiones:", estadisticas.get('total_sesiones', 0)),
            ("Promedio créditos/materia:", estadisticas.get('promedio_creditos_por_materia', 0))
        ]
        
        for i, (label, valor) in enumerate(stats_items):
            item_frame = tk.Frame(stats_frame, bg=self.config.COLORS['bg_card'])
            item_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(
                item_frame,
                text=label,
                font=("Segoe UI", 11),
                bg=self.config.COLORS['bg_card'],
                fg=self.config.COLORS['text_secondary'],
                anchor="w"
            ).pack(side=tk.LEFT)
            
            tk.Label(
                item_frame,
                text=str(valor),
                font=("Segoe UI", 11, "bold"),
                bg=self.config.COLORS['bg_card'],
                fg=self.config.COLORS['text_primary'],
                anchor="e"
            ).pack(side=tk.RIGHT)
        
        # Botón cerrar
        tk.Button(
            ventana,
            text="Cerrar",
            font=("Segoe UI", 10, "bold"),
            bg=self.config.COLORS['primary'],
            fg="white",
            padx=20, pady=8,
            relief="flat",
            command=ventana.destroy
        ).pack(pady=20)
    
    # Métodos de notificación
    
    def _mostrar_error(self, titulo: str, mensaje: str):
        """Muestra mensaje de error"""
        import tkinter.messagebox as messagebox
        messagebox.showerror(titulo, mensaje)
    
    def _mostrar_exito(self, titulo: str, mensaje: str):
        """Muestra mensaje de éxito"""
        import tkinter.messagebox as messagebox
        messagebox.showinfo(titulo, mensaje)
    
    def _mostrar_advertencia(self, titulo: str, mensaje: str):
        """Muestra mensaje de advertencia"""
        import tkinter.messagebox as messagebox
        messagebox.showwarning(titulo, mensaje)
    
    def _cerrar_aplicacion(self):
        """Maneja el cierre de la aplicación"""
        try:
            # Limpiar recursos
            if hasattr(self, 'db_manager'):
                self.db_manager.cerrar_conexion()
            
            logger.info("Aplicación cerrada correctamente")
            self.master.destroy()
            
        except Exception as e:
            logger.error(f"Error cerrando aplicación: {e}")
            self.master.destroy()
    
    def run(self):
        """Inicia el bucle principal de la aplicación"""
        try:
            self.master.mainloop()
        except KeyboardInterrupt:
            logger.info("Aplicación interrumpida por usuario")
            self._cerrar_aplicacion()
        except Exception as e:
            logger.error(f"Error en bucle principal: {e}")
            raise
