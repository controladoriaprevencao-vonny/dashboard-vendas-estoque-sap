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
    page_title="Relatório de Vendas - Vonný",
    page_icon="icone.png",
    layout="wide",
)

st.markdown(
    """
    <style>
    header[data-testid="stHeader"] { background-color: #E6007E !important; }
    section[data-testid="stSidebar"] { border-right: 1px solid #F5CCD8; }
    h1, h2, h3 { color: #C5006B !important; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; }
    </style>
""",
    unsafe_allow_html=True,
)

# Exibindo o logotipo no topo
try:
    st.image("icone.png", width=100)
except Exception:
    pass

st.title("📈 Relatório Executivo de Vendas")
st.markdown("Visualização consolidada de vendas por Loja e Material, ordenada automaticamente por maiores valores[cite: 6].")

@st.cache_data(ttl=300)
def baixar_vendas():
    if not supabase:
        return None
    try:
        file_res = supabase.storage.from_(BUCKET_NOME).download("gestao/vendas_fixo.xlsx")
        if file_res:
            return pd.read_excel(io.BytesIO(file_res), engine="openpyxl")
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
            loja_selecionada = st.multiselect("Filtrar por Loja (Divisão)", options=lojas, key="filtro_loja_vendas")
        if loja_selecionada:
            df_filtrado = df_filtrado[df_filtrado["Divisão"].astype(str).isin(loja_selecionada)]

    if "Material" in df_vendas.columns:
        materiais = sorted(df_vendas["Material"].dropna().astype(str).unique())
        with f2:
            material_selecionado = st.multiselect("Filtrar por Material", options=materiais, key="filtro_material_vendas")
        if material_selecionado:
            df_filtrado = df_filtrado[df_filtrado["Material"].astype(str).isin(material_selecionado)]

    if "Grupo de mercadorias" in df_vendas.columns:
        grupos = sorted(df_vendas["Grupo de mercadorias"].dropna().astype(str).unique())
        with f3:
            grupo_selecionado = st.multiselect("Filtrar por Grupo de Mercadorias", options=grupos, key="filtro_grupo_vendas")
        if grupo_selecionado:
            df_filtrado = df_filtrado[df_filtrado["Grupo de mercadorias"].astype(str).isin(grupo_selecionado)]

    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        total_qtd = df_filtrado["Quantidade faturada"].sum() if "Quantidade faturada" in df_filtrado.columns else 0
        st.metric("📦 Quantidade Total Faturada (Filtrado)", f"{total_qtd:,.0f}")
    with m2:
        total_val = df_filtrado["Valor líquido"].sum() if "Valor líquido" in df_filtrado.columns else 0
        st.metric("💰 Valor Líquido Total (Filtrado)", f"R$ {total_val:,.2f}")

    # ORDENAÇÃO AUTOMÁTICA: Maiores valores líquidos no topo por padrão[cite: 6]
    if "Valor líquido" in df_filtrado.columns:
        df_filtrado = df_filtrado.sort_values(by="Valor líquido", ascending=False)
    elif "Quantidade faturada" in df_filtrado.columns:
        df_filtrado = df_filtrado.sort_values(by="Quantidade faturada", ascending=False)

    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(df_filtrado, use_container_width=True)
else:
    st.warning("⚠️ Nenhuma planilha de Vendas encontrada no Supabase. Vá até a Central de Upload para enviar uma.")
