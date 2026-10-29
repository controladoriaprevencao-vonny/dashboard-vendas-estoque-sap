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
