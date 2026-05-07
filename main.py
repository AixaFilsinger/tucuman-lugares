from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import LugarCreate, LugarUpdate
from database import get_client
from ia import clasificar_lugar, generar_descripcion, detectar_duplicado
import unicodedata
import re

app = FastAPI(title="Tucumán Lugares API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def normalizar_nombre(nombre: str) -> str:
    """Normaliza un nombre para comparación: minúsculas, sin tildes, sin espacios extra"""
    nombre = nombre.lower().strip()
    nombre = unicodedata.normalize('NFD', nombre)
    nombre = ''.join(c for c in nombre if unicodedata.category(c) != 'Mn')
    nombre = re.sub(r'\s+', ' ', nombre)
    return nombre

# ── CREAR ──────────────────────────────────────────────
@app.post("/lugares", status_code=201)
def crear_lugar(lugar: LugarCreate):
    client = get_client()

    # 1. Traer todos los lugares activos para chequear duplicados
    res = client.get("/rest/v1/lugares", params={
        "activo": "eq.true",
        "select": "id,nombre"
    })
    try:
        existentes = res.json()
        if not isinstance(existentes, list):
            existentes = []
    except Exception:
        existentes = []

    nombre_norm = normalizar_nombre(lugar.nombre)

    # 2. Chequeo por hash (nombre normalizado exacto)
    for e in existentes:
        if normalizar_nombre(e["nombre"]) == nombre_norm:
            raise HTTPException(
                status_code=409,
                detail=f"Duplicado exacto encontrado: '{e['nombre']}'"
            )

    # 3. Chequeo semántico con IA (solo primeros 30 para no gastar tokens)
    for e in existentes[:30]:
        if detectar_duplicado(lugar.nombre, e["nombre"]):
            raise HTTPException(
                status_code=409,
                detail=f"Posible duplicado detectado por IA: '{e['nombre']}'"
            )

    # 4. Clasificar con IA si no tiene categoría
    categoria = lugar.categoria
    if not categoria:
        categoria = clasificar_lugar(lugar.nombre, lugar.ubicacion or "")

    # 5. Generar descripción con IA si no tiene
    descripcion = lugar.descripcion
    if not descripcion:
        descripcion = generar_descripcion(lugar.nombre, categoria, lugar.ubicacion or "")

    # 6. Insertar en Supabase
    nuevo = {
        "nombre": lugar.nombre,
        "ubicacion": lugar.ubicacion,
        "categoria": categoria,
        "descripcion": descripcion,
        "fuente": lugar.fuente,
    }
    res = client.post("/rest/v1/lugares", json=nuevo)

    if res.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=f"Error guardando: {res.text}")

    return res.json()[0]

# ── LISTAR ─────────────────────────────────────────────
@app.get("/lugares")
def listar_lugares(categoria: str = None, solo_activos: bool = True):
    client = get_client()
    params = {"select": "*", "order": "created_at.desc"}
    if solo_activos:
        params["activo"] = "eq.true"
    if categoria:
        params["categoria"] = f"eq.{categoria}"

    res = client.get("/rest/v1/lugares", params=params)
    return res.json()

# ── OBTENER UNO ────────────────────────────────────────
@app.get("/lugares/{lugar_id}")
def obtener_lugar(lugar_id: str):
    client = get_client()
    res = client.get("/rest/v1/lugares", params={
        "id": f"eq.{lugar_id}",
        "select": "*"
    })
    data = res.json()
    if not data:
        raise HTTPException(status_code=404, detail="Lugar no encontrado")
    return data[0]

# ── EDITAR ─────────────────────────────────────────────
@app.put("/lugares/{lugar_id}")
def editar_lugar(lugar_id: str, datos: LugarUpdate):
    client = get_client()
    update_data = {k: v for k, v in datos.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    res = client.patch(
        "/rest/v1/lugares",
        params={"id": f"eq.{lugar_id}"},
        json=update_data
    )
    if res.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=f"Error actualizando: {res.text}")
    return {"mensaje": "Actualizado correctamente", "id": lugar_id}

# ── DESACTIVAR (soft delete) ───────────────────────────
@app.delete("/lugares/{lugar_id}")
def desactivar_lugar(lugar_id: str):
    client = get_client()
    res = client.patch(
        "/rest/v1/lugares",
        params={"id": f"eq.{lugar_id}"},
        json={"activo": False}
    )
    if res.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=f"Error desactivando: {res.text}")
    return {"mensaje": "Lugar desactivado", "id": lugar_id}

# ── HEALTH CHECK ───────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "mensaje": "API Tucumán Lugares funcionando 🎉"}