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

# Estilização para garantir que as células e tabelas expandam e mostrem o conteúdo inteiro
st.markdown(
    """
    <style>
    header[data-testid="stHeader"] { background-color: #E6007E !important; }
    section[data-testid="stSidebar"] { border-right: 1px solid #F5CCD8; }
    h1, h2, h3 { color: #C5006B !important; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; }
    div[data-testid="stDataFrame"] { width: 100% !important; }
    </style>
""",
    unsafe_allow_html=True,
)

# Exibindo o logotipo no topo
try:
    st.image("icone.png", width=100)
except Exception:
    pass

st.title("📋 Relatório Consolidado de Estoque")
st.markdown("Área de análise e filtros inteligentes em cascata do estoque atual, ordenados pela coluna **Val.utiliz.libre**.")

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
    st.markdown("### 🔍 Filtros Interativos Inteligentes")
    
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    
    colunas_loja_possiveis = ["Centro", "Divisão", "Divisao", "Loja"]
    col_loja_encontrada = next((c for c in colunas_loja_possiveis if c in df_estoque.columns), None)
    
    col_deposito_possiveis = ["Depósito", "Deposito", "Dep."]
    col_dep_encontrada = next((c for c in col_deposito_possiveis if c in df_estoque.columns), None)

    # --- FILTRO 1: CENTRO / LOJA ---
    df_f1 = df_estoque.copy()
    if col_loja_encontrada:
        lojas_opcoes = sorted(df_f1[col_loja_encontrada].dropna().astype(str).unique())
        with f_col1:
            loja_escolhida_est = st.multiselect("Centro / Loja", options=lojas_opcoes, key="filtro_loja_est")
        if loja_escolhida_est:
            df_f1 = df_f1[df_f1[col_loja_encontrada].astype(str).isin(loja_escolhida_est)]
    else:
        with f_col1:
            st.info("Coluna 'Centro' não encontrada.")

    # --- FILTRO 2: MATERIAL ---
    df_f2 = df_f1.copy()
    if "Material" in df_estoque.columns:
        materiais_opcoes = sorted(df_f2["Material"].dropna().astype(str).unique())
        with f_col2:
            material_escolhido_est = st.multiselect("Material", options=materiais_opcoes, key="filtro_mat_est")
        if material_escolhido_est:
            df_f2 = df_f2[df_f2["Material"].astype(str).isin(material_escolhido_est)]

    # --- FILTRO 3: GRUPO DE MERCADORIAS ---
    df_f3 = df_f2.copy()
    if "Grupo de mercadorias" in df_estoque.columns:
        grupos_opcoes = sorted(df_f3["Grupo de mercadorias"].dropna().astype(str).unique())
        with f_col3:
            grupo_escolhido_est = st.multiselect("Grupo de Mercadorias", options=grupos_opcoes, key="filtro_grupo_est")
        if grupo_escolhido_est:
            df_f3 = df_f3[df_f3["Grupo de mercadorias"].astype(str).isin(grupo_escolhido_est)]

    # --- FILTRO 4: DEPÓSITO ---
    df_filtrado_est = df_f3.copy()
    if col_dep_encontrada:
        depositos_opcoes = sorted(
            [str(int(x)) for x in pd.to_numeric(df_filtrado_est[col_dep_encontrada].dropna(), errors="coerce").unique() if pd.notna(x)]
        )
        with f_col4:
            dep_escolhido_est = st.multiselect("Depósito", options=depositos_opcoes, key="filtro_dep_est")
        
        if dep_escolhido_est:
            df_filtrado_est = df_filtrado_est[
                pd.to_numeric(df_filtrado_est[col_dep_encontrada], errors="coerce")
                .fillna(-999999)
                .astype(int)
                .astype(str)
                .isin(dep_escolhido_est)
            ]
    else:
        with f_col4:
            st.info("Coluna 'Depósito' não encontrada.")

    # ORDENAÇÃO EXCLUSIVA: Coluna "Val.utiliz.libre" (Positivos primeiro, do maior para o menor)
    col_alvo = "Val.utiliz.libre"
    if col_alvo in df_filtrado_est.columns:
        df_filtrado_est[col_alvo] = pd.to_numeric(df_filtrado_est[col_alvo], errors="coerce").fillna(0)
        df_filtrado_est["_prioridade"] = df_filtrado_est[col_alvo].apply(lambda x: 1 if x >= 0 else 0)
        df_filtrado_est = df_filtrado_est.sort_values(by=["_prioridade", col_alvo], ascending=[False, False])
        df_filtrado_est = df_filtrado_est.drop(columns=["_prioridade"])

    st.markdown(f"**Total de linhas exibidas:** {len(df_filtrado_est)}")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Configuração de colunas: Valores em Real (R$) com separador de milhar e quantidades formatadas
    config_colunas_est = {}
    for col in df_filtrado_est.columns:
        col_lower = col.lower()
        if "val" in col_lower or "valor" in col_lower:
            config_colunas_est[col] = st.column_config.NumberColumn(
                col, format="R$ %,.2f", help="Valores em Real"
            )
        elif "utiliz" in col_lower or "quant" in col_lower or "estoque" in col_lower:
            config_colunas_est[col] = st.column_config.NumberColumn(
                col, format="%,.0f", help="Quantidades"
            )

    st.dataframe(df_filtrado_est, use_container_width=True, column_config=config_colunas_est)
else:
    st.warning("⚠️ Nenhuma planilha de Estoque encontrada no Supabase. Faça o upload na aba de Gestão.")
