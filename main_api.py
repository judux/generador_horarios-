import sys
from pathlib import Path
print("--- INICIANDO VERSIÓN MÁS RECIENTE DEL SERVIDOR ---")

from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add project root to the Python path
# This is necessary to ensure that modules like 'logica' and 'database' can be found
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from database.connection import DatabaseManager
from logica.services.materia_service import MateriaService
from database.repositories.grupo_repository import GrupoRepository

# --- App Definition ---
app = FastAPI(
    title="API de Horarios Udenar",
    description="API para gestionar la creación y consulta de horarios académicos.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes. En producción, esto debería ser más restrictivo.
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todas las cabeceras
)

# --- Static Files ---
# Mount the 'assets' directory to be accessible at '/static'
app.mount("/static", StaticFiles(directory=project_root / "assets"), name="static")

# --- Database Dependency ---
# Dependency function to get a database manager for each request
def get_db_manager():
    db = DatabaseManager()
    try:
        yield db
    finally:
        db.cerrar_conexion()

# --- API Endpoints ---

@app.get("/")
def read_root():
    """
    Endpoint de bienvenida que devuelve un mensaje de saludo.
    """
    return {"message": "Bienvenido a la API del proyecto de horarios"}



@app.get("/materias")
def obtener_materias_filtradas(db: DatabaseManager = Depends(get_db_manager)):
    """
    Obtiene una lista de todas las materias.
    """
    materia_service = MateriaService(db)
    materias = materia_service.obtener_todas_las_materias()
    return materias

@app.get("/materias/buscar")
def buscar_materias(term: str, db: DatabaseManager = Depends(get_db_manager)):
    """
    Busca materias por un término de búsqueda.
    """
    materia_service = MateriaService(db)
    todas_las_materias = materia_service.obtener_todas_las_materias()
    
    # Filtramos en Python por simplicidad
    termino_lower = term.lower()
    materias_encontradas = [ 
        m for m in todas_las_materias 
        if termino_lower in m['nombre'].lower() or termino_lower in m['codigo'].lower()
    ]
    
    return materias_encontradas

@app.get("/materias/{codigo_materia}")
def obtener_detalles_materia(codigo_materia: str, db: DatabaseManager = Depends(get_db_manager)):
    """
    Obtiene los detalles completos de una materia, incluyendo grupos y sesiones.
    """
    materia_service = MateriaService(db)
    detalles = materia_service.obtener_detalle_materia(codigo_materia)
    if detalles is None:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    return detalles


