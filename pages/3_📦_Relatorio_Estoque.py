import os
import io
import pandas as pd
import streamlit as st
from supabase import create_client, Client

SUPABASE_URL = "https://cfxrcnnuupabepbqascx.supabase.co"
SUPABASE_KEY = "sb_publishable_-Hoz_n3NdCndYmNETF4sDQ_9Bzphw5Q"
BUCKET_NOME = "dados-vonny"

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

supabase: Client = init_supabase()

st.set_page_config(
    page_title="Relatório de Estoque - Vonný",
    page_icon="icone.png",
    layout="wide",
)

st.markdown(
    """
    <style>
    header[data-testid="stHeader"] { background-color: #E6007E !important; }
    section[data-testid="stSidebar"] { border-right: 1px solid #F5CCD8; }
    h1, h2, h3 { color: #C5006B !important; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; }
    .stButton>button {
        width: 100%; background-color: #555555 !important; color: #FFFFFF !important;
        font-weight: bold !important; border-radius: 6px; height: 48px; border: none; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #333333 !important; color: #FFFFFF !important; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📋 Relatório Consolidado de Estoque")
st.markdown("Área de análise e filtros avançados do estoque atual.")

@st.cache_data(ttl=300)
def baixar_estoque():
    if not supabase:
        return None
    try:
        file_res = supabase.storage.from_(BUCKET_NOME).download("gestao/estoque_fixo.xlsx")
        if file_res:
            return pd.read_excel(io.BytesIO(file_res), engine="openpyxl")
    except Exception:
        return None
    return None

df_estoque = baixar_estoque()

if df_estoque is not None:
    st.markdown("### 🔍 Filtros Interativos")
    
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    df_filtrado_est = df_estoque.copy()
    
    # 1. Filtro por Loja (Divisão)
    if "Divisão" in df_estoque.columns:
        lojas_est = sorted(df_estoque["Divisão"].dropna().astype(str).unique())
        with f_col1:
            loja_escolhida_est = st.multiselect("Loja (Divisão)", options=lojas_est, key="filtro_loja_est")
        if loja_escolhida_est:
            df_filtrado_est = df_filtrado_est[df_filtrado_est["Divisão"].astype(str).isin(loja_escolhida_est)]
    
    # 2. Filtro por Material
    if "Material" in df_estoque.columns:
        materiais_est = sorted(df_estoque["Material"].dropna().astype(str).unique())
        with f_col2:
            material_escolhido_est = st.multiselect("Material", options=materiais_est, key="filtro_mat_est")
        if material_escolhido_est:
            df_filtrado_est = df_filtrado_est[df_filtrado_est["Material"].astype(str).isin(material_escolhido_est)]

    # 3. Filtro por Grupo de Mercadorias
    if "Grupo de mercadorias" in df_estoque.columns:
        grupos_est = sorted(df_estoque["Grupo de mercadorias"].dropna().astype(str).unique())
        with f_col3:
            grupo_escolhido_est = st.multiselect("Grupo de Mercadorias", options=grupos_est, key="filtro_grupo_est")
        if grupo_escolhido_est:
            df_filtrado_est = df_filtrado_est[df_filtrado_est["Grupo de mercadorias"].astype(str).isin(grupo_escolhido_est)]

    # 4. Filtro por Depósito
    col_deposito_possiveis = ["Depósito", "Deposito", "Dep."]
    col_dep_encontrada = next((c for c in col_deposito_possiveis if c in df_estoque.columns), None)
    
    if col_dep_encontrada:
        depositos_est = sorted(df_estoque[col_dep_encontrada].dropna().astype(str).unique())
        with f_col4:
            dep_escolhido_est = st.multiselect("Depósito", options=depositos_est, key="filtro_dep_est")
        if dep_escolhido_est:
            df_filtrado_est = df_filtrado_est[df_filtrado_est[col_dep_encontrada].astype(str).isin(dep_escolhido_est)]
    else:
        with f_col4:
            st.info("Coluna 'Depósito' não encontrada.")

    st.markdown(f"**Total de linhas exibidas:** {len(df_filtrado_est)}")
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(df_filtrado_est, use_container_width=True)
else:
    st.warning("⚠️ Nenhuma planilha de Estoque encontrada no Supabase. Faça o upload na aba de Gestão.")
