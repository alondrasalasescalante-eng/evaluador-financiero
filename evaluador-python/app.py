import streamlit as st
import pandas as pd
from modelo_financiero import ModeloFinanciero

st.set_page_config(page_title="Evaluador Financiero de Proyectos", layout="wide")

st.title("📊 Evaluador Financiero de Proyectos Pro")
st.caption("Modelo integral con Presupuesto de Inversiones, Personal, Egresos con/sin IGV y Balance General")

# Barra Lateral: Parámetros del Proyecto
with st.sidebar:
    st.header("⚙️ Configuración del Proyecto")
    
    st.subheader("1. Proyección de Ventas")
    tipo_proyeccion = st.radio("Modalidad de Proyección", ["Manual por Año", "Por Tasa % y Capacidad Máx."])
    
    ventas_manuales = []
    if tipo_proyeccion == "Manual por Año":
        st.write("Ingrese unidades estimadas por año:")
        c1, c2, c3, c4, c5 = st.columns(5)
        v1 = c1.number_input("Año 1", value=4000)
        v2 = c2.number_input("Año 2", value=4200)
        v3 = c3.number_input("Año 3", value=4400)
        v4 = c4.number_input("Año 4", value=4700)
        v5 = c5.number_input("Año 5", value=5000)
        ventas_manuales = [v1, v2, v3, v4, v5]
        unidades_base, crec_unidades, capacidad_max = 4000, 0.05, 100000
    else:
        unidades_base = st.number_input("Unidades Base (Año 1)", value=4000)
        crec_unidades = st.number_input("Tasa Crecimiento Unidades (ej. 0.05)", value=0.05, step=0.01)
        capacidad_max = st.number_input("Capacidad Máxima de Planta (Unidades)", value=6000)

    precio_base = st.number_input("Precio Unitario Base ($)", value=840.0)
    crec_precio = st.number_input("Crecimiento Precio (ej. 0.03)", value=0.03, step=0.01)

    st.subheader("2. Costos y Personal ($)")
    costo_unit_base = st.number_input("Costo Unitario Materiales ($)", value=378.0)
    mod = st.number_input("Mano de Obra Directa (MOD Anual)", value=224400.0)
    moi = st.number_input("Mano de Obra Indirecta (MOI Anual)", value=150000.0)
    costos_indirectos = st.number_input("Costos Indirectos Fabricación (GIF)", value=635400.0)
    
    st.markdown("---")
    personal_admin = st.number_input("Personal Administrativo (Anual)", value=223000.0)
    otros_gastos_admin = st.number_input("Otros Gastos Administrativos", value=61000.0)
    
    st.markdown("---")
    tiene_personal_ventas = st.toggle("¿Incluir Área de Ventas?", value=True)
    if tiene_personal_ventas:
        personal_ventas = st.number_input("Personal de Ventas (Anual)", value=180000.0)
        comision_ventas_pct = st.number_input("Comisión de Ventas (ej. 0.025 = 2.5%)", value=0.025, step=0.005)
        otros_gastos_ventas = st.number_input("Otros Gastos de Ventas", value=96600.0)
    else:
        personal_ventas = 0.0
        comision_ventas_pct = 0.0
        otros_gastos_ventas = 0.0

    st.subheader("3. Financiamiento y Tasas")
    prestamo = st.number_input("Monto del Préstamo Bancario ($)", value=1173354.0)
    tasa_interes = st.number_input("Tasa de Interés Anual (ej. 0.12)", value=0.12, step=0.01)
    cok = st.number_input("Tasa COK / Descuento (ej. 0.14)", value=0.14, step=0.01)
    valor_residual = st.number_input("Valor Residual al Año 5 ($)", value=0.0)

    st.subheader("4. Políticas Comerciales e IGV")
    igv = st.number_input("Tasa IGV (ej. 0.18)", value=0.18, step=0.01)
    dias_cobro = st.number_input("Días de Cobro Clientes", value=30)
    dias_pago = st.number_input("Días de Pago Proveedores", value=45)
    pct_inv_pt = st.number_input("% Inv. Final Producto Terminado", value=0.10, step=0.01)
    pct_inv_md = st.number_input("% Inv. Final Materiales Directos", value=0.10, step=0.01)
    pct_dividendos = st.number_input("% Distribución Dividendos", value=0.40, step=0.01)

# Pestaña Principal para Inversiones
st.header("🏗️ Presupuesto de Inversión Fija (Tangible e Intangible)")

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

df_activos_input = pd.DataFrame(activos_base)

df_activos_editado = st.data_editor(
    df_activos_input,
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

datos_entrada = {
    "tipo_proyeccion": tipo_proyeccion,
    "ventas_manuales": ventas_manuales,
    "unidades_base": unidades_base,
    "crec_unidades": crec_unidades,
    "capacidad_max": capacidad_max,
    "precio_base": precio_base,
    "crec_precio": crec_precio,
    "costo_unit_base": costo_unit_base,
    "mod": mod,
    "moi": moi,
    "costos_indirectos": costos_indirectos,
    "personal_admin": personal_admin,
    "otros_gastos_admin": otros_gastos_admin,
    "tiene_personal_ventas": tiene_personal_ventas,
    "personal_ventas": personal_ventas,
    "comision_ventas_pct": comision_ventas_pct,
    "otros_gastos_ventas": otros_gastos_ventas,
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

st.subheader("🎯 Indicadores Financieros de Evaluación")
k1, k2, k3, k4 = st.columns(4)
eval_dict = res.get("evaluacion", {})
k1.metric("VAN Económico (FCL)", fmt(eval_dict.get("van_fcl")))
k2.metric("TIR Económica (FCL)", fmt_pct(eval_dict.get("tir_fcl")))
k3.metric("VAN Financiero (FCA)", fmt(eval_dict.get("van_fca")))
k4.metric("TIR Financiera (FCA)", fmt_pct(eval_dict.get("tir_fca")))

st.divider()

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

import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. Indicador Visual de Viabilidad Financiera
# ---------------------------------------------------------
van_val = res.get("evaluacion", {}).get("van_fcl", 0) or 0

if van_val > 0:
    st.success(f"✅ **Proyecto viable:** El VAN económico es positivo ({fmt(van_val)}). Genera valor por encima de la tasa de descuento.")
else:
    st.error(f"❌ **Proyecto no viable:** El VAN económico es negativo ({fmt(van_val)}). El proyecto no cubre el costo de oportunidad del capital.")

# ---------------------------------------------------------
# 2. Gráfico Interactivo de Flujos de Caja
# ---------------------------------------------------------
st.subheader("📈 Comportamiento de los Flujos de Caja")

flujo_econ = res["flujo_detallado"]["flujo_economico"]
flujo_financ = res["flujo_detallado"]["flujo_financiero"]
anios_eje = [f"Año {i}" for i in range(len(flujo_econ))]

fig = go.Figure()
fig.add_trace(go.Bar(x=anios_eje, y=flujo_econ, name="Flujo de Caja Libre (FCL)", marker_color="#38bdf8"))
fig.add_trace(go.Bar(x=anios_eje, y=flujo_financ, name="Flujo de Caja Financiero (FCA)", marker_color="#818cf8"))

fig.update_layout(
    barmode="group",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f8fafc"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=30, b=20)
)

st.plotly_chart(fig, use_container_width=True)
