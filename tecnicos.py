import streamlit as st
import pandas as pd
import plotly.express as px
import os
from PIL import Image

st.set_page_config(page_title="Dashboard Postventa", layout="wide")

META = 6600000

# 🔒 RUTA FIJA (NO SE BORRA NUNCA)
ruta_base = r"C:\taller"
os.makedirs(ruta_base, exist_ok=True)
archivo = os.path.join(ruta_base, "datos_taller.xlsx")

orden_meses = [
"Enero","Febrero","Marzo","Abril","Mayo","Junio",
"Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
]

# -----------------------------
# CREAR BASE DE DATOS
# -----------------------------

if not os.path.exists(archivo):

    tecnicos = pd.DataFrame(columns=["Tecnico"])

    datos = pd.DataFrame(columns=[
        "Mes",
        "Tecnico",
        "Mano_Obra",
        "Repuestos",
        "Horas_Productivas",
        "Horas_Laborales"
    ])

    with pd.ExcelWriter(archivo, engine="openpyxl") as writer:
        tecnicos.to_excel(writer, sheet_name="tecnicos", index=False)
        datos.to_excel(writer, sheet_name="datos", index=False)

# -----------------------------
# CARGAR DATOS
# -----------------------------

tecnicos = pd.read_excel(archivo, sheet_name="tecnicos")
datos = pd.read_excel(archivo, sheet_name="datos")

# -----------------------------
# HEADER
# -----------------------------

col1,col2 = st.columns([2,4])

try:
    logo = Image.open("logo_empresa.png")
    col1.image(logo,width=250)
except:
    pass

