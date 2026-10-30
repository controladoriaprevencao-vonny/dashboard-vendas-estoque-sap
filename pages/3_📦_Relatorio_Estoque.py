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

st.title("📋 Relatório Consolidado de Estoque")
st.markdown("Consulta e filtros do estoque atual hospedado na nuvem.")

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
    f_col1, f_col2 = st.columns(2)
    df_filtrado = df_estoque.copy()
    
    if "Divisão" in df_estoque.columns:
        lojas = sorted(df_estoque["Divisão"].dropna().astype(str).unique())
        with f_col1:
            l_sel = st.multiselect("Filtrar por Loja (Divisão)", options=lojas)
        if l_sel:
            df_filtrado = df_filtrado[df_filtrado["Divisão"].astype(str).isin(l_sel)]
            
    if "Material" in df_estoque.columns:
        materiais = sorted(df_estoque["Material"].dropna().astype(str).unique())
        with f_col2:
            m_sel = st.multiselect("Filtrar por Material", options=materiais)
        if m_sel:
            df_filtrado = df_filtrado[df_filtrado["Material"].astype(str).isin(m_sel)]

    st.markdown(f"**Total de linhas exibidas:** {len(df_filtrado)}")
    st.dataframe(df_filtrado, use_container_width=True)
else:
    st.warning("⚠️ Nenhuma planilha de Estoque encontrada no Supabase. Faça o upload na aba de Gestão.")
