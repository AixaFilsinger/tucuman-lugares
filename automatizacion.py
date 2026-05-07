
import httpx
import time
import json
from datetime import datetime
from ia import clasificar_lugar, generar_descripcion

API_URL = "http://localhost:8000"
LOG_FILE = "logs.json"

# ── simular scraping/API externa) ──────
FUENTE_NUEVA = [
    {"nombre": "Antares Tucumán", "ubicacion": "Av. Soldati 401, Tucumán", "fuente": "mock"},
    {"nombre": "Bar El Cairo", "ubicacion": "Córdoba 21, Tucumán", "fuente": "mock"},
    {"nombre": "Café del Convento", "ubicacion": "Congreso 1, Tucumán", "fuente": "mock"},
    {"nombre": "La Yunta Parrilla", "ubicacion": "Av. Mitre 900, Tucumán", "fuente": "mock"},
    {"nombre": "Irlanda Bar", "ubicacion": "San Martín 500, Tucumán", "fuente": "mock"},
    {"nombre": "Boliche Sobretodo", "ubicacion": "Av. Roca 750, Tucumán", "fuente": "mock"},
    {"nombre": "El Porteño Bar", "ubicacion": "Las Piedras 480, Tucumán", "fuente": "mock"},
]

def guardar_log(resultado: dict):
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append(resultado)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def ejecutar_flujo():
    print("=" * 50)
    print(f" Iniciando flujo — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    resultado = {
        "fecha": datetime.now().isoformat(),
        "total_procesados": 0,
        "insertados": 0,
        "duplicados": 0,
        "errores": 0,
        "detalle": []
    }

    for lugar in FUENTE_NUEVA:
        resultado["total_procesados"] += 1
        nombre = lugar["nombre"]
        print(f"\n Procesando: {nombre}")

        try:
            print(f"    Clasificando con IA...")
            categoria = clasificar_lugar(nombre, lugar.get("ubicacion", ""))
            descripcion = generar_descripcion(nombre, categoria, lugar.get("ubicacion", ""))
            print(f"    Categoría: {categoria}")

            datos = {
                "nombre": nombre,
                "ubicacion": lugar.get("ubicacion"),
                "fuente": lugar.get("fuente", "automatizacion"),
                "categoria": categoria,
                "descripcion": descripcion,
            }

            res = httpx.post(f"{API_URL}/lugares", json=datos, timeout=30)

            if res.status_code == 201:
                print(f"   Insertado correctamente")
                resultado["insertados"] += 1
                resultado["detalle"].append({
                    "nombre": nombre,
                    "estado": "insertado",
                    "categoria": categoria
                })

            elif res.status_code == 409:
                motivo = res.json().get("detail", "Duplicado")
                print(f"   ⚠️  Duplicado saltado: {motivo}")
                resultado["duplicados"] += 1
                resultado["detalle"].append({
                    "nombre": nombre,
                    "estado": "duplicado",
                    "motivo": motivo
                })

            else:
                print(f"   Error: {res.text}")
                resultado["errores"] += 1
                resultado["detalle"].append({
                    "nombre": nombre,
                    "estado": "error",
                    "motivo": res.text
                })

        except Exception as e:
            print(f"    Excepción: {e}")
            resultado["errores"] += 1
            resultado["detalle"].append({
                "nombre": nombre,
                "estado": "error",
                "motivo": str(e)
            })

        time.sleep(10)

    guardar_log(resultado)

    print("\n" + "=" * 50)
    print("# RESUMEN DEL FLUJO")
    print("=" * 50)
    print(f"   Total procesados : {resultado['total_procesados']}")
    print(f"   * Insertados     : {resultado['insertados']}")
    print(f"     Duplicados     : {resultado['duplicados']}")
    print(f"   x Errores        : {resultado['errores']}")
    print(f"    Log guardado   : {LOG_FILE}")
    print("=" * 50)

    return resultado

if __name__ == "__main__":
    ejecutar_flujo()