"""
Componente de notificación tipo "Toast" o "Snackbar" para customtkinter.
"""

import customtkinter as ctk
from typing import Optional

class NotificationToast(ctk.CTkToplevel):
    """
    Una ventana de notificación discreta que aparece en una esquina y se desvanece.
    """
    def __init__(
        self,
        parent,
        title: str,
        message: str,
        duration: int = 3000,
        notification_type: str = "info", # "info", "success", "warning", "error"
        position: str = "bottom_right" # "top_right", "bottom_right", etc.
    ):
        super().__init__(parent)
        self.parent = parent
        self.duration = duration
        self.position = position

        # Configuración de la ventana
        self.overrideredirect(True) # Sin bordes ni barra de título
        self.attributes("-topmost", True) # Siempre visible
        self.attributes("-alpha", 0.0) # Inicia transparente

        # Colores según el tipo de notificación
        colors = {
            "info": ("#3B82F6", "#FFFFFF"),      # Azul (primary)
            "success": ("#10B981", "#FFFFFF"),   # Verde (success)
            "warning": ("#F59E0B", "#111827"),   # Amarillo (warning)
            "error": ("#EF4444", "#FFFFFF")       # Rojo (danger)
        }
        bg_color, text_color = colors.get(notification_type, colors["info"])

        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=bg_color, corner_radius=8, border_width=1, border_color=bg_color)
        main_frame.pack(expand=True, fill="both")

        # Contenido
        title_label = ctk.CTkLabel(
            main_frame,
            text=title,
            font=("Segoe UI", 12, "bold"),
            text_color=text_color,
            anchor="w"
        )
        title_label.pack(padx=15, pady=(10, 2), fill="x")

        message_label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=("Segoe UI", 10),
            text_color=text_color,
            wraplength=280,
            justify="left",
            anchor="w"
        )
        message_label.pack(padx=15, pady=(0, 10), fill="x")

        # Posicionar la ventana
        self._set_position()

        # Iniciar animación
        self.after(100, self.fade_in)

    def _set_position(self):
        """Calcula y establece la posición de la notificación en la pantalla."""
        self.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        toast_width = self.winfo_width()
        toast_height = self.winfo_height()

        # Por ahora, solo implementamos 'bottom_right'
        x = parent_x + parent_width - toast_width - 20
        y = parent_y + parent_height - toast_height - 20
        
        self.geometry(f"{toast_width}x{toast_height}+{x}+{y}")

    def fade_in(self):
        """Animación de aparición gradual."""
        alpha = self.attributes("-alpha")
        if alpha < 0.95:
            self.attributes("-alpha", alpha + 0.05)
            self.after(20, self.fade_in)
        else:
            self.after(self.duration, self.fade_out)

    def fade_out(self):
        """Animación de desaparición gradual."""
        alpha = self.attributes("-alpha")
        if alpha > 0.0:
            self.attributes("-alpha", alpha - 0.05)
            self.after(20, self.fade_out)
        else:
            self.destroy()
