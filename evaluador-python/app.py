import streamlit as st
import pandas as pd
from modelo_financiero import ModeloFinanciero

st.set_page_config(
    page_title="Evaluador Financiero de Proyectos",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Personalizados
st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .main-header { font-size: 2.2rem; font-weight: 700; color: #ffffff; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.0rem; color: #94a3b8; margin-bottom: 1.5rem; }
    
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 14px 18px;
    }
    div[data-testid="stMetricLabel"] > label { color: #94a3b8 !important; font-weight: 600 !important; }
    div[data-testid="stMetricValue"] > div { color: #38bdf8 !important; font-weight: 700 !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #0f172a; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; background-color: #1e293b; border-radius: 8px 8px 0px 0px;
        color: #94a3b8; font-weight: 600; padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] { background-color: #2563eb !important; color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📈 Evaluador Financiero de Proyectos Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Evaluación financiera integral con clasificación dinámica de Costos Fijos y Variables</div>', unsafe_allow_html=True)

# Barra Lateral: Parámetros Generales
with st.sidebar:
    st.title("⚙️ Parámetros Generales")
    
    with st.expander("📦 Proyección de Ventas", expanded=True):
        tipo_proyeccion = st.radio("Modalidad", ["Manual por Año", "Por Tasa % y Capacidad Máx."])
        ventas_manuales = []
        if tipo_proyeccion == "Manual por Año":
            st.caption("Unidades por año:")
            c1, c2, c3, c4, c5 = st.columns(5)
            v1 = c1.number_input("A1", value=4000)
            v2 = c2.number_input("A2", value=4200)
            v3 = c3.number_input("A3", value=4400)
            v4 = c4.number_input("A4", value=4700)
            v5 = c5.number_input("A5", value=5000)
            ventas_manuales = [v1, v2, v3, v4, v5]
            unidades_base, crec_unidades, capacidad_max = 4000, 0.05, 100000
        else:
            unidades_base = st.number_input("Unidades Año 1", value=4000)
            crec_unidades = st.number_input("Crecimiento Anual %", value=0.05, step=0.01)
            capacidad_max = st.number_input("Techo Capacidad", value=6000)

        precio_base = st.number_input("Precio Unitario Base ($)", value=840.0)
        crec_precio = st.number_input("Crecimiento Precio %", value=0.03, step=0.01)
        costo_unit_base = st.number_input("Costo Unit. Materiales Directos ($)", value=378.0)

    with st.expander("🏦 Financiamiento y Estructura", expanded=False):
        prestamo = st.number_input("Monto Préstamo ($)", value=1173354.0)
        tasa_interes = st.number_input("Tasa Interés Anual", value=0.12, step=0.01)
        cok = st.number_input("Tasa Descuento COK", value=0.14, step=0.01)
        valor_residual = st.number_input("Valor Residual Año 5", value=0.0)

    with st.expander("🏛️ Políticas Comerciales e IGV", expanded=False):
        igv = st.number_input("Tasa IGV", value=0.18, step=0.01)
        dias_cobro = st.number_input("Días Cobro Clientes", value=30)
        dias_pago = st.number_input("Días Pago Proveedores", value=45)
        pct_inv_pt = st.number_input("% Inv. Prod. Terminado", value=0.10, step=0.01)
        pct_inv_md = st.number_input("% Inv. Mat. Directo", value=0.10, step=0.01)
        pct_dividendos = st.number_input("% Distribución Dividendos", value=0.40, step=0.01)

# Pestaña 1: Presupuesto de Inversiones
st.subheader("🏗️ 1. Presupuesto de Inversión Fija (Tangible e Intangible)")

activos_base = [
    {"nombre": "Terreno industrial", "tipo": "tangible", "cantidad": 2000, "costo_unitario": 90.0, "vida_util": 0},
    {"nombre": "Edificaciones (Planta, Almacenes, Oficinas)", "tipo": "tangible", "cantidad": 1, "costo_unitario": 650000.0, "vida_util": 20},
    {"nombre": "Maquinaria de producción", "tipo": "tangible", "cantidad": 1, "costo_unitario": 1125000.0, "vida_util": 10},
    {"nombre": "Equipos auxiliares de planta", "tipo": "tangible", "cantidad": 1, "costo_unitario": 150000.0, "vida_util": 10},
    {"nombre": "Equipos de oficina y cómputo", "tipo": "tangible", "cantidad": 1, "costo_unitario": 30000.0, "vida_util": 4},
    {"nombre": "Vehículos (Camión y camioneta)", "tipo": "tangible", "cantidad": 1, "costo_unitario": 115000.0, "vida_util": 5},
    {"nombre": "Muebles y enseres", "tipo": "tangible", "cantidad": 1, "costo_unitario": 25000.0, "vida_util": 10},
    {"nombre": "Instalaciones complementarias", "tipo": "tangible", "cantidad": 1, "costo_unitario": 120000.0, "vida_util": 10},
    {"nombre": "Estudio de factibilidad y Licencias", "tipo": "intangible", "cantidad": 1, "costo_unitario": 100000.0, "vida_util": 5},
    {"nombre": "Certificaciones (HACCP, BPM) y Marca", "tipo": "intangible", "cantidad": 1, "costo_unitario": 187336.0, "vida_util": 5},
]

df_activos_editado = st.data_editor(
    pd.DataFrame(activos_base),
    column_config={
        "nombre": st.column_config.TextColumn("Concepto / Activo"),
        "tipo": st.column_config.SelectboxColumn("Tipo de Inversión", options=["tangible", "intangible"]),
        "cantidad": st.column_config.NumberColumn("Cantidad", min_value=1, step=1),
        "costo_unitario": st.column_config.NumberColumn("Valor Unitario ($)", format="$%f"),
        "vida_util": st.column_config.NumberColumn("Vida Útil (Años)", min_value=0, step=1),
    },
    num_rows="dynamic",
    use_container_width=True
)

df_activos_editado["valor"] = df_activos_editado["cantidad"] * df_activos_editado["costo_unitario"]
activos_procesados = df_activos_editado.to_dict(orient="records")

inv_tangible = float(df_activos_editado[df_activos_editado["tipo"] == "tangible"]["valor"].sum())
inv_intangible = float(df_activos_editado[df_activos_editado["tipo"] == "intangible"]["valor"].sum())
inv_fija_total = inv_tangible + inv_intangible

c_inv1, c_inv2, c_inv3 = st.columns(3)
c_inv1.metric("Inversión Fija Tangible", f"${inv_tangible:,.2f}")
c_inv2.metric("Inversión Fija Intangible", f"${inv_intangible:,.2f}")
c_inv3.metric("Total Inversión Fija", f"${inv_fija_total:,.2f}")

st.divider()

# Pestaña 2: Dos Cuadros Editables para Costos y Gastos
st.subheader("🏭 2. Presupuesto de Costos de Fabricación y Gastos Operativos")
st.caption("Clasifica cada costo asignando su porcentaje Fijo y Variable (% Fijo + % Variable debe sumar 100%):")

col_cif, col_ga_gv = st.columns(2)

with col_cif:
    st.markdown("### 🛠️ Cuadro 1: Costos Indirectos de Fabricación (CIF / GIF)")
    cif_base = [
        {"concepto": "Materiales Indirectos", "monto_anual": 120000.0, "pct_fijo": 0.20, "pct_variable": 0.80},
        {"concepto": "Mano de Obra Indirecta (MOI)", "monto_anual": 150000.0, "pct_fijo": 0.80, "pct_variable": 0.20},
        {"concepto": "Servicios de Planta (Luz, Agua, Gas)", "monto_anual": 210000.0, "pct_fijo": 0.30, "pct_variable": 0.70},
        {"concepto": "Mantenimiento y Repuestos", "monto_anual": 155400.0, "pct_fijo": 0.40, "pct_variable": 0.60},
        {"concepto": "Seguros e Inspecciones de Planta", "monto_anual": 150000.0, "pct_fijo": 1.00, "pct_variable": 0.00},
    ]
    df_cif_editado = st.data_editor(
        pd.DataFrame(cif_base),
        column_config={
            "concepto": st.column_config.TextColumn("Concepto CIF"),
            "monto_anual": st.column_config.NumberColumn("Monto Anual ($)", format="$%f"),
            "pct_fijo": st.column_config.NumberColumn("% Fijo", min_value=0.0, max_value=1.0, step=0.05),
            "pct_variable": st.column_config.NumberColumn("% Variable", min_value=0.0, max_value=1.0, step=0.05),
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_cif"
    )
    df_cif_editado["cif_fijo"] = df_cif_editado["monto_anual"] * df_cif_editado["pct_fijo"]
    df_cif_editado["cif_variable"] = df_cif_editado["monto_anual"] * df_cif_editado["pct_variable"]
    
    cif_fijo_total = float(df_cif_editado["cif_fijo"].sum())
    cif_var_total = float(df_cif_editado["cif_variable"].sum())

with col_ga_gv:
    st.markdown("### 💼 Cuadro 2: Gastos Operativos (Admin y Ventas)")
    gastos_base = [
        {"concepto": "Personal Administrativo", "tipo_gasto": "Admin", "monto_anual": 223000.0, "pct_fijo": 1.00, "pct_variable": 0.00},
        {"concepto": "Servicios y Útiles de Administración", "tipo_gasto": "Admin", "monto_anual": 61000.0, "pct_fijo": 0.70, "pct_variable": 0.30},
        {"concepto": "Personal y Jefatura de Ventas", "tipo_gasto": "Ventas", "monto_anual": 180000.0, "pct_fijo": 0.90, "pct_variable": 0.10},
        {"concepto": "Comisiones por Ventas", "tipo_gasto": "Ventas", "monto_anual": 91600.0, "pct_fijo": 0.00, "pct_variable": 1.00},
        {"concepto": "Publicidad y Promoción", "tipo_gasto": "Ventas", "monto_anual": 96600.0, "pct_fijo": 0.50, "pct_variable": 0.50},
    ]
    df_gastos_editado = st.data_editor(
        pd.DataFrame(gastos_base),
        column_config={
            "concepto": st.column_config.TextColumn("Concepto Gasto"),
            "tipo_gasto": st.column_config.SelectboxColumn("Categoría", options=["Admin", "Ventas"]),
            "monto_anual": st.column_config.NumberColumn("Monto Anual ($)", format="$%f"),
            "pct_fijo": st.column_config.NumberColumn("% Fijo", min_value=0.0, max_value=1.0, step=0.05),
            "pct_variable": st.column_config.NumberColumn("% Variable", min_value=0.0, max_value=1.0, step=0.05),
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_gastos"
    )
    df_gastos_editado["monto_fijo"] = df_gastos_editado["monto_anual"] * df_gastos_editado["pct_fijo"]
    df_gastos_editado["monto_variable"] = df_gastos_editado["monto_anual"] * df_gastos_editado["pct_variable"]

    ga_fijo_total = float(df_gastos_editado[df_gastos_editado["tipo_gasto"] == "Admin"]["monto_fijo"].sum())
    ga_var_total = float(df_gastos_editado[df_gastos_editado["tipo_gasto"] == "Admin"]["monto_variable"].sum())
    
    gv_fijo_total = float(df_gastos_editado[df_gastos_editado["tipo_gasto"] == "Ventas"]["monto_fijo"].sum())
    gv_var_total = float(df_gastos_editado[df_gastos_editado["tipo_gasto"] == "Ventas"]["monto_variable"].sum())

# Cuadro Complementario: Mano de Obra Directa (MOD)
st.markdown("### 👷 Cuadro MOD: Mano de Obra Directa")
c_mod1, c_mod2 = st.columns(2)
mod_anual = c_mod1.number_input("Mano de Obra Directa Total Anual ($)", value=224400.0)
pct_mod_fijo = c_mod2.slider("Porcentaje Fijo de MOD (% fijos por salario base o supervisores directos)", 0.0, 1.0, 0.30, step=0.05)

st.divider()

# Ejecución del Modelo Financiero
datos_entrada = {
    "tipo_proyeccion": tipo_proyeccion,
    "ventas_manuales": ventas_manuales,
    "unidades_base": unidades_base,
    "crec_unidades": crec_unidades,
    "capacidad_max": capacidad_max,
    "precio_base": precio_base,
    "crec_precio": crec_precio,
    "costo_unit_base": costo_unit_base,
    "mod_anual": mod_anual,
    "pct_mod_fijo": pct_mod_fijo,
    "cif_fijo_total": cif_fijo_total,
    "cif_var_total": cif_var_total,
    "ga_fijo_total": ga_fijo_total,
    "ga_var_total": ga_var_total,
    "gv_fijo_total": gv_fijo_total,
    "gv_var_total": gv_var_total,
    "prestamo": prestamo,
    "tasa_interes": tasa_interes,
    "cok": cok,
    "valor_residual": valor_residual,
    "igv": igv,
    "dias_cobro": dias_cobro,
    "dias_pago": dias_pago,
    "pct_inv_pt": pct_inv_pt,
    "pct_inv_md": pct_inv_md,
    "pct_dividendos": pct_dividendos,
    "impuestos": 0.30,
    "plazo": 5,
    "activos": activos_procesados
}

modelo = ModeloFinanciero(datos_entrada)
res = modelo.ejecutar_modelo_completo()

def fmt(n):
    if n is None or isinstance(n, str):
        return "—"
    try:
        val = float(n)
        return f"${val:,.2f}"
    except (ValueError, TypeError):
        return "—"

def fmt_pct(n):
    if n is None or isinstance(n, str):
        return "N/A"
    try:
        val = float(n)
        return f"{val:.2f}%"
    except (ValueError, TypeError):
        return "N/A"

# Dashboard de Indicadores Principales
st.subheader("🎯 Resumen de Evaluación Financiera")
k1, k2, k3, k4 = st.columns(4)
eval_dict = res.get("evaluacion", {})
k1.metric("VAN Económico (FCL)", fmt(eval_dict.get("van_fcl")))
k2.metric("TIR Económica (FCL)", fmt_pct(eval_dict.get("tir_fcl")))
k3.metric("VAN Financiero (FCA)", fmt(eval_dict.get("van_fca")))
k4.metric("TIR Financiera (FCA)", fmt_pct(eval_dict.get("tir_fca")))

st.divider()

# Pestañas de Resultados
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "🏛️ Balance General", "💵 Flujo de Efectivo", "💸 Egresos con/sin IGV",
    "📦 Compras MD", "🛠️ Depreciación & Amortización", "🧾 Liquidación IGV", 
    "💼 Capital de Trabajo", "📈 Estado Resultados", "📊 Flujos Evaluativos"
])

with tab1:
    st.subheader("Estado de Situación Financiera Proyectado ($)")
    df_bs = pd.DataFrame(res["estado_situacion"]).set_index("anio").T
    st.dataframe(df_bs.style.format(fmt), use_container_width=True)

with tab2:
    st.subheader("Estado de Flujo de Efectivo Proyectado ($)")
    df_fe = pd.DataFrame(res["flujo_efectivo"]).set_index("anio").T
    st.dataframe(df_fe.style.format(fmt), use_container_width=True)

with tab3:
    st.subheader("Cuadro Comparativo de Egresos Proyectados ($)")
    egr_sin = res.get("egresos_sin_igv")
    egr_con = res.get("egresos_con_igv")
    
    if egr_sin and egr_con:
        st.write("**Egresos Sin IGV:**")
        df_egr_sin = pd.DataFrame(egr_sin).set_index("anio").T
        st.dataframe(df_egr_sin.style.format(fmt), use_container_width=True)
        
        st.write("**Egresos Con IGV:**")
        df_egr_con = pd.DataFrame(egr_con).set_index("anio").T
        st.dataframe(df_egr_con.style.format(fmt), use_container_width=True)
    else:
        st.info("Cargando información de egresos...")

with tab4:
    st.subheader("Compras y Requerimiento de Materiales Directos")
    df_md = pd.DataFrame(res["modulo_compras_md"]).set_index("anio").T
    st.dataframe(df_md.style.format("{:,.2f}"), use_container_width=True)

with tab5:
    st.subheader("Cuadro de Depreciación y Amortización por Activo ($)")
    df_depr = pd.DataFrame(res["depreciaciones"])
    df_depr["Depreciación Anual"] = df_depr["depr_anual"]
    st.dataframe(df_depr[["nombre", "tipo", "valor", "vida_util", "Depreciación Anual"]].style.format({"valor": fmt, "Depreciación Anual": fmt}), use_container_width=True)

with tab6:
    st.subheader("Módulo de Impuesto General a las Ventas (IGV) ($)")
    df_igv = pd.DataFrame(res["modulo_igv"]).set_index("anio").T
    st.dataframe(df_igv.style.format(fmt), use_container_width=True)

with tab7:
    st.subheader("Necesidades de Capital de Trabajo ($)")
    df_ct = pd.DataFrame(res["modulo_ct"]).set_index("anio").T
    st.dataframe(df_ct.style.format(fmt), use_container_width=True)

with tab8:
    st.subheader("Estado de Resultados Proyectado ($)")
    df_er = pd.DataFrame(res["estado_resultados"]).set_index("anio").T
    st.dataframe(df_er.style.format(fmt), use_container_width=True)

with tab9:
    st.subheader("Flujos de Caja Evaluativos ($)")
    df_flujo = pd.DataFrame(res["flujo_detallado"], index=[f"Año {i}" for i in range(6)]).T
    st.dataframe(df_flujo.style.format(fmt), use_container_width=True)
