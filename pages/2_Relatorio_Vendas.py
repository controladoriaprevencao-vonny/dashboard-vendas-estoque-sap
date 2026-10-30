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

st.title("📈 Relatório Executivo de Vendas")
st.markdown("Visualização de vendas consolidadas e detalhadas com ordenação precisa por Material e Data.")

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
    # --- 1. FILTRO GLOBAL (MANDANTE PARA TODA A PÁGINA) ---
    st.markdown("### 🌐 Filtro Global (Mandante da Página)")
    g1, g2, g3 = st.columns(3)
    
    df_global = df_vendas.copy()

    if "Divisão" in df_vendas.columns:
        lojas_g = sorted(df_vendas["Divisão"].dropna().astype(str).unique())
        with g1:
            loja_g = st.multiselect("Loja Global (Divisão)", options=lojas_g, key="global_loja")
        if loja_g:
            df_global = df_global[df_global["Divisão"].astype(str).isin(loja_g)]

    if "Material" in df_vendas.columns:
        mat_g = sorted(df_vendas["Material"].dropna().astype(str).unique())
        with g2:
            material_g = st.multiselect("Material Global", options=mat_g, key="global_material")
        if material_g:
            df_global = df_global[df_global["Material"].astype(str).isin(material_g)]

    if "Grupo de mercadorias" in df_vendas.columns:
        grupo_g = sorted(df_vendas["Grupo de mercadorias"].dropna().astype(str).unique())
        with g3:
            grupo_sel_g = st.multiselect("Grupo Global", options=grupo_g, key="global_grupo")
        if grupo_sel_g:
            df_global = df_global[df_global["Grupo de mercadorias"].astype(str).isin(grupo_sel_g)]

    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        total_qtd = df_global["Quantidade faturada"].sum() if "Quantidade faturada" in df_global.columns else 0
        st.metric("📦 Quantidade Total Faturada (Global)", f"{total_qtd:,.0f}".replace(",", "."))
    with m2:
        total_val = df_global["Valor líquido"].sum() if "Valor líquido" in df_global.columns else 0
        st.metric("💰 Valor Líquido Total (Global)", f"R$ {total_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("---")

    # --- TABELA 1: CONSOLIDADA ---
    st.markdown("### 📊 Visão Consolidada (Agrupada)")
    
    with st.expander("🔍 Filtros específicos da Tabela Consolidada"):
        fc1, fc2 = st.columns(2)
        df_cons_filtrado = df_global.copy()
        
        if "Divisão" in df_cons_filtrado.columns:
            l_cons = sorted(df_cons_filtrado["Divisão"].dropna().astype(str).unique())
            with fc1:
                sel_l_cons = st.multiselect("Filtrar Loja (Consolidado)", options=l_cons, key="cons_loja")
            if sel_l_cons:
                df_cons_filtrado = df_cons_filtrado[df_cons_filtrado["Divisão"].astype(str).isin(sel_l_cons)]

        if "Material" in df_cons_filtrado.columns:
            m_cons = sorted(df_cons_filtrado["Material"].dropna().astype(str).unique())
            with fc2:
                sel_m_cons = st.multiselect("Filtrar Material (Consolidado)", options=m_cons, key="cons_mat")
            if sel_m_cons:
                df_cons_filtrado = df_cons_filtrado[df_cons_filtrado["Material"].astype(str).isin(sel_m_cons)]

    colunas_agrupamento = [c for c in ["Divisão", "Material", "Denominação de item", "Grupo de mercadorias"] if c in df_cons_filtrado.columns]
    colunas_soma = [c for c in ["Quantidade faturada", "Valor líquido", "Subtotal 1", "Preço interno"] if c in df_cons_filtrado.columns]
    
    if colunas_agrupamento and colunas_soma:
        df_consolidado = df_cons_filtrado.groupby(colunas_agrupamento, as_index=False)[colunas_soma].sum()
    else:
        df_consolidado = df_cons_filtrado.copy()

    if "Valor líquido" in df_consolidado.columns:
        df_consolidado = df_consolidado.sort_values(by="Valor líquido", ascending=False)

    config_colunas_cons = {}
    for col in df_consolidado.columns:
        col_lower = col.lower()
        if "valor" in col_lower or "liquido" in col_lower or "subtotal" in col_lower or "preço" in col_lower or "preco" in col_lower:
            config_colunas_cons[col] = st.column_config.NumberColumn(col, format="R$ %,.2f")
        elif "quantidade" in col_lower or "utiliz" in col_lower:
            config_colunas_cons[col] = st.column_config.NumberColumn(col, format="%,.0f")

    st.dataframe(df_consolidado, use_container_width=True, column_config=config_colunas_cons)


    # --- TABELA 2: COMPLETA / DETALHADA ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📋 Visão Completa (Detalhada / Sem Consolidação)")
    
    with st.expander("🔍 Filtros específicos da Tabela Detalhada (Incluindo Análise Inteligente de Devolução)"):
        fd1, fd2, fd3, fd4 = st.columns(4)
        df_det_filtrado = df_global.copy()
        
        if "Divisão" in df_det_filtrado.columns:
            l_det = sorted(df_det_filtrado["Divisão"].dropna().astype(str).unique())
            with fd1:
                sel_l_det = st.multiselect("Filtrar Loja (Detalhado)", options=l_det, key="det_loja")
            if sel_l_det:
                df_det_filtrado = df_det_filtrado[df_det_filtrado["Divisão"].astype(str).isin(sel_l_det)]

        if "Material" in df_det_filtrado.columns:
            m_det = sorted(df_det_filtrado["Material"].dropna().astype(str).unique())
            with fd2:
                sel_m_det = st.multiselect("Filtrar Material (Detalhado)", options=m_det, key="det_mat")
            if sel_m_det:
                df_det_filtrado = df_det_filtrado[df_det_filtrado["Material"].astype(str).isin(sel_m_det)]

        # Filtro tradicional de Devolução
        col_dev_possiveis = ["Devolução", "Devolucao"]
        col_dev_encontrada = next((c for c in col_dev_possiveis if c in df_det_filtrado.columns), None)
        
        filtro_inteligente_ativo = False

        if col_dev_encontrada:
            dev_ops = sorted(df_det_filtrado[col_dev_encontrada].dropna().astype(str).unique())
            with fd3:
                sel_dev = st.multiselect("Filtro Direto Devolução", options=dev_ops, key="det_dev")
            if sel_dev:
                df_det_filtrado = df_det_filtrado[df_det_filtrado[col_dev_encontrada].astype(str).isin(sel_dev)]

            # NOVO FILTRO INTELIGENTE DE DEVOLUÇÃO POR MATERIAL
            with fd4:
                sel_dev_inteligente = st.multiselect("Análise: Trazer Material Completo com Devolução", options=dev_ops, key="det_dev_inteligente")
            
            if sel_dev_inteligente and "Material" in df_det_filtrado.columns:
                materiais_com_devolucao = df_det_filtrado[df_det_filtrado[col_dev_encontrada].astype(str).isin(sel_dev_inteligente)]["Material"].unique()
                df_det_filtrado = df_det_filtrado[df_det_filtrado["Material"].isin(materiais_com_devolucao)]
                filtro_inteligente_ativo = True
        else:
            with fd3:
                st.info("Coluna 'Devolução' não encontrada.")
            with fd4:
                st.info("Indisponível.")

    # Identifica coluna de data para ordenação cronológica precisa
    col_data_encontrada = next((c for c in df_det_filtrado.columns if "data" in c.lower()), None)

    # ORDENAÇÃO
    if filtro_inteligente_ativo and "Material" in df_det_filtrado.columns and col_data_encontrada:
        # Cria cópia temporária da data convertida em datetime para ordenar perfeitamente de forma cronológica
        df_det_filtrado["_data_temp"] = pd.to_datetime(df_det_filtrado[col_data_encontrada], errors="coerce")
        df_det_filtrado = df_det_filtrado.sort_values(by=["Material", "_data_temp"], ascending=[True, True])
        df_det_filtrado = df_det_filtrado.drop(columns=["_data_temp"])
    elif filtro_inteligente_ativo and "Material" in df_det_filtrado.columns:
        df_det_filtrado = df_det_filtrado.sort_values(by="Material", ascending=True)
    else:
        if "Valor líquido" in df_det_filtrado.columns:
            df_det_filtrado = df_det_filtrado.sort_values(by="Valor líquido", ascending=False)

    # Tratamento final de exibição das datas para o formato DD/MM/AAAA limpo nas células
    for col in df_det_filtrado.columns:
        if "data" in col.lower():
            df_det_filtrado[col] = pd.to_datetime(df_det_filtrado[col], errors="coerce").dt.strftime("%d/%m/%Y").fillna(df_det_filtrado[col])

    config_colunas_det = {}
    for col in df_det_filtrado.columns:
        col_lower = col.lower()
        if "valor" in col_lower or "liquido" in col_lower or "subtotal" in col_lower or "preço" in col_lower or "preco" in col_lower:
            config_colunas_det[col] = st.column_config.NumberColumn(col, format="R$ %,.2f")
        elif "quantidade" in col_lower or "utiliz" in col_lower:
            config_colunas_det[col] = st.column_config.NumberColumn(col, format="%,.0f")

    st.dataframe(df_det_filtrado, use_container_width=True, column_config=config_colunas_det)

else:
    st.warning("⚠️ Nenhuma planilha de Vendas encontrada no Supabase. Vá até a Central de Upload para enviar uma.")
