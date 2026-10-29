import pandas as pd
import streamlit as st

# Configuração da página web
st.set_page_config(
    page_title="Dashboard Executivo - Vonný", page_icon="📊", layout="wide"
)

# Estilo visual corporativo e limpo
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    h1, h2, h3 {
        color: #1F4E79;
    }
    .stButton>button {
        width: 100%;
        background-color: #1F4E79;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 50px;
    }
    .stButton>button:hover {
        background-color: #153a5b;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Inicializa o estado de navegação
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "Home"

# ==========================================
# FUNÇÕES COM CACHE PARA LEITURA RÁPIDA
# ==========================================
@st.cache_data
def carregar_vendas(uploaded_file):
    if uploaded_file is None:
        return None
    df = pd.read_excel(uploaded_file)
    if "Quantidade faturada" in df.columns and "Preço interno" in df.columns:
        df["Quantidade faturada"] = pd.to_numeric(
            df["Quantidade faturada"], errors="coerce"
        ).fillna(0)
        df["Preço interno"] = pd.to_numeric(
            df["Preço interno"], errors="coerce"
        ).fillna(0)
        df["Valor líquido"] = df["Quantidade faturada"] * df["Preço interno"]
    return df

@st.cache_data
def carregar_estoque(uploaded_file):
    if uploaded_file is None:
        return None
    df = pd.read_excel(uploaded_file)
    return df

# ==========================================
# BARRA LATERAL (Upload e Configurações)
# ==========================================
with st.sidebar:
    st.header("📂 Painel de Upload")
    st.markdown("Carregue os relatórios do SAP:")

    file_vendas = st.file_uploader(
        "Relatório de Vendas (.xlsx)", type=["xlsx"], key="vendas"
    )
    file_estoque = st.file_uploader(
        "Relatório de Estoques (.xlsx)", type=["xlsx"], key="estoque"
    )

    st.markdown("---")
    if st.button("🏠 Voltar ao Menu Principal"):
        st.session_state.pagina_atual = "Home"
        st.rerun()

    if st.button("🔄 Limpar Dados e Cache"):
        st.cache_data.clear()
        st.rerun()

# Carrega os dados usando as funções otimizadas com cache
df_vendas = carregar_vendas(file_vendas)
df_estoque = carregar_estoque(file_estoque)

# ==========================================
# NAVEGAÇÃO ENTRE PÁGINAS (HOME / VENDAS / ESTOQUE)
# ==========================================

if st.session_state.pagina_atual == "Home":
    st.title("📊 Dashboard Executivo - Vonný")
    st.markdown(
        "Bem-vindo ao sistema de relatórios gerenciais do SAP. Escolha abaixo qual módulo deseja acessar:"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        st.markdown("### 📈 Módulo de Vendas")
        st.markdown(
            "Análises de faturamento por grupos de mercadorias, filtros por loja e médias de vendas e preços."
        )
        if st.button("Acessar Vendas ➔", key="btn_vendas"):
            st.session_state.pagina_atual = "Vendas"
            st.rerun()

    with col_btn2:
        st.markdown("### 📋 Módulo de Estoques")
        st.markdown(
            "Controle consolidado de inventário, quantidades em utilização livre e valor total em estoque."
        )
        if st.button("Acessar Estoques ➔", key="btn_estoques"):
            st.session_state.pagina_atual = "Estoques"
            st.rerun()

    if df_vendas is None and df_estoque is None:
        st.info(
            "💡 Dica: Faça o upload dos arquivos do SAP na barra lateral esquerda para habilitar os relatórios."
        )

# ==========================================
# PÁGINA DE VENDAS
# ==========================================
elif st.session_state.pagina_atual == "Vendas":
    st.title("📈 Relatório Executivo de Vendas")

    if df_vendas is not None:
        tab_v1, tab_v2, tab_v3 = st.tabs(
            [
                "Resumo por Grupos",
                "Média de Vendas por Produto",
                "Média Preço Interno",
            ]
        )

        with tab_v1:
            st.subheader("Resumo de Grupos de Mercadorias")
            if "Divisão" in df_vendas.columns:
                divisões = ["TODAS"] + list(
                    df_vendas["Divisão"].dropna().astype(str).unique()
                )
                loja_selecionada = st.selectbox(
                    "Selecione a Loja:", divisões, key="filtro_loja"
                )

                df_filtrado = df_vendas.copy()
                if loja_selecionada != "TODAS":
                    df_filtrado = df_filtrado[
                        df_filtrado["Divisão"].astype(str) == loja_selecionada
                    ]
            else:
                df_filtrado = df_vendas.copy()

            if (
                "Grupo de mercadorias" in df_filtrado.columns
                and "Valor líquido" in df_filtrado.columns
            ):
                resumo_grupo = (
                    df_filtrado.groupby("Grupo de mercadorias")["Valor líquido"]
                    .sum()
                    .reset_index()
                )
                resumo_grupo.columns = [
                    "Grupo de Mercadorias",
                    "Valor Líquido Total (R$)",
                ]
                resumo_grupo["Valor Líquido Total (R$)"] = resumo_grupo[
                    "Valor Líquido Total (R$)"
                ].map("R$ {:,.2f}".format)

                st.dataframe(
                    resumo_grupo,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Grupo de Mercadorias": st.column_config.TextColumn(
                            "Grupo de Mercadorias", width="medium"
                        ),
                        "Valor Líquido Total (R$)": st.column_config.TextColumn(
                            "Valor Líquido Total (R$)", width="medium"
                        ),
                    },
                )
            else:
                st.warning(
                    "Colunas necessárias não encontradas no arquivo de Vendas."
                )

        with tab_v2:
            st.subheader("Média de Vendas por Produto")
            if (
                "Material" in df_vendas.columns
                and "Denominação de item" in df_vendas.columns
            ):
                media_prod = (
                    df_vendas.groupby(["Material", "Denominação de item"])
                    .agg(
                        {
                            "Quantidade faturada": "mean",
                            "Valor líquido": "mean",
                        }
                    )
                    .reset_index()
                )
                media_prod.columns = [
                    "Código Material",
                    "Denominação de Item",
                    "Média de Vendas (Qtd)",
                    "Média de Valor Líquido (R$)",
                ]

                media_prod["Média de Vendas (Qtd)"] = media_prod[
                    "Média de Vendas (Qtd)"
                ].apply(lambda x: f"{int(round(x)):,}".replace(",", "."))
                media_prod["Média de Valor Líquido (R$)"] = media_prod[
                    "Média de Valor Líquido (R$)"
                ].map("R$ {:,.2f}".format)

                st.dataframe(
                    media_prod,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Código Material": st.column_config.TextColumn(
                            "Código Material", width="small"
                        ),
                        "Denominação de Item": st.column_config.TextColumn(
                            "Denominação de Item", width="large"
                        ),
                        "Média de Vendas (Qtd)": st.column_config.TextColumn(
                            "Média de Vendas (Qtd)", width="small"
                        ),
                        "Média de Valor Líquido (R$)": st.column_config.TextColumn(
                            "Média de Valor Líquido (R$)", width="medium"
                        ),
                    },
                )

        with tab_v3:
            st.subheader("Média de Preço Interno por Produto")
            if (
                "Material" in df_vendas.columns
                and "Denominação de item" in df_vendas.columns
                and "Preço interno" in df_vendas.columns
            ):
                media_preco = (
                    df_vendas.groupby(["Material", "Denominação de item"])
                    .agg(
                        {
                            "Quantidade faturada": "mean",
                            "Preço interno": "mean",
                        }
                    )
                    .reset_index()
                )
                media_preco.columns = [
                    "Código Material",
                    "Denominação de Item",
                    "Média de Vendas (Qtd)",
                    "Média de Preço Interno (R$)",
                ]

                media_preco["Média de Vendas (Qtd)"] = media_preco[
                    "Média de Vendas (Qtd)"
                ].apply(lambda x: f"{int(round(x)):,}".replace(",", "."))
                media_preco["Média de Preço Interno (R$)"] = media_preco[
                    "Média de Preço Interno (R$)"
                ].map("R$ {:,.2f}".format)

                st.dataframe(
                    media_preco,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Código Material": st.column_config.TextColumn(
                            "Código Material", width="small"
                        ),
                        "Denominação de Item": st.column_config.TextColumn(
                            "Denominação de Item", width="large"
                        ),
                        "Média de Vendas (Qtd)": st.column_config.TextColumn(
                            "Média de Vendas (Qtd)", width="small"
                        ),
                        "Média de Preço Interno (R$)": st.column_config.TextColumn(
                            "Média de Preço Interno (R$)", width="medium"
                        ),
                    },
                )
    else:
        st.warning(
            "⚠️ O arquivo de Vendas ainda não foi carregado. Faça o upload na barra lateral."
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ Voltar ao Menu Principal"):
        st.session_state.pagina_atual = "Home"
        st.rerun()

# ==========================================
# PÁGINA DE ESTOQUES
# ==========================================
elif st.session_state.pagina_atual == "Estoques":
    st.title("📋 Relatório Consolidado de Estoque")

    if df_estoque is not None:
        col_mat = (
            "Material"
            if "Material" in df_estoque.columns
            else df_estoque.columns[0]
        )
        col_desc = (
            "Texto breve material"
            if "Texto breve material" in df_estoque.columns
            else df_estoque.columns[1]
        )
        col_qtd = (
            "Utilização livre"
            if "Utilização livre" in df_estoque.columns
            else df_estoque.columns[5]
        )
        col_val = (
            "Val.utiliz.livre"
            if "Val.utiliz.livre" in df_estoque.columns
            else df_estoque.columns[6]
        )

        df_estoque[col_qtd] = pd.to_numeric(
            df_estoque[col_qtd], errors="coerce"
        ).fillna(0)
        df_estoque[col_val] = pd.to_numeric(
            df_estoque[col_val], errors="coerce"
        ).fillna(0)

        resumo_est = (
            df_estoque.groupby([col_mat, col_desc])
            .agg({col_qtd: "sum", col_val: "sum"})
            .reset_index()
        )
        resumo_est.columns = [
            "Código Material",
            "Denominação de Item",
            "Quantidade em Estoque",
            "Valor Total em Estoque (R$)",
        ]

        resumo_est["Quantidade em Estoque"] = resumo_est[
            "Quantidade em Estoque"
        ].apply(lambda x: f"{int(x):,}".replace(",", "."))
        resumo_est["Valor Total em Estoque (R$)"] = resumo_est[
            "Valor Total em Estoque (R$)"
        ].map("R$ {:,.2f}".format)

        st.dataframe(
            resumo_est,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Código Material": st.column_config.TextColumn(
                    "Código Material", width="small"
                ),
                "Denominação de Item": st.column_config.TextColumn(
                    "Denominação de Item", width="large"
                ),
                "Quantidade em Estoque": st.column_config.TextColumn(
                    "Quantidade em Estoque", width="medium"
                ),
                "Valor Total em Estoque (R$)": st.column_config.TextColumn(
                    "Valor Total em Estoque (R$)", width="medium"
                ),
            },
        )
    else:
        st.warning(
            "⚠️ O arquivo de Estoques ainda não foi carregado. Faça o upload na barra lateral."
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ Voltar ao Menu Principal"):
        st.session_state.pagina_atual = "Home"
        st.rerun()
