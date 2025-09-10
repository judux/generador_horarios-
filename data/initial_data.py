"""
Datos iniciales para poblar la base de datos
"""

MATERIAS_INICIALES = [
    {
        "codigo": "9797",
        "nombre": "ADMINISTRACION EDUCATIVA",
        "grupos": [{
            "nombre_grupo": "Grupo 1",
            "tipo_sesion_predominante": "TEORICA",
            "docente": "HERRERA FIGUEROA EDGAR HUMBERTO",
            "sesiones": [
                {"dia": "Jueves", "inicio": "15:00", "fin": "17:00", "salon": "Aula A306 (BLOQUE 3)"},
                {"dia": "Viernes", "inicio": "13:00", "fin": "15:00", "salon": "Aula A306 (BLOQUE 3)"}
            ]
        }]
    },
    {
        "codigo": "9807",
        "nombre": "AMBIENTES DE APRENDIZAJE",
        "grupos": [{
            "nombre_grupo": "Grupo 1",
            "tipo_sesion_predominante": "PRACTICA",
            "docente": "JOJOA JOJOA HAROLD ANTONIO",
            "sesiones": [
                {"dia": "Miércoles", "inicio": "11:00", "fin": "13:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"},
                {"dia": "Jueves", "inicio": "09:00", "fin": "11:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]
        }]
    },
    {
        "codigo": "9790",
        "nombre": "AMBIENTES VIRTUALES DE APRENDIZAJE",
        "grupos": [
            {
                "nombre_grupo": "Grupo 1",
                "tipo_sesion_predominante": "TEORICA",
                "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO",
                "sesiones": [
                    {"dia": "Lunes", "inicio": "11:00", "fin": "13:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
                ]
            },
            {
                "nombre_grupo": "Grupo 2",
                "tipo_sesion_predominante": "PRACTICA",
                "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO",
                "sesiones": [
                    {"dia": "Martes", "inicio": "11:00", "fin": "13:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
                ]
            }
        ]
    },
    {
        "codigo": "9788",
        "nombre": "APLICACIONES WEB",
        "grupos": [{
            "nombre_grupo": "Grupo 1",
            "tipo_sesion_predominante": "PRACTICA",
            "docente": "JATIVA ERAZO JAIRO OMAR",
            "sesiones": [
                {"dia": "Martes", "inicio": "07:00", "fin": "09:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"},
                {"dia": "Miércoles", "inicio": "07:00", "fin": "09:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
            ]
        }]
    },
    {
        "codigo": "9789",
        "nombre": "APLICACIONES WEB EN SERVIDOR",
        "grupos": [{
            "nombre_grupo": "Grupo 1",
            "tipo_sesion_predominante": "PRACTICA",
            "docente": "NARVAEZ CALVACHE DARIO FAVIER",
            "sesiones": [
                {"dia": "Martes", "inicio": "09:00", "fin": "11:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"},
                {"dia": "Miércoles", "inicio": "09:00", "fin": "11:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
            ]
        }]
    },
    {
        "codigo": "9808",
        "nombre": "COMUNICACION Y REDES",
        "grupos": [{
            "nombre_grupo": "Grupo 1",
            "tipo_sesion_predominante": "PRACTICA",
            "docente": "CARLOS FERNANDO GONZALEZ GUZMAN",
            "sesiones": [
                {"dia": "Lunes", "inicio": "17:00", "fin": "19:00", "salon": "Aula A408 (BLOQUE TECNOLOGICO)"},
                {"dia": "Miércoles", "inicio": "15:00", "fin": "17:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]
        }]
    },
    {
        "codigo": "9791",
        "nombre": "COMUNICACION VISUAL",
        "grupos": [
            {
                "nombre_grupo": "Grupo 1",
                "tipo_sesion_predominante": "TEORICA",
                "docente": "PAZ SAAVEDRA LUIS EDUARDO",
                "sesiones": [
                    {"dia": "Jueves", "inicio": "17:00", "fin": "19:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
                ]
            },
            {
                "nombre_grupo": "Grupo 2",
                "tipo_sesion_predominante": "PRACTICA",
                "docente": "PAZ SAAVEDRA LUIS EDUARDO",
                "sesiones": [
                    {"dia": "Viernes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
                ]
            }
        ]
    },
    {
        "codigo": "8320",
        "nombre": "CORRIENTES PEDAGOGICAS",
        "grupos": [{
            "nombre_grupo": "Grupo 1",
            "tipo_sesion_predominante": "TEORICA",
            "docente": "JATIVA ERAZO JAIRO OMAR",
            "sesiones": [
                {"dia": "Jueves", "inicio": "09:00", "fin": "11:00", "salon": "Aula A303 (BLOQUE 3)"},
                {"dia": "Viernes", "inicio": "09:00", "fin": "11:00", "salon": "Aula A303 (BLOQUE 3)"}
            ]
        }]
    },
    {
        "codigo": "9785",
        "nombre": "DESARROLLO DE SOFTWARE",
        "grupos": [
            {
                "nombre_grupo": "Grupo 1",
                "tipo_sesion_predominante": "TEORICA",
                "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO",
                "sesiones": [
                    {"dia": "Martes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
                ]
            },
            {
                "nombre_grupo": "Grupo 2",
                "tipo_sesion_predominante": "PRACTICA",
                "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO",
                "sesiones": [
                    {"dia": "Miércoles", "inicio": "15:00", "fin": "17:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
                ]
            }
        ]
    },
    {
        "codigo": "9787",
        "nombre": "DESARROLLO DE SOFTWARE EDUCATIVO",
        "grupos": [
            {
                "nombre_grupo": "Grupo 2",
                "tipo_sesion_predominante": "TEORICA",
                "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO",
                "sesiones": [
                    {"dia": "Miércoles", "inicio": "13:00", "fin": "15:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
                ]
            },
            {
                "nombre_grupo": "Grupo 1",
                "tipo_sesion_predominante": "PRACTICA",
                "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO",
                "sesiones": [
                    {"dia": "Viernes", "inicio": "13:00", "fin": "15:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
                ]
            }
        ]
    },
    {
        "codigo": "4553",
        "nombre": "DIDACTICA DE LA INFORMATICA",
        "grupos": [{
            "nombre_grupo": "Grupo 1",
            "tipo_sesion_predominante": "TEORICA",
            "docente": "DELGADO ACHICANOY NATALIA FERNANDA",
            "sesiones": [
                {"dia": "Lunes", "inicio": "17:00", "fin": "19:00", "salon": "Aula A301 (Bloque 1 Sur B)"},
                {"dia": "Jueves", "inicio": "15:00", "fin": "17:00", "salon": "Aula A302 (BLOQUE 3)"}
            ]
        }]
    },
    {
        "codigo": "9786",
        "nombre": "DISEÑO GRAFICO Y ANIMACION",
        "grupos": [{
            "nombre_grupo": "Grupo 1",
            "tipo_sesion_predominante": "PRACTICA",
            "docente": "DELGADO ACHICANOY NATALIA FERNANDA",
            "sesiones": [
                {"dia": "Lunes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"},
                {"dia": "Jueves", "inicio": "17:00", "fin": "19:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]
        }]
    },
    {
        "codigo": "FHILO_ED_SC",
        "nombre": "FILOSOFIA E HISTORIA DE LA EDUCACION",
        "grupos": [{
            "nombre_grupo": "Grupo 1",
            "tipo_sesion_predominante": "TEORICA",
            "docente": "PAZ SAAVEDRA LUIS EDUARDO",
            "sesiones": [
                {"dia": "Miércoles", "inicio": "13:00", "fin": "15:00", "salon": "Aula A402 (Bloque 1 Sur B)"},
                {"dia": "Jueves", "inicio": "13:00", "fin": "15:00", "salon": "Aula A102 (BLOQUE 3)"}
            ]
        }]
    },
    {
        "codigo": "6537",
        "nombre": "HARDWARE Y SISTEMAS OPERATIVOS",
        "grupos": [
            {
                "nombre_grupo": "Grupo 1",
                "tipo_sesion_predominante": "TEORICA",
                "docente": "ROSERO CALDERON OSCAR ANDRES",
                "sesiones": [
                    {"dia": "Lunes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"},
                    {"dia": "Jueves", "inicio": "17:00", "fin": "19:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
                ]
            },
            {
                "nombre_grupo": "Grupo 2",
                "tipo_sesion_predominante": "TEORICA",
                "docente": "ROSERO CALDERON OSCAR ANDRES",
                "sesiones": [
                    {"dia": "Lunes", "inicio": "17:00", "fin": "19:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"},
                    {"dia": "Jueves", "inicio": "15:00", "fin": "17:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
                ]
            }
        ]
    },
    {
        "codigo": "9809",
        "nombre": "INVESTIGACION CUALITATIVA",
        "grupos": [
            {
                "nombre_grupo": "Grupo 1",
                "tipo_sesion_predominante": "TEORICA",
                "docente": "JOJOA JOJOA HAROLD ANTONIO",
                "sesiones": [
                    {"dia": "Martes", "inicio": "13:00", "fin": "15:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
                ]
            },
            {
                "nombre_grupo": "Grupo 2",
                "tipo_sesion_predominante": "PRACTICA",
                "docente": "JOJOA JOJOA HAROLD ANTONIO",
                "sesiones": [
                    {"dia": "Viernes", "inicio": "09:00", "fin": "11:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
                ]
            }
        ]
    }
]
