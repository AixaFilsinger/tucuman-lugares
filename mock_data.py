
import httpx
import time

API_URL = "http://localhost:8000"

LUGARES_MOCK = [
    {"nombre": "PIPA pizzería", "ubicacion": "José Rondeau 1011, Tucumán", "fuente": "mock"},
    {"nombre": "Bar Irlanda Tucumán", "ubicacion": "cATAMARCA 380, Tucumán", "fuente": "mock"},
    {"nombre": "Dot Bar", "ubicacion": "Ildefonso de las Muñecas 643, Tucumán", "fuente": "mock"},
    {"nombre": "Mr. JOHN'S & WARHOL", "ubicacion": "Av. Aconquija 1702, Tucumán", "fuente": "mock"},
    {"nombre": "La Leñita Restaurante", "ubicacion": "Gral. José de San Martín 389, Tucumán", "fuente": "mock"},
    {"nombre": "Restó Boris", "ubicacion": "San Juan 1131, Tucumán", "fuente": "mock"},
    {"nombre": "José Cuervo", "ubicacion": "Miguel Lillo 352, Tucumán", "fuente": "mock"},
    {"nombre": "Patio Sur", "ubicacion": "Gral. José María Paz 540", "fuente": "mock"},
    {"nombre": "24 Street Coffee & Beer", "ubicacion": "Av. 24 de Septiembre & Junín, Tucumán", "fuente": "mock"},
    {"nombre": "Monasterio", "ubicacion": "Gral. José María Paz 516, Tucumán", "fuente": "mock"},
]

def cargar_datos():
    print(" Iniciando carga de datos mock...\n")
    exitosos = 0
    errores = 0

    for lugar in LUGARES_MOCK:
        try:
            res = httpx.post(f"{API_URL}/lugares", json=lugar, timeout=30)
            if res.status_code == 201:
                data = res.json()
                print(f" {data['nombre']} → categoría: {data['categoria']}")
                exitosos += 1
            elif res.status_code == 409:
                print(f"  Duplicado saltado: {lugar['nombre']}")
            else:
                print(f" Error en {lugar['nombre']}: {res.text}")
                errores += 1
            time.sleep(1)  # Pausa para no saturar la API de IA
        except Exception as e:
            print(f" Excepción en {lugar['nombre']}: {e}")
            errores += 1

    print(f"\n Resultado: {exitosos} cargados, {errores} errores")

if __name__ == "__main__":
    cargar_datos()