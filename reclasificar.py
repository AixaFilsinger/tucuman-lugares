
import httpx
import time

import httpx

API_URL = "http://localhost:8000"

def reclasificar():
    res = httpx.get(f"{API_URL}/lugares", params={"solo_activos": True})
    lugares = res.json()
    
    print(f"🔄 Reclasificando lugares en 'otro'...\n")
    
    from ia import clasificar_lugar
    
    for lugar in lugares:
        if lugar.get("categoria") == "otro":
            nueva_cat = clasificar_lugar(lugar["nombre"], lugar.get("ubicacion", ""))
            
            res = httpx.put(
                f"{API_URL}/lugares/{lugar['id']}",
                json={"categoria": nueva_cat},
                timeout=30
            )
            
            if res.status_code == 200:
                print(f" {lugar['nombre']} → {nueva_cat}")
            else:
                print(f" Error en {lugar['nombre']}")

if __name__ == "__main__":
    reclasificar()