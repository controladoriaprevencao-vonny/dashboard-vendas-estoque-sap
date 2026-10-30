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

st.title("📈 Relatório Executivo de Vendas")
st.markdown("Dados consolidados por Loja e Material com filtros interativos.")

def processar_vendas_consolidado(file_bytes):
    if file_bytes is None:
        return None
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
        if "Quantidade faturada" in df.columns:
            df["Quantidade faturada"] = pd.to_numeric(df["Quantidade faturada"], errors="coerce").fillna(0)
        if "Preço interno" in df.columns:
            df["Preço interno"] = pd.to_numeric(df["Preço interno"], errors="coerce").fillna(0)
        if "Quantidade faturada" in df.columns and "Preço interno" in df.columns:
            df["Valor líquido"] = df["Quantidade faturada"] * df["Preço interno"]
        
        if "Divisão" in df.columns and "Material" in df.columns:
            agg_dict = {"Quantidade faturada": "sum"}
            if "Valor líquido" in df.columns:
                agg_dict["Valor líquido"] = "sum"
            if "Denominação de item" in df.columns:
                agg_dict["Denominação de item"] = "first"
            if "Grupo de mercadorias" in df.columns:
                agg_dict["Grupo de mercadorias"] = "first"
            
            df = df.groupby(["Divisão", "Material"], as_index=False).agg(agg_dict)
        return df
    except Exception:
        return None

@st.cache_data(ttl=300)
def baixar_vendas():
    if not supabase:
        return None
    try:
        file_res = supabase.storage.from_(BUCKET_NOME).download("gestao/vendas_fixo.xlsx")
        if file_res:
            return processar_vendas_consolidado(file_res)
    except Exception:
        return None
    return None

df_vendas = baixar_vendas()

if df_vendas is not None:
    st.markdown("### 🔍 Filtros Interativos")
    f1, f2, f3 = st.columns(3)
    df_filtrado = df_vendas.copy()
    
    if "Divisão" in df_vendas.columns:
        lojas = sorted(df_vendas["Divisão"].dropna().astype(str).unique())
        with f1:
            l_sel = st.multiselect("Filtrar por Loja (Divisão)", options=lojas)
        if l_sel:
            df_filtrado = df_filtrado[df_filtrado["Divisão"].astype(str).isin(l_sel)]
            
    if "Material" in df_vendas.columns:
        materiais = sorted(df_vendas["Material"].dropna().astype(str).unique())
        with f2:
            m_sel = st.multiselect("Filtrar por Material", options=materiais)
        if m_sel:
            df_filtrado = df_filtrado[df_filtrado["Material"].astype(str).isin(m_sel)]
            
    if "Grupo de mercadorias" in df_vendas.columns:
        grupos = sorted(df_vendas["Grupo de mercadorias"].dropna().astype(str).unique())
        with f3:
            g_sel = st.multiselect("Filtrar por Grupo", options=grupos)
        if g_sel:
            df_filtrado = df_filtrado[df_filtrado["Grupo de mercadorias"].astype(str).isin(g_sel)]

    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        st.metric("📦 Quantidade Total Faturada", f"{df_filtrado['Quantidade faturada'].sum():,.0f}")
    with m2:
        st.metric("💰 Valor Líquido Total", f"R$ {df_filtrado['Valor líquido'].sum():,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(df_filtrado, use_container_width=True)
else:
    st.warning("⚠️ Nenhuma planilha de Vendas encontrada no Supabase. Faça o upload na aba de Gestão.")
