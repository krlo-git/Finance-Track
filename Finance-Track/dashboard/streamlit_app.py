import streamlit as st
import requests
import pandas as pd
from datetime import date
from charts import grafico_gastos_por_categoria, grafico_evolucion_mensual

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Finance Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Finance Tracker")
st.caption("Rastreador de finanzas personales")

# ── Selector de mes ────────────────────────────────────
meses_disponibles = [f"2018-{str(m).zfill(2)}" for m in range(1, 13)]
col_mes, _, _ = st.columns([1, 2, 2])
with col_mes:
    mes_sel = st.selectbox("Selecciona un mes", options=meses_disponibles, index=0)

# ── Obtener resumen ────────────────────────────────────
try:
    resumen = requests.get(f"{API_URL}/resumen?mes={mes_sel}").json()
except Exception:
    st.error("No se puede conectar a la API. Asegúrate de que FastAPI esté corriendo.")
    st.stop()

# ── KPIs principales ───────────────────────────────────
st.markdown("---")
k1, k2, k3 = st.columns(3)
k1.metric("💵 Ingresos", f"${resumen['total_ingresos']:,.0f}")
k2.metric("💸 Gastos", f"${resumen['total_gastos']:,.0f}")
balance = resumen['balance']
k3.metric("📊 Balance", f"${balance:,.0f}", delta="positivo" if balance >= 0 else "negativo")

# ── Alertas de presupuesto ─────────────────────────────
alertas = [c for c in resumen["por_categoria"] if c["alerta"]]
if alertas:
    st.warning(f"⚠ Presupuesto superado en: {', '.join(a['categoria'] for a in alertas)}")

# ── Gráficos ───────────────────────────────────────────
st.markdown("---")
g1, g2 = st.columns(2)

with g1:
    st.subheader("Gastos por categoría")
    df_cat = pd.DataFrame(resumen["por_categoria"])
    if not df_cat.empty:
        st.plotly_chart(grafico_gastos_por_categoria(df_cat), use_container_width=True)

with g2:
    st.subheader("Evolución mensual 2018")
    try:
        resumenes = []
        for m in range(1, 13):
            mes = f"2018-{str(m).zfill(2)}"
            r = requests.get(f"{API_URL}/resumen?mes={mes}").json()
            resumenes.append({
                "mes": mes,
                "ingresos": r["total_ingresos"],
                "gastos": r["total_gastos"]
            })
        df_evol = pd.DataFrame(resumenes)
        st.plotly_chart(grafico_evolucion_mensual(df_evol), use_container_width=True)
    except Exception:
        st.info("Sin datos suficientes para evolución mensual.")

# ── Tabla de transacciones ─────────────────────────────
st.markdown("---")
st.subheader("Transacciones del mes")

col_f1, col_f2 = st.columns(2)
with col_f1:
    filtro_tipo = st.selectbox("Tipo", ["Todos", "gasto", "ingreso"])
with col_f2:
    try:
        cats = requests.get(f"{API_URL}/categorias").json()
        nombres_cats = ["Todas"] + [c["nombre"] for c in cats]
        filtro_cat = st.selectbox("Categoría", nombres_cats)
    except Exception:
        filtro_cat = "Todas"

params = {"mes": mes_sel}
if filtro_tipo != "Todos":
    params["tipo"] = filtro_tipo

try:
    txs = requests.get(f"{API_URL}/transacciones", params=params).json()
    df_tx = pd.DataFrame([{
        "Fecha": t["fecha"],
        "Descripción": t["descripcion"],
        "Categoría": t["categoria"]["nombre"],
        "Cuenta": t["cuenta"]["nombre"],
        "Tipo": t["tipo"],
        "Monto": t["monto"]
    } for t in txs])

    if filtro_cat != "Todas" and not df_tx.empty:
        df_tx = df_tx[df_tx["Categoría"] == filtro_cat]

    if not df_tx.empty:
        st.dataframe(df_tx, use_container_width=True, hide_index=True)
    else:
        st.info("Sin transacciones para los filtros seleccionados.")
except Exception as e:
    st.error(f"Error cargando transacciones: {e}")

# ── Agregar transacción ────────────────────────────────
st.markdown("---")
with st.expander("➕ Agregar transacción"):
    c1, c2 = st.columns(2)
    fecha = c1.date_input("Fecha", value=date.today())
    monto = c2.number_input("Monto ($)", min_value=1.0, step=10.0)
    descripcion = st.text_input("Descripción")
    tipo = st.radio("Tipo", ["gasto", "ingreso"], horizontal=True)

    try:
        cats = requests.get(f"{API_URL}/categorias").json()
        cats_filtradas = [c for c in cats if c["tipo"] == tipo]
        cat_sel = st.selectbox("Categoría", cats_filtradas, format_func=lambda x: x["nombre"])

        cuentas = requests.get(f"{API_URL}/cuentas").json()
        cuenta_sel = st.selectbox("Cuenta", cuentas, format_func=lambda x: x["nombre"])
    except Exception:
        st.error("Error cargando categorías/cuentas.")
        cat_sel, cuenta_sel = None, None

    if st.button("Guardar"):
        if cat_sel and cuenta_sel and descripcion:
            payload = {
                "fecha": str(fecha),
                "descripcion": descripcion,
                "monto": monto,
                "tipo": tipo,
                "categoria_id": cat_sel["id"],
                "cuenta_id": cuenta_sel["id"]
            }
            res = requests.post(f"{API_URL}/transacciones", json=payload)
            if res.status_code == 201:
                st.success("✓ Transacción guardada.")
                st.rerun()
            else:
                st.error(f"Error: {res.text}")
        else:
            st.warning("Completa todos los campos.")