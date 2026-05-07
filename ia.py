import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.0-flash"

def clasificar_lugar(nombre: str, ubicacion: str = "") -> str:
    # 1. Primero intenta con reglas
    nombre_lower = nombre.lower()
    reglas = {
        "bar": ["bar", "pub", "taberna", "cervecería", "birra"],
        "boliche": ["boliche", "disco", "club", "dance", "bailable"],
        "café": ["café", "cafe", "cafetería", "cafeteria", "coffee", "tea"],
        "restaurante": ["restaurante", "restó", "resto", "pizzería", "pizza", 
                       "parrilla", "grill", "comedor", "bodegón", "sushi",
                       "hamburguesería", "burger", "cocina"],
        "recital": ["recital", "show", "teatro", "music", "jazz", "rock"],
        "cultural": ["cultural", "museo", "galería", "galeria", "arte", "espacio"],
    }
    
    for categoria, palabras in reglas.items():
        for palabra in palabras:
            if palabra in nombre_lower:
                return categoria
    
    # 2. Si no matchea por reglas, intentar con IA (Prompt detallado)
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=f"""Sos un experto en locales nocturnos y gastronómicos de Tucumán, Argentina.
Clasificá este lugar en UNA de estas categorías: bar, boliche, café, restaurante, recital, cultural, otro.

Lugar: "{nombre}"
Ubicación: "{ubicacion}"

Ejemplos:
- "Bar Irlanda" → bar
- "24 Street Coffee & Beer" → café
- "PIPA pizzería" → restaurante
- "Mr. JOHN'S & WARHOL" → boliche

Respondé SOLO con la categoría en minúsculas, sin puntos ni explicaciones."""
        )
        
        resultado = response.text.strip().lower()
        categorias_validas = ["bar", "boliche", "café", "restaurante", "recital", "cultural", "otro"]
        
        for cat in categorias_validas:
            if cat in resultado:
                return cat
        return "otro"
        
    except Exception as e:
        print(f"Error clasificando con IA: {e}")
        return "otro"

def generar_descripcion(nombre: str, categoria: str, ubicacion: str = "") -> str:
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=f"""Generá una descripción corta, atractiva y en español rioplatense (máximo 2 oraciones) para este lugar de Tucumán, Argentina.
La descripción debe sonar natural, como si fuera para una app de recomendaciones.

Nombre: {nombre}
Categoría: {categoria}
Ubicación: {ubicacion}

Escribí SOLO la descripción, sin comillas, sin aclaraciones."""
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error generando descripción: {e}")
        return ""

def detectar_duplicado(nombre_nuevo: str, nombre_existente: str) -> bool:
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=f"""¿Estos dos nombres de lugares en Tucumán, Argentina, hacen referencia al mismo local?
Considerá variaciones de nombre, abreviaciones, orden de palabras distinto.

A: "{nombre_nuevo}"
B: "{nombre_existente}"

Ejemplos de duplicados:
- "Bar Irlanda Tucumán" y "Irlanda Bar" → SI
- "El Federal" y "Federal Bar" → SI
- "La Leñita" y "PIPA pizzería" → NO

Respondé SOLO con SI o NO."""
        )
        respuesta = response.text.strip().upper()
        return "SI" in respuesta or "SÍ" in respuesta
    except Exception as e:
        print(f"Error detectando duplicado: {e}")
        return False

def limpiar_nombre(nombre: str) -> str:
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=f"""Limpiá y normalizá este nombre de local de Tucumán.
Corregí mayúsculas, eliminá caracteres raros, dejalo prolijo.
Nombre original: "{nombre}"
Respondé SOLO con el nombre limpio, sin explicaciones."""
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error limpiando nombre: {e}")
        return nombre