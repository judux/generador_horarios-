"""
Administrador de conexiones a la base de datos
"""

import sqlite3
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Generator

from config.database_config import DatabaseConfig

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Administrador centralizado de conexiones a la base de datos"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.config.ensure_database_dir()
        self._connection: Optional[sqlite3.Connection] = None
    
    def crear_conexion(self) -> Optional[sqlite3.Connection]:
        """Crea una nueva conexión a la base de datos"""
        try:
            conn = sqlite3.connect(
                str(self.config.database_path),
                timeout=self.config.CONNECTION_CONFIG['timeout'],
                check_same_thread=self.config.CONNECTION_CONFIG['check_same_thread'],
                isolation_level=self.config.CONNECTION_CONFIG['isolation_level']
            )
            
            # Aplicar configuraciones PRAGMA
            for pragma in self.config.PRAGMA_SETTINGS:
                conn.execute(pragma)
            
            logger.info(f"Conexión exitosa a la base de datos: {self.config.database_path}")
            return conn
            
        except sqlite3.Error as e:
            logger.error(f"Error al conectar con la base de datos: {e}")
            return None
    
    def obtener_conexion(self) -> sqlite3.Connection:
        """Obtiene la conexión principal, la crea si no existe"""
        if self._connection is None:
            self._connection = self.crear_conexion()
        
        if self._connection is None:
            raise RuntimeError("No se pudo establecer conexión con la base de datos")
        
        return self._connection
    
    @contextmanager
    def transaccion(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager para transacciones automáticas"""
        conn = self.obtener_conexion()
        try:
            conn.execute("BEGIN")
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error en transacción, rollback ejecutado: {e}")
            raise
    
    @contextmanager
    def cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Context manager para cursores"""
        conn = self.obtener_conexion()
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    def verificar_conexion(self) -> bool:
        """Verifica que la conexión a la base de datos funcione"""
        try:
            with self.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Verificación de conexión fallida: {e}")
            return False
    
    def cerrar_conexion(self):
        """Cierra la conexión principal si existe"""
        if self._connection:
            try:
                self._connection.close()
                logger.info("Conexión a base de datos cerrada")
            except sqlite3.Error as e:
                logger.error(f"Error al cerrar conexión: {e}")
            finally:
                self._connection = None
    
    def obtener_info_base_datos(self) -> dict:
        """Obtiene información sobre el estado de la base de datos"""
        try:
            with self.cursor() as cursor:
                # Verificar si las tablas principales existen
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('Materias', 'GruposMateria', 'SesionesClase')
                """)
                tablas_existentes = [row[0] for row in cursor.fetchall()]
                
                # Contar registros en cada tabla
                conteos = {}
                for tabla in tablas_existentes:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    conteos[tabla] = cursor.fetchone()[0]
                
                return {
                    'database_path': str(self.config.database_path),
                    'database_exists': self.config.database_path.exists(),
                    'tablas_existentes': tablas_existentes,
                    'conteo_registros': conteos,
                    'conexion_activa': self._connection is not None
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo información de BD: {e}")
            return {'error': str(e)}
    
    def ejecutar_query(self, query: str, params: tuple = ()) -> list:
        """Ejecuta una query SELECT y retorna los resultados"""
        try:
            with self.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error ejecutando query: {e}")
            raise
    
    def ejecutar_comando(self, comando: str, params: tuple = ()) -> int:
        """Ejecuta un comando INSERT/UPDATE/DELETE y retorna filas afectadas"""
        try:
            with self.transaccion() as conn:
                cursor = conn.cursor()
                cursor.execute(comando, params)
                return cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Error ejecutando comando: {e}")
            raise
    
    def __enter__(self):
        """Entrada del context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Salida del context manager"""
        self.cerrar_conexion()
