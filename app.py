
import pandas as pd
import streamlit as st
import plotly.express as px
import re

st.set_page_config(page_title="Dashboard de Vagas", layout="wide")

st.title("📊 Dashboard Interativo – Vagas de Emprego")

uploaded_file = st.file_uploader("📂 Envie o CSV atualizado", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Corrigir salário para valor numérico
    def extrair_valor_salario(s):
        if pd.isna(s):
            return None
        match = re.search(r"R\$(\d{1,3}(?:\.\d{3})*,\d{2})", str(s))
        if match:
            return float(match.group(1).replace(".", "").replace(",", "."))
        try:
            return float(str(s).replace(",", "."))
        except:
            return None

    df["Salário Numérico"] = df["Salários"].apply(extrair_valor_salario)

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Filtros")

    salario_min, salario_max = int(df["Salário Numérico"].min()), int(df["Salário Numérico"].max())
    salario_range = st.sidebar.slider("Filtrar por salário (R$)", salario_min, salario_max, (salario_min, salario_max))

    area = st.sidebar.multiselect("Área de atuação", options=df["Áreas de atuação da empresa e do setor"].dropna().unique())
    cargos = st.sidebar.multiselect("Cargos", options=df["Cargos"].dropna().unique())
    competencias_tec = st.sidebar.text_input("Filtrar por competência técnica (texto)")
    competencias_transv = st.sidebar.text_input("Filtrar por competência transversal (texto)")
    local = st.sidebar.multiselect("Local", options=df["Local da oportunidade"].dropna().unique())
    modalidade = st.sidebar.multiselect("Modalidade de trabalho", options=df["Modalidade de trabalho"].dropna().unique())

    # --- FILTROS DINÂMICOS ---
    df_filtrado = df.dropna(subset=["Salário Numérico"])
    df_filtrado = df_filtrado[df_filtrado["Salário Numérico"].between(*salario_range)]

    if area:
        df_filtrado = df_filtrado[df_filtrado["Áreas de atuação da empresa e do setor"].isin(area)]

    if cargos:
        df_filtrado = df_filtrado[df_filtrado["Cargos"].isin(cargos)]

    if competencias_tec:
        df_filtrado = df_filtrado[df_filtrado["Competências técnicas"].str.contains(competencias_tec, case=False, na=False)]

    if competencias_transv:
        df_filtrado = df_filtrado[df_filtrado["Competências transversais"].str.contains(competencias_transv, case=False, na=False)]

    if local:
        df_filtrado = df_filtrado[df_filtrado["Local da oportunidade"].isin(local)]

    if modalidade:
        df_filtrado = df_filtrado[df_filtrado["Modalidade de trabalho"].isin(modalidade)]

    # --- GRÁFICO DE BARRAS: TOP SALÁRIOS ---
    st.subheader("💼 Top 10 Vagas com Maiores Salários")
    top_vagas = df_filtrado.sort_values(by="Salário Numérico", ascending=False).head(10)
    fig_bar = px.bar(top_vagas, x="Salário Numérico", y="Cargos", orientation="h",
                     labels={"Salário Numérico": "Salário (R$)", "Cargos": "Cargo"},
                     title="Top 10 Vagas com Maiores Salários")
    fig_bar.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- GRÁFICO DE PIZZA: Modalidade ---
    st.subheader("📌 Distribuição das Modalidades de Trabalho")
    fig_pie = px.pie(df_filtrado, names="Modalidade de trabalho", title="Modalidade das Vagas Filtradas")
    st.plotly_chart(fig_pie, use_container_width=True)

    # --- TABELA FINAL ---
    st.subheader("📋 Vagas Filtradas")
    st.dataframe(df_filtrado[
        ["QNT", "Cargos", "Salários", "Áreas de atuação da empresa e do setor", 
         "Competências técnicas", "Competências transversais", 
         "Local da oportunidade", "Modalidade de trabalho"]
    ])
else:
    st.info("Envie um arquivo CSV para começar.")
