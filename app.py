import streamlit as st
import pandas as pd
import os

# Configuración de página "Wide" para aprovechar todo el monitor como un programa de escritorio
st.set_page_config(page_title="Sistema de Depósito", page_icon="📦", layout="wide")

# ==========================================
# CONFIGURACIÓN DE TU EXCEL
# ==========================================
COL_NOMBRE = "Artículo - Desc. Gen."
COL_CODIGO_BEJ = "Stock - Artículo - Cód. Gen."
COL_CODIGO_PROV = "Codigo Proveedor"
COL_LOTE = "Stock - Partida - Cód."
COL_VENC = "Stock - Partida - F. Vto. / Ingreso"
COL_CANT = "Stock - Partida - Cant. Real en UM 1"

@st.cache_data
def cargar_bd():
    if os.path.exists("base_datos_actual.xlsx"):
        try:
            return pd.read_excel("base_datos_actual.xlsx")
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

# ==========================================
# CSS PARA IGUALAR TU PROGRAMA ORIGINAL
# ==========================================
st.markdown("""
    <style>
    /* Ocultar barra superior y menú para que parezca una app de escritorio */
    header {visibility: hidden;}
    
    /* Tamaños de texto gigantes para Dani */
    html, body, p, div, span { font-size: 24px !important; }
    
    /* Estilos del Stock Total Verde (Igual a 3.PNG) */
    .stock-gigante {
        font-size: 60px !important;
        color: #00b050 !important;
        font-weight: 900 !important;
        margin-top: 20px;
    }
    
    /* Fondo limpio esperando búsqueda (Igual a 1.PNG) */
    .esperando {
        text-align: center;
        font-size: 50px !important;
        font-weight: bold;
        margin-top: 100px;
        margin-bottom: 100px;
    }

    /* Colores exactos de los botones de 3.PNG y 4.PNG */
    button[kind="primary"] { font-size: 24px !important; height: 60px !important; }
    
    /* Botón Naranja VER LOTES */
    .btn-naranja > button {
        background-color: #f39c12 !important;
        color: white !important;
        border: 2px solid #e67e22 !important;
        font-weight: bold !important;
    }
    /* Botón Morado UBICACIÓN */
    .btn-morado > button {
        background-color: #8e44ad !important;
        color: white !important;
        border: 2px solid #732d91 !important;
        font-weight: bold !important;
    }
    /* Botón Rojo VOLVER/CERRAR */
    .btn-rojo > button {
        background-color: #e74c3c !important;
        color: white !important;
        border: 2px solid #c0392b !important;
        font-weight: bold !important;
    }
    /* Botón Verde TAREAS */
    .btn-verde > button {
        background-color: #27ae60 !important;
        color: white !important;
        border: 2px solid #2ecc71 !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# Variables de memoria
if "articulo_seleccionado" not in st.session_state:
    st.session_state["articulo_seleccionado"] = None

df = cargar_bd()

# ==========================================
# VENTANAS FLOTANTES (POP-UPS EXACTOS)
# ==========================================

# 1. Pop-up de Resultados (Igual a 2.PNG)
@st.dialog("Resultados de búsqueda", width="large")
def modal_resultados(df_filtrado):
    st.write("Seleccioná el artículo correcto de la lista:")
    
    # Armamos una lista de opciones claras para Dani
    opciones = df_filtrado[COL_CODIGO_BEJ].astype(str) + " - " + df_filtrado[COL_NOMBRE].astype(str)
    opciones_unicas = opciones.unique()
    
    elegido = st.radio("Opciones encontradas:", opciones_unicas, label_visibility="collapsed")
    
    st.write("---")
    if st.button("ABRIR ARTÍCULO SELECCIONADO", type="primary", use_container_width=True):
        st.session_state["articulo_seleccionado"] = elegido
        st.rerun()
    
    # Botón rojo para cerrar (Igual a 2.PNG)
    st.markdown('<div class="btn-rojo">', unsafe_allow_html=True)
    if st.button("CERRAR VENTANA", use_container_width=True):
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 2. Pop-up de Lotes (Igual a 4.PNG)
@st.dialog("Lotes del artículo", width="large")
def modal_lotes(df_lotes):
    # Renombramos columnas para igualar a 4.PNG
    df_lotes_limpio = df_lotes.rename(columns={
        COL_LOTE: "Nro de Lote",
        COL_CANT: "Cantidad",
        COL_VENC: "Vencimiento"
    })
    st.dataframe(df_lotes_limpio, use_container_width=True, hide_index=True)
    
    st.write("---")
    # Botón rojo para volver (Igual a 4.PNG)
    st.markdown('<div class="btn-rojo">', unsafe_allow_html=True)
    if st.button("VOLVER AL BUSCADOR", use_container_width=True):
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# PANTALLA PRINCIPAL (DISEÑO 1.PNG y 3.PNG)
# ==========================================

# BARRA SUPERIOR (Buscador y Botones)
col_buscar, col_espacio, col_plan, col_hoja, col_tareas = st.columns([4, 1, 1.5, 1.5, 1.5])

with col_buscar:
    busqueda = st.text_input("🔍 Buscar por Nombre o Código...", label_visibility="collapsed", placeholder="Ingresar búsqueda...")

with col_plan:
    st.button("Planilla de\nControl", use_container_width=True)
with col_hoja:
    st.button("Hoja de\nRuta 🚚", use_container_width=True)
with col_tareas:
    st.markdown('<div class="btn-verde">', unsafe_allow_html=True)
    st.button("📋 TAREAS ✔", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# LÓGICA DE BÚSQUEDA
if busqueda:
    if not df.empty:
        mask = df[COL_NOMBRE].astype(str).str.contains(busqueda, case=False, na=False) | \
               df[COL_CODIGO_BEJ].astype(str).str.contains(busqueda, case=False, na=False)
        
        if COL_CODIGO_PROV in df.columns:
            mask = mask | df[COL_CODIGO_PROV].astype(str).str.contains(busqueda, case=False, na=False)
        
        resultados = df[mask]
        
        if not resultados.empty:
            # Si buscó, abrimos la ventana flotante automáticamente
            modal_resultados(resultados)
        else:
            st.error("No se encontró el artículo.")

# MOSTRAR LA PANTALLA (ESPERANDO O EL ARTÍCULO)
if st.session_state["articulo_seleccionado"] is None:
    # Pantalla vacía (Igual a 1.PNG)
    st.markdown('<div class="esperando">ESPERANDO BÚSQUEDA...</div>', unsafe_allow_html=True)
    st.markdown('<div class="stock-gigante" style="color: black !important;">STOCK TOTAL: --</div>', unsafe_allow_html=True)

else:
    # Pantalla con el artículo cargado (Igual a 3.PNG)
    articulo_actual = st.session_state["articulo_seleccionado"]
    
    # Filtramos el DataFrame para obtener los datos
    opciones_df = df[COL_CODIGO_BEJ].astype(str) + " - " + df[COL_NOMBRE].astype(str)
    df_exacto = df[opciones_df == articulo_actual].copy()
    
    df_exacto[COL_CANT] = pd.to_numeric(df_exacto[COL_CANT], errors='coerce').fillna(0)
    total_stock = df_exacto[COL_CANT].sum()
    
    # Extraemos el nombre y códigos
    nombre_limpio = df_exacto.iloc[0][COL_NOMBRE] if not df_exacto.empty else "DESCONOCIDO"
    cod_prov = df_exacto.iloc[0][COL_CODIGO_PROV] if COL_CODIGO_PROV in df_exacto.columns else "--"
    
    # Textos centrales (Igual a 3.PNG)
    st.markdown(f"<h1 style='text-align: center; font-size: 50px !important;'>{nombre_limpio}</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #95a5a6;'>📍 UBICACIÓN: SIN ASIGNAR</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>CÓD. PROVEEDOR: {cod_prov}</h4>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>MARCA: --</h4>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #2980b9;'>PROVEEDOR: --</h4>", unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    # Fila inferior: Stock Total a la izquierda, Botones a la derecha (Igual a 3.PNG)
    col_stock, col_btn_lotes, col_btn_ubi = st.columns([2, 1, 1])
    
    with col_stock:
        st.markdown(f'<div class="stock-gigante">STOCK TOTAL: {total_stock:g}</div>', unsafe_allow_html=True)
        
    with col_btn_lotes:
        st.write("") # Espaciador para alinear
        st.markdown('<div class="btn-naranja">', unsafe_allow_html=True)
        if st.button("VER LOTES 🔍", use_container_width=True):
            # Filtramos solo los que tienen stock positivo
            df_lotes_positivos = df_exacto[df_exacto[COL_CANT] > 0][[COL_LOTE, COL_CANT, COL_VENC]]
            modal_lotes(df_lotes_positivos)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_btn_ubi:
        st.write("") # Espaciador para alinear
        st.markdown('<div class="btn-morado">', unsafe_allow_html=True)
        st.button("UBICACIÓN 📍", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Sección escondida al fondo para que Leandro (Admin) pueda subir la BD
st.write("---")
with st.expander("⚙️ Administrador: Actualizar Base de Datos"):
    archivo_db = st.file_uploader("Subir Excel", type=["xlsx"])
    if archivo_db:
        with open("base_datos_actual.xlsx", "wb") as f:
            f.write(archivo_db.getbuffer())
        st.cache_data.clear()
        st.success("✅ Base de datos actualizada.")
        st.rerun()
