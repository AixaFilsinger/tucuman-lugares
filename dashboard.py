import streamlit as st
import httpx
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Tucumán Lugares",
    page_icon="🍺",
    layout="wide"
)

st.title("🍺 Tucumán Lugares — Panel de Administración")

# ── FUNCIONES ──────────────────────────────────────────

def get_lugares(solo_activos=True):
    try:
        res = httpx.get(f"{API_URL}/lugares", params={"solo_activos": solo_activos})
        return res.json()
    except:
        return []

def crear_lugar(datos):
    res = httpx.post(f"{API_URL}/lugares", json=datos, timeout=30)
    return res

def editar_lugar(lugar_id, datos):
    res = httpx.put(f"{API_URL}/lugares/{lugar_id}", json=datos, timeout=30)
    return res

def desactivar_lugar(lugar_id):
    res = httpx.delete(f"{API_URL}/lugares/{lugar_id}")
    return res

# ── MÉTRICAS ───────────────────────────────────────────

lugares = get_lugares()

col1, col2, col3, col4 = st.columns(4)

categorias = {}
for l in lugares:
    cat = l.get("categoria", "otro") or "otro"
    categorias[cat] = categorias.get(cat, 0) + 1

with col1:
    st.metric("Total Lugares", len(lugares))
with col2:
    st.metric("Bares", categorias.get("bar", 0))
with col3:
    st.metric("Restaurantes", categorias.get("restaurante", 0))
with col4:
    st.metric("Cafés", categorias.get("café", 0))

st.divider()

# ── TABS ───────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(["📋 Ver Lugares", "➕ Agregar", "✏️ Editar / Eliminar"])

# ── TAB 1: VER ─────────────────────────────────────────
with tab1:
    col_filtro1, col_filtro2 = st.columns([2, 1])
    with col_filtro1:
        filtro_cat = st.selectbox(
            "Filtrar por categoría",
            ["Todas"] + list(set(l.get("categoria", "otro") for l in lugares))
        )
    with col_filtro2:
        mostrar_inactivos = st.checkbox("Mostrar inactivos")

    lugares_filtrados = get_lugares(solo_activos=not mostrar_inactivos)
    if filtro_cat != "Todas":
        lugares_filtrados = [l for l in lugares_filtrados if l.get("categoria") == filtro_cat]

    if lugares_filtrados:
        df = pd.DataFrame(lugares_filtrados)
        columnas = ["nombre", "ubicacion", "categoria", "descripcion", "fuente", "created_at"]
        columnas_presentes = [c for c in columnas if c in df.columns]
        st.dataframe(df[columnas_presentes], use_container_width=True, hide_index=True)

        # Gráfico de categorías
        if len(categorias) > 0:
            st.subheader("📊 Distribución por categoría")
            df_cat = pd.DataFrame(
                list(categorias.items()),
                columns=["Categoría", "Cantidad"]
            )
            st.bar_chart(df_cat.set_index("Categoría"))
    else:
        st.info("No hay lugares para mostrar.")

# ── TAB 2: AGREGAR ─────────────────────────────────────
with tab2:
    st.subheader("Agregar nuevo lugar")

    with st.container():
        nombre = st.text_input("Nombre *", placeholder="Ej: Bar El Federal")
        ubicacion = st.text_input("Ubicación", placeholder="Ej: Av. Mate de Luna 1200")
        
        col_a, col_b = st.columns(2)
        with col_a:
            categoria_manual = st.selectbox(
                "Categoría (opcional — la IA la detecta sola)",
                ["", "bar", "boliche", "café", "restaurante", "recital", "cultural", "otro"]
            )
        with col_b:
            fuente = st.selectbox("Fuente", ["manual", "mock", "scraping", "api"])
        
        descripcion_manual = st.text_area("Descripción (opcional — la IA la genera sola)")

        if st.button("✅ Guardar lugar", type="primary"):
            if not nombre:
                st.error("El nombre es obligatorio")
            else:
                with st.spinner("La IA está clasificando y generando descripción..."):
                    datos = {
                        "nombre": nombre,
                        "ubicacion": ubicacion,
                        "fuente": fuente,
                    }
                    if categoria_manual:
                        datos["categoria"] = categoria_manual
                    if descripcion_manual:
                        datos["descripcion"] = descripcion_manual

                    res = crear_lugar(datos)
                    if res.status_code == 201:
                        data = res.json()
                        st.success(f"✅ '{data['nombre']}' guardado — categoría: {data['categoria']}")
                        st.rerun()
                    elif res.status_code == 409:
                        st.warning(f"⚠️ {res.json().get('detail', 'Duplicado detectado')}")
                    else:
                        st.error(f"❌ Error: {res.text}")

# ── TAB 3: EDITAR / ELIMINAR ───────────────────────────
with tab3:
    st.subheader("Editar o desactivar un lugar")

    if not lugares:
        st.info("No hay lugares cargados.")
    else:
        opciones = {f"{l['nombre']} ({l.get('categoria','?')})": l['id'] for l in lugares}
        seleccion = st.selectbox("Seleccioná un lugar", list(opciones.keys()))
        lugar_id = opciones[seleccion]

        lugar_actual = next((l for l in lugares if l['id'] == lugar_id), None)

        if lugar_actual:
            with st.form("form_editar"):
                nuevo_nombre = st.text_input("Nombre", value=lugar_actual.get("nombre", ""))
                nueva_ubicacion = st.text_input("Ubicación", value=lugar_actual.get("ubicacion", "") or "")
                nueva_categoria = st.selectbox(
                    "Categoría",
                    ["bar", "boliche", "café", "restaurante", "recital", "cultural", "otro"],
                    index=["bar", "boliche", "café", "restaurante", "recital", "cultural", "otro"].index(
                        lugar_actual.get("categoria", "otro") or "otro"
                    )
                )
                nueva_descripcion = st.text_area("Descripción", value=lugar_actual.get("descripcion", "") or "")

                col_guardar, col_eliminar = st.columns(2)
                with col_guardar:
                    guardar = st.form_submit_button("💾 Guardar cambios", type="primary")
                with col_eliminar:
                    eliminar = st.form_submit_button("🗑️ Desactivar lugar")

            if guardar:
                datos = {
                    "nombre": nuevo_nombre,
                    "ubicacion": nueva_ubicacion,
                    "categoria": nueva_categoria,
                    "descripcion": nueva_descripcion,
                }
                res = editar_lugar(lugar_id, datos)
                if res.status_code == 200:
                    st.success("✅ Lugar actualizado correctamente")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {res.text}")

            if eliminar:
                res = desactivar_lugar(lugar_id)
                if res.status_code == 200:
                    st.success("✅ Lugar desactivado")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {res.text}")