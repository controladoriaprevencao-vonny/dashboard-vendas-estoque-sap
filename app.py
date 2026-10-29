import pandas as pd
import streamlit as st

# Configuração da página web em modo expansivo
st.set_page_config(
    page_title="Dashboard Executivo SAP", page_icon="📊", layout="wide"
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
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📊 Dashboard Executivo - Vendas e Estoques SAP")
st.markdown(
    "Utilize o painel lateral à esquerda para carregar os relatórios e visualizar as análises de forma organizada."
)

# ==========================================
# ÁREA DE UPLOAD ORGANIZADA NA BARRA LATERAL
# ==========================================
with st.sidebar:
    st.header("📂 Painel de Upload")
    st.markdown("Faça o envio dos relatórios do SAP separadamente:")

    file_vendas = st.file_uploader(
        "1. Relatório de Vendas (.xlsx)", type=["xlsx"], key="vendas"
    )
    file_estoque = st.file_uploader(
        "2. Relatório de Estoques (.xlsx)", type=["xlsx"], key="estoque"
    )

    st.markdown("---")
    if st.button("🔄 Limpar Dados e Recarregar"):
        st.cache_data.clear()
        st.rerun()

# Lê os arquivos de forma independente assim que enviados
df_vendas = pd.read_excel(file_vendas) if file_vendas is not None else None
df_estoque = pd.read_excel(file_estoque) if file_estoque is not None else None

st.markdown("---")

# ==========================================
# SEÇÃO DE VENDAS (Independente)
# ==========================================
if df_vendas is not None:
    st.header("📈 Análises de Vendas")

    if "Quantidade faturada" in df_vendas.columns and "Preço interno" in df_vendas.columns:
        df_vendas["Quantidade faturada"] = pd.to_numeric(
            df_vendas["Quantidade faturada"], errors="coerce"
        ).fillna(0)
        df_vendas["Preço interno"] = pd.to_numeric(
            df_vendas["Preço interno"], errors="coerce"
        ).fillna(0)
        df_vendas["Subtotal 1"] = (
            df_vendas["Quantidade faturada"] * df_vendas["Preço interno"]
        )
        df_vendas["Valor líquido"] = (
            df_vendas["Quantidade faturada"] * df_vendas["Preço interno"]
        )

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

            # Centralização forçada via column_config
            st.dataframe(
                resumo_grupo,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Grupo de Mercadorias": st.column_config.TextColumn(
                        "Grupo de Mercadorias",
                        width="medium",
                        pinned=True,
                    ),
                    "Valor Líquido Total (R$)": st.column_config.TextColumn(
                        "Valor Líquido Total (R$)", width="medium"
                    ),
                },
            )
        else:
            st.warning("Colunas de resumo não encontradas no arquivo de Vendas.")

    with tab_v2:
        st.subheader("Média de Vendas por Produto")
        if (
            "Material" in df_vendas.columns
            and "Denominação de item" in df_vendas.columns
        ):
            media_prod = (
                df_vendas.groupby(["Material", "Denominação de item"])
                .agg({"Quantidade faturada": "mean", "Valor líquido": "mean"})
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
                        "Código Material"
                    ),
                    "Denominação de Item": st.column_config.TextColumn(
                        "Denominação de Item"
                    ),
                    "Média de Vendas (Qtd)": st.column_config.TextColumn(
                        "Média de Vendas (Qtd)"
                    ),
                    "Média de Valor Líquido (R$)": st.column_config.TextColumn(
                        "Média de Valor Líquido (R$)"
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
                .agg({"Quantidade faturada": "mean", "Preço interno": "mean"})
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
                        "Código Material"
                    ),
                    "Denominação de Item": st.column_config.TextColumn(
                        "Denominação de Item"
                    ),
                    "Média de Vendas (Qtd)": st.column_config.TextColumn(
                        "Média de Vendas (Qtd)"
                    ),
                    "Média de Preço Interno (R$)": st.column_config.TextColumn(
                        "Média de Preço Interno (R$)"
                    ),
                },
            )

# ==========================================
# SEÇÃO DE ESTOQUES (Independente)
# ==========================================
if df_estoque is not None:
    st.header("📋 Análises de Estoque")

    col_mat = (
        "Material" if "Material" in df_estoque.columns else df_estoque.columns[0]
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
            "Código Material": st.column_config.TextColumn("Código Material"),
            "Denominação de Item": st.column_config.TextColumn(
                "Denominação de Item"
            ),
            "Quantidade em Estoque": st.column_config.TextColumn(
                "Quantidade em Estoque"
            ),
            "Valor Total em Estoque (R$)": st.column_config.TextColumn(
                "Valor Total em Estoque (R$)"
            ),
        },
    )

if df_vendas is None and df_estoque is None:
    st.info(
        "👈 Utilize o painel lateral à esquerda para carregar o relatório de Vendas e/ou de Estoques e exibir os dados."
    )