col2.markdown("<h2>Productividad Postventa Caribe</h2>",unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# MENU
# -----------------------------

menu = st.sidebar.selectbox(
"Menú",
[
"Dashboard Ejecutivo",
"Registrar Productividad",
"Gestión de Técnicos",
"Análisis por Técnico",
"Informe Mensual",
"By RoelStar/2026"
]
)

# -----------------------------
# GESTION TECNICOS
# -----------------------------

if menu == "Gestión de Técnicos":

    st.subheader("Administración de Técnicos")

    nuevo = st.text_input("Nuevo técnico")

    if st.button("Agregar técnico"):

        if nuevo != "":
            tecnicos.loc[len(tecnicos)] = [nuevo]

            with pd.ExcelWriter(archivo, engine="openpyxl") as writer:
                tecnicos.to_excel(writer, sheet_name="tecnicos", index=False)
                datos.to_excel(writer, sheet_name="datos", index=False)

            st.success("Técnico agregado")

    st.dataframe(tecnicos)

# -----------------------------
# REGISTRO PRODUCTIVIDAD
# -----------------------------

elif menu == "Registrar Productividad":

    st.subheader("Registro mensual")

    mes = st.selectbox("Mes", orden_meses)

    tecnico = st.selectbox("Técnico", tecnicos["Tecnico"])

    mano = st.number_input("Mano de obra",0)
    rep = st.number_input("Repuestos",0)
    horas_prod = st.number_input("Horas productivas",0.0)
    horas_lab = st.number_input("Horas laborales del mes",0.0)

    if st.button("Guardar"):

        nuevo = pd.DataFrame([{
            "Mes":mes,
            "Tecnico":tecnico,
            "Mano_Obra":mano,
            "Repuestos":rep,
            "Horas_Productivas":horas_prod,
            "Horas_Laborales":horas_lab
        }])

        datos = pd.concat([datos,nuevo],ignore_index=True)

        with pd.ExcelWriter(archivo, engine="openpyxl") as writer:
            tecnicos.to_excel(writer, sheet_name="tecnicos", index=False)
            datos.to_excel(writer, sheet_name="datos", index=False)

        st.success("Registro guardado")

# -----------------------------
# DASHBOARD EJECUTIVO
# -----------------------------

elif menu == "Dashboard Ejecutivo":

    st.subheader("Indicadores generales")

    if len(datos)==0:
        st.warning("No hay datos")
        st.stop()

    # 🔹 TOTALES GENERALES
    total_mo = datos["Mano_Obra"].sum()
    total_rep = datos["Repuestos"].sum()

    # 🔹 AGRUPACIÓN GENERAL
    meses_trabajados = datos["Mes"].nunique()

    prod = datos.groupby("Tecnico")[[
        "Mano_Obra",
        "Repuestos",
        "Horas_Productivas",
        "Horas_Laborales"
    ]].sum().reset_index()

    meta_acumulada = META * meses_trabajados

    prod["Cumplimiento %"] = (prod["Mano_Obra"] / meta_acumulada) * 100
    prod["Productividad %"] = (prod["Horas_Productivas"] / prod["Horas_Laborales"]) * 100

    # 🔥 PROMEDIOS (REFERENCIA)
    prom_cumplimiento = prod["Cumplimiento %"].mean()
    prom_productividad = prod["Productividad %"].mean()

    # 🔥 MÉTRICAS REALES DEL NEGOCIO (CLAVE GERENCIAL)
    total_horas_prod = prod["Horas_Productivas"].sum()
    total_horas_lab = prod["Horas_Laborales"].sum()
    total_tecnicos = prod["Tecnico"].nunique()

    cumplimiento_real = (total_mo / (META * meses_trabajados * total_tecnicos)) * 100
    productividad_real = (total_horas_prod / total_horas_lab) * 100

    # 🔹 MÉTRICAS (ORDEN GERENCIAL)
    col1,col2,col3,col4,col5,col6 = st.columns(6)

    col1.metric("💰 Mano obra total",f"${total_mo:,.0f}")
    col2.metric("🔧 Repuestos totales",f"${total_rep:,.0f}")
    col3.metric("👨‍🔧 Técnicos",total_tecnicos)
    col4.metric("🎯 Meta mensual",f"${META:,.0f}")

    # 🔥 IMPORTANTES (NEGOCIO REAL)
    col5.metric("📊 Cumplimiento REAL", f"{cumplimiento_real:.1f}%")
    col6.metric("⚡ Productividad REAL", f"{productividad_real:.1f}%")

    # 🔹 REFERENCIA (PEQUEÑA)
    st.caption(f"Promedio técnicos → Cumplimiento: {prom_cumplimiento:.1f}% | Productividad: {prom_productividad:.1f}%")

    st.divider()

    # 🔥 CUADRO TOTALIZADO
    st.subheader("Resumen Total por Técnico")

    tabla_total = prod.copy()

    tabla_mostrar = tabla_total.copy()

    tabla_mostrar["Mano_Obra"] = tabla_mostrar["Mano_Obra"].map('${:,.0f}'.format)
    tabla_mostrar["Repuestos"] = tabla_mostrar["Repuestos"].map('${:,.0f}'.format)
    tabla_mostrar["Cumplimiento %"] = tabla_mostrar["Cumplimiento %"].map('{:.1f}%'.format)
    tabla_mostrar["Productividad %"] = tabla_mostrar["Productividad %"].map('{:.1f}%'.format)

    st.dataframe(tabla_mostrar, use_container_width=True)

    st.divider()

    # -----------------------------
    # GRÁFICOS
    # -----------------------------

    st.subheader("Cumplimiento Presupuesto")

    fig = px.bar(
        prod,
        x="Tecnico",
        y="Mano_Obra",
        color="Cumplimiento %",
        text="Mano_Obra",
        color_continuous_scale="RdYlGn"
    )
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",")
    st.plotly_chart(fig,use_container_width=True)

    st.subheader("Ranking Repuestos")

    fig2 = px.bar(prod,x="Tecnico",y="Repuestos",text="Repuestos",color="Repuestos")
    fig2.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig2.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",")
    st.plotly_chart(fig2,use_container_width=True)

    st.subheader("Productividad técnica")

    fig3 = px.bar(
        prod,
        x="Tecnico",
        y="Productividad %",
        text="Productividad %",
        color="Productividad %",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig3,use_container_width=True)

    st.subheader("Evolución mensual")

    mes_data = datos.groupby("Mes")[["Mano_Obra","Repuestos"]].sum().reset_index()
    mes_data["Mes"] = pd.Categorical(mes_data["Mes"],categories=orden_meses,ordered=True)
    mes_data = mes_data.sort_values("Mes")

    fig4 = px.line(mes_data,x="Mes",y=["Mano_Obra","Repuestos"],markers=True)
    fig4.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",")
    st.plotly_chart(fig4,use_container_width=True)

    st.subheader("Participación técnicos en venta de repuestos")

    fig_pie = px.pie(
        prod,
        names="Tecnico",
        values="Repuestos",
        hole=0.4
    )

    fig_pie.update_traces(textposition="inside", textinfo="percent+label")

    st.plotly_chart(fig_pie, use_container_width=True)                                                               

