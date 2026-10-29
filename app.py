import pandas as pd
import streamlit as st

# Configuração da página web com o ícone personalizado
st.set_page_config(
    page_title="Dashboard Executivo - Vonný",
    page_icon="icone.png",
    layout="wide",
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

# Inicializa o estado da sessão para navegação e arquivos persistentes
if "perfil_atual" not in st.session_state:
    st.session_state.perfil_atual = "Home"

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "Home"

if "df_vendas_fixo" not in st.session_state:
    st.session_state.df_vendas_fixo = None

if "df_estoque_fixo" not in st.session_state:
    st.session_state.df_estoque_fixo = None

# ==========================================
# FUNÇÕES COM CACHE PARA LEITURA RÁPIDA
# ==========================================
@st.cache_data
def processar_vendas(uploaded_file):
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
def processar_estoque(uploaded_file):
    if uploaded_file is None:
        return None
    df = pd.read_excel(uploaded_file)
    return df

# ==========================================
# BARRA LATERAL (Navegação de Perfis)
# ==========================================
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    
    st.markdown("### Selecione o Perfil:")
    if st.button("🏠 Menu Principal"):
        st.session_state.perfil_atual = "Home"
        st.session_state.pagina_atual = "Home"
        st.rerun()
        
    if st.button("🛠️ Visão Administrativa"):
        st.session_state.perfil_atual = "Admin"
        st.rerun()
        
    if st.button("📦 Visão Gestão / Produtos"):
        st.session_state.perfil_atual = "Gerente"
        st.session_state.pagina_atual = "Home"
        st.rerun()

    st.markdown("---")
    
    # Status rápido das bases fixas
    st.markdown("### 📊 Status dos Dados Fixos")
    if st.session_state.df_vendas_fixo is not None:
        st.success("✅ Arquivo 1 Carregado")
    else:
        st.warning("⚠️ Arquivo 1 Ausente")
        
    if st.session_state.df_estoque_fixo is not None:
        st.success("✅ Arquivo 2 Carregado")
    else:
        st.warning("⚠️ Arquivo 2 Ausente")

# ==========================================
# 1. HOME / SELEÇÃO DE PERFIL
# ==========================================
if st.session_state.perfil_atual == "Home":
    st.title("📊 Dashboard Executivo - Vonný")
    st.markdown("Bem-vindo ao sistema de relatórios gerenciais integrados ao SAP. Escolha abaixo qual visão deseja acessar:")
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛠️ Visão Administrativa")
        st.markdown("Área restrita para upload, atualização e fixação das planilhas base que alimentarão os relatórios.")
        if st.button("Acessar Administrativo ➔", key="btn_admin"):
            st.session_state.perfil_atual = "Admin"
            st.rerun()
            
    with col2:
        st.markdown("### 📦 Visão Gerentes de Produto")
        st.markdown("Área executiva para análise interativa dos relatórios de vendas, estoques, rankings e filtros por loja.")
        if st.button("Acessar Gestão ➔", key="btn_gerente"):
            st.session_state.perfil_atual = "Gerente"
            st.session_state.pagina_atual = "Home"
            st.rerun()

# ==========================================
# 2. VISÃO ADMINISTRATIVA (UPLOAD E FIXAÇÃO)
# ==========================================
elif st.session_state.perfil_atual == "Admin":
    st.title("🛠️ Painel Administrativo - Gestão de Planilhas")
    st.markdown("Faça o upload dos arquivos complementares. Eles ficarão fixos na sessão para alimentar o painel.")

    col_up1, col_up2 = st.columns(2)

    with col_up1:
        st.markdown("**Arquivo 1**")
        file_vendas = st.file_uploader(
            "Upload Arquivo 1", 
            type=["xlsx"], 
            key="up_vendas", 
            label_visibility="collapsed"
        )
        if file_vendas is not None:
            st.session_state.df_vendas_fixo = processar_vendas(file_vendas)
            st.success("Arquivo 1 fixado com sucesso!")

    with col_up2:
        st.markdown("**Arquivo 2**")
        file_estoque = st.file_uploader(
            "Upload Arquivo 2", 
            type=["xlsx"], 
            key="up_estoque", 
            label_visibility="collapsed"
        )
        if file_estoque is not None:
            st.session_state.df_estoque_fixo = processar_estoque(file_estoque)
            st.success("Arquivo 2 fixado com sucesso!")

    st.markdown("---")
    
    if st.button("🔄 Limpar Dados Fixos da Sessão"):
        st.session_state.df_vendas_fixo = None
        st.session_state.df_estoque_fixo = None
        st.cache_data.clear()
        st.rerun()

# ==========================================
# 3. VISÃO DOS GERENTES DE PRODUTO
# ==========================================
elif st.session_state.perfil_atual == "Gerente":
    
    # Recupera os dados fixos salvos pelo admin
    df_vendas = st.session_state.df_vendas_fixo
    df_estoque = st.session_state.df_estoque_fixo

    # Sub-menu de navegação para o gerente
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🧭 Módulos Gerenciais")
        if st.button("📊 Menu Principal Gestão"):
            st.session_state.pagina_atual = "Home"
            st.rerun()
        if st.button("📈 Módulo de Vendas"):
            st.session_state.pagina_atual = "Vendas"
            st.rerun()
        if st.button("📋 Módulo de Estoques"):
            st.session_state.pagina_atual = "Estoques"
            st.rerun()

    # Página Inicial do Gerente
    if st.session_state.pagina_atual == "Home":
        st.title("📦 Visão Executiva - Gestão de Produtos")
        st.markdown("Selecione abaixo o módulo que deseja analisar com base nas planilhas oficiais fixadas pela administração:")

        st.markdown("<br>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("### 📈 Módulo de Vendas")
            st.markdown("Análises de faturamento por grupos, rankings, preço total real, filtros por loja e médias.")
            if st.button("Entrar em Vendas ➔", key="g_vendas"):
                st.session_state.pagina_atual = "Vendas"
                st.rerun()

        with col_g2:
            st.markdown("### 📋 Módulo de Estoques")
            st.markdown("Controle consolidado de inventário, ranking por valor imobilizado e utilização livre.")
            if st.button("Entrar em Estoques ➔", key="g_estoque"):
                st.session_state.pagina_atual = "Estoques"
                st.rerun()

    # Módulo de Vendas do Gerente
    elif st.session_state.pagina_atual == "Vendas":
        st.title("📈 Relatório Executivo de Vendas")

        if df_vendas is not None:
            tab_v1, tab_v2, tab_v3, tab_v4 = st.tabs(
                [
                    "Resumo por Grupos",
                    "Média de Vendas por Produto",
                    "Média Preço Interno",
                    "Preço Total Real",
                ]
            )

            def filtrar_por_loja(df, key_sufixo):
                if "Divisão" in df.columns:
                    divisões = ["TODAS"] + list(
                        df["Divisão"].dropna().astype(str).unique()
                    )
                    loja_selecionada = st.selectbox(
                        "Selecione a Loja:", divisões, key=f"filtro_loja_{key_sufixo}"
                    )
                    if loja_selecionada != "TODAS":
                        return df[df["Divisão"].astype(str) == loja_selecionada]
                return df

            with tab_v1:
                st.subheader("Resumo de Grupos de Mercadorias")
                df_f1 = filtrar_por_loja(df_vendas, "tab1")

                if (
                    "Grupo de mercadorias" in df_f1.columns
                    and "Valor líquido" in df_f1.columns
                ):
                    resumo_grupo = (
                        df_f1.groupby("Grupo de mercadorias")["Valor líquido"]
                        .sum()
                        .reset_index()
                    )
                    resumo_grupo = resumo_grupo.sort_values(by="Valor líquido", ascending=False).reset_index(drop=True)
                    resumo_grupo.insert(0, "Ranking", range(1, len(resumo_grupo) + 1))

                    resumo_grupo.columns = [
                        "Ranking",
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
                            "Ranking": st.column_config.TextColumn("Ranking", width="small"),
                            "Grupo de Mercadorias": st.column_config.TextColumn("Grupo de Mercadorias", width="medium"),
                            "Valor Líquido Total (R$)": st.column_config.TextColumn("Valor Líquido Total (R$)", width="medium"),
                        },
                    )
                else:
                    st.warning("Colunas necessárias não encontradas no arquivo de Vendas.")

            with tab_v2:
                st.subheader("Média de Vendas por Produto")
                df_f2 = filtrar_por_loja(df_vendas, "tab2")

                if (
                    "Material" in df_f2.columns
                    and "Denominação de item" in df_f2.columns
                ):
                    media_prod = (
                        df_f2.groupby(["Material", "Denominação de item"])
                        .agg(
                            {
                                "Quantidade faturada": "mean",
                                "Valor líquido": "mean",
                            }
                        )
                        .reset_index()
                    )
                    media_prod = media_prod.sort_values(by="Valor líquido", ascending=False).reset_index(drop=True)
                    media_prod.insert(0, "Ranking", range(1, len(media_prod) + 1))

                    media_prod.columns = [
                        "Ranking",
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
                            "Ranking": st.column_config.TextColumn("Ranking", width="small"),
                            "Código Material": st.column_config.TextColumn("Código Material", width="small"),
                            "Denominação de Item": st.column_config.TextColumn("Denominação de Item", width="large"),
                            "Média de Vendas (Qtd)": st.column_config.TextColumn("Média de Vendas (Qtd)", width="small"),
                            "Média de Valor Líquido (R$)": st.column_config.TextColumn("Média de Valor Líquido (R$)", width="medium"),
                        },
                    )

            with tab_v3:
                st.subheader("Média de Preço Interno por Produto")
                df_f3 = filtrar_por_loja(df_vendas, "tab3")

                if (
                    "Material" in df_f3.columns
                    and "Denominação de item" in df_f3.columns
                    and "Preço interno" in df_f3.columns
                ):
                    media_preco = (
                        df_f3.groupby(["Material", "Denominação de item"])
                        .agg(
                            {
                                "Quantidade faturada": "mean",
                                "Preço interno": "mean",
                            }
                        )
                        .reset_index()
                    )
                    media_preco = media_preco.sort_values(by="Preço interno", ascending=False).reset_index(drop=True)
                    media_preco.insert(0, "Ranking", range(1, len(media_preco) + 1))

                    media_preco.columns = [
                        "Ranking",
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
                            "Ranking": st.column_config.TextColumn("Ranking", width="small"),
                            "Código Material": st.column_config.TextColumn("Código Material", width="small"),
                            "Denominação de Item": st.column_config.TextColumn("Denominação de Item", width="large"),
                            "Média de Vendas (Qtd)": st.column_config.TextColumn("Média de Vendas (Qtd)", width="small"),
                            "Média de Preço Interno (R$)": st.column_config.TextColumn("Média de Preço Interno (R$)", width="medium"),
                        },
                    )

            with tab_v4:
                st.subheader("Preço Total Real das Vendas por Produto")
                df_f4 = filtrar_por_loja(df_vendas, "tab4")

                if (
                    "Material" in df_f4.columns
                    and "Denominação de item" in df_f4.columns
                    and "Quantidade faturada" in df_f4.columns
                    and "Valor líquido" in df_f4.columns
                ):
                    total_real = (
                        df_f4.groupby(["Material", "Denominação de item"])
                        .agg(
                            {
                                "Quantidade faturada": "sum",
                                "Valor líquido": "sum",
                            }
                        )
                        .reset_index()
                    )
                    total_real = total_real.sort_values(by="Valor líquido", ascending=False).reset_index(drop=True)
                    total_real.insert(0, "Ranking", range(1, len(total_real) + 1))

                    total_real.columns = [
                        "Ranking",
                        "Código Material",
                        "Denominação de Item",
                        "Quantidade Total Faturada",
                        "Preço Total Real (R$)",
                    ]

                    total_real["Quantidade Total Faturada"] = total_real[
                        "Quantidade Total Faturada"
                    ].apply(lambda x: f"{int(round(x)):,}".replace(",", "."))
                    total_real["Preço Total Real (R$)"] = total_real[
                        "Preço Total Real (R$)"
                    ].map("R$ {:,.2f}".format)

                    st.dataframe(
                        total_real,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Ranking": st.column_config.TextColumn("Ranking", width="small"),
                            "Código Material": st.column_config.TextColumn("Código Material", width="small"),
                            "Denominação de Item": st.column_config.TextColumn("Denominação de Item", width="large"),
                            "Quantidade Total Faturada": st.column_config.TextColumn("Quantidade Total Faturada", width="small"),
                            "Preço Total Real (R$)": st.column_config.TextColumn("Preço Total Real (R$)", width="medium"),
                        },
                    )
        else:
            st.warning("⚠️ O arquivo de Vendas fixo ainda não foi carregado pela administração. Acesse a **Visão Administrativa** para subir a planilha.")

    # Módulo de Estoques do Gerente
    elif st.session_state.pagina_atual == "Estoques":
        st.title("📋 Relatório Consolidado de Estoque")

        if df_estoque is not None:
            coluna_loja_estoque = None
            for col in ["Divisão", "Centro", "Depósito", "Local"]:
                if col in df_estoque.columns:
                    coluna_loja_estoque = col
                    break

            df_estoque_filtrado = df_estoque.copy()
            if coluna_loja_estoque:
                divisões_est = ["TODAS"] + list(
                    df_estoque[coluna_loja_estoque].dropna().astype(str).unique()
                )
                loja_est_selecionada = st.selectbox(
                    f"Selecione a Loja ({coluna_loja_estoque}):",
                    divisões_est,
                    key="filtro_loja_estoque",
                )
                if loja_est_selecionada != "TODAS":
                    df_estoque_filtrado = df_estoque_filtrado[
                        df_estoque_filtrado[coluna_loja_estoque].astype(str)
                        == loja_est_selecionada
                    ]

            col_mat = (
                "Material"
                if "Material" in df_estoque_filtrado.columns
                else df_estoque_filtrado.columns[0]
            )
            col_desc = (
                "Texto breve material"
                if "Texto breve material" in df_estoque_filtrado.columns
                else df_estoque_filtrado.columns[1]
            )
            col_qtd = (
                "Utilização livre"
                if "Utilização livre" in df_estoque_filtrado.columns
                else df_estoque_filtrado.columns[5]
            )
            col_val = (
                "Val.utiliz.livre"
                if "Val.utiliz.livre" in df_estoque_filtrado.columns
                else df_estoque_filtrado.columns[6]
            )

            df_estoque_filtrado[col_qtd] = pd.to_numeric(
                df_estoque_filtrado[col_qtd], errors="coerce"
            ).fillna(0)
            df_estoque_filtrado[col_val] = pd.to_numeric(
                df_estoque_filtrado[col_val], errors="coerce"
            ).fillna(0)

            resumo_est = (
                df_estoque_filtrado.groupby([col_mat, col_desc])
                .agg({col_qtd: "sum", col_val: "sum"})
                .reset_index()
            )
            
            resumo_est = resumo_est.sort_values(by=col_val, ascending=False).reset_index(drop=True)
            resumo_est.insert(0, "Ranking", range(1, len(resumo_est) + 1))

            resumo_est.columns = [
                "Ranking",
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
                    "Ranking": st.column_config.TextColumn("Ranking", width="small"),
                    "Código Material": st.column_config.TextColumn("Código Material", width="small"),
                    "Denominação de Item": st.column_config.TextColumn("Denominação de Item", width="large"),
                    "Quantidade em Estoque": st.column_config.TextColumn("Quantidade em Estoque", width="medium"),
                    "Valor Total em Estoque (R$)": st.column_config.TextColumn("Valor Total em Estoque (R$)", width="medium"),
                },
            )
        else:
            st.warning("⚠️ O arquivo de Estoques fixo ainda não foi carregado pela administração. Acesse a **Visão Administrativa** para subir a planilha.")
