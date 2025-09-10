"""
Clase base para todos los repositorios
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Tuple
from database.connection import DatabaseManager

logger = logging.getLogger(__name__)

class BaseRepository(ABC):
    """Clase base abstracta para todos los repositorios"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def _ejecutar_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Ejecuta una query SELECT y retorna los resultados"""
        try:
            with self.db_manager.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error ejecutando query: {query}, params: {params}, error: {e}")
            raise
    
    def _ejecutar_comando(self, comando: str, params: Tuple = ()) -> int:
        """Ejecuta un comando INSERT/UPDATE/DELETE y retorna el ID o filas afectadas"""
        try:
            with self.db_manager.transaccion() as conn:
                cursor = conn.cursor()
                cursor.execute(comando, params)
                return cursor.lastrowid or cursor.rowcount
        except Exception as e:
            logger.error(f"Error ejecutando comando: {comando}, params: {params}, error: {e}")
            raise
    
    def _existe_registro(self, tabla: str, campo: str, valor: Any) -> bool:
        """Verifica si existe un registro en una tabla"""
        query = f"SELECT 1 FROM {tabla} WHERE {campo} = ? LIMIT 1"
        resultado = self._ejecutar_query(query, (valor,))
        return len(resultado) > 0
    
    def _contar_registros(self, tabla: str, condicion: str = "1=1", params: Tuple = ()) -> int:
        """Cuenta registros en una tabla con condición opcional"""
        query = f"SELECT COUNT(*) FROM {tabla} WHERE {condicion}"
        resultado = self._ejecutar_query(query, params)
        return resultado[0][0] if resultado else 0