# -----------------------------
# INFORME MENSUAL (AJUSTADO)
# -----------------------------

elif menu == "Informe Mensual":

    st.subheader("Seguimiento mes a mes")

    for mes in orden_meses:

        datos_mes = datos[datos["Mes"] == mes]

        if len(datos_mes) > 0:

            st.markdown(f"## {mes}")

            tabla = datos_mes.groupby("Tecnico")[[
                "Mano_Obra",
                "Repuestos",
                "Horas_Productivas",
                "Horas_Laborales"
            ]].sum().reset_index()

            tabla["Cumplimiento %"] = (tabla["Mano_Obra"] / META) * 100
            tabla["Productividad %"] = (tabla["Horas_Productivas"] / tabla["Horas_Laborales"]) * 100

            # -----------------------------
            # TABLA FORMATEADA
            # -----------------------------
            tabla_mostrar = tabla.copy()

            tabla_mostrar["Mano_Obra"] = tabla_mostrar["Mano_Obra"].map('${:,.0f}'.format)
            tabla_mostrar["Repuestos"] = tabla_mostrar["Repuestos"].map('${:,.0f}'.format)
            tabla_mostrar["Cumplimiento %"] = tabla_mostrar["Cumplimiento %"].map('{:.1f}%'.format)
            tabla_mostrar["Productividad %"] = tabla_mostrar["Productividad %"].map('{:.1f}%'.format)

            st.dataframe(tabla_mostrar, use_container_width=True)

            # 🔥 RESUMEN REAL DEL MES (AQUÍ VA)
            total_mo_mes = tabla["Mano_Obra"].sum()
            total_horas_prod_mes = tabla["Horas_Productivas"].sum()
            total_horas_lab_mes = tabla["Horas_Laborales"].sum()

            cantidad_tecnicos_mes = tabla["Tecnico"].nunique()

            cumplimiento_real = (total_mo_mes / (META * cantidad_tecnicos_mes)) * 100
            productividad_real = (total_horas_prod_mes / total_horas_lab_mes) * 100

            c1, c2 = st.columns(2)

            c1.metric("Cumplimiento real del mes", f"{cumplimiento_real:.1f}%")
            c2.metric("Productividad real del mes", f"{productividad_real:.1f}%")

            st.divider()

            # -----------------------------
            # GRÁFICO
            # -----------------------------
            fig = px.bar(
                tabla,
                x="Tecnico",
                y="Mano_Obra",
                color="Cumplimiento %",
                text="Mano_Obra",
                color_continuous_scale="RdYlGn"
            )

            fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            fig.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",")

            st.plotly_chart(fig,use_container_width=True)

# -----------------------------
# ANALISIS TECNICO
# -----------------------------

elif menu == "Análisis por Técnico":

    tecnico = st.selectbox("Seleccionar técnico", tecnicos["Tecnico"])

    datos_t = datos[datos["Tecnico"] == tecnico]

    if len(datos_t) == 0:
        st.warning("Sin datos")
        st.stop()

    fig = px.line(datos_t,x="Mes",y=["Mano_Obra","Repuestos"],markers=True)
    fig.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",")
    st.plotly_chart(fig,use_container_width=True)

    total = datos_t["Mano_Obra"].sum()
    meses_trabajados = datos["Mes"].nunique()
    meta_acumulada = META * meses_trabajados

    cumplimiento = (total / meta_acumulada) * 100

    st.metric("Cumplimiento total", f"{cumplimiento:.1f}%")