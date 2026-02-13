"""
Utilidades para formateo de datos
"""
import pytz
from datetime import datetime


# Zona horaria de Bogotá, Colombia
bogota_tz = pytz.timezone('America/Bogota')


def obtener_fecha_bogota():
    """Retorna la fecha y hora actual de Bogotá, Colombia"""
    return datetime.now(bogota_tz)


def formato_pesos(valor):
    """
    Formatea un número como pesos colombianos: $1.234.567
    
    Args:
        valor: Número a formatear
        
    Returns:
        String formateado como pesos colombianos
    """
    if valor is None:
        valor = 0
    valor = int(float(valor))
    entero = str(valor)

    entero_formateado = ""
    for i, digito in enumerate(reversed(entero)):
        if i > 0 and i % 3 == 0:
            entero_formateado = "." + entero_formateado
        entero_formateado = digito + entero_formateado

    return f"${entero_formateado}"


def allowed_file(filename, allowed_extensions):
    """
    Verifica si un archivo tiene una extensión permitida
    
    Args:
        filename: Nombre del archivo
        allowed_extensions: Set de extensiones permitidas
        
    Returns:
        Boolean indicando si el archivo es permitido
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
