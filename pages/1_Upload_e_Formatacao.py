import streamlit as st

st.markdown("### Upload de Gestão Fixo")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Planilha de Estoque")
    # Componente de upload
    arquivo_estoque = st.file_uploader(
        "Envie a planilha de estoque", type=["xlsx", "xlsm"], key="up_estoque"
    )

    # Se um arquivo foi enviado agora, exibe as informações dele
    if arquivo_estoque is not None:
        st.success(f"✅ **Arquivo selecionado:** {arquivo_estoque.name}")
        st.info(
            f"📦 **Tamanho:** {arquivo_estoque.size / 1024:.2f} KB | **Tipo:** {arquivo_estoque.type}"
        )
        # Aqui você pode chamar sua função que envia para o Supabase
        # st.button("Confirmar Envio para o Supabase", key="btn_envio_estoque")
    else:
        # Opcional: Mostrar qual arquivo já está ativo no Supabase atualmente
        st.warning("⚠️ Nenhum novo arquivo selecionado. O sistema está utilizando o arquivo atual gravado no Supabase.")

with col2:
    st.markdown("#### Planilha de Vendas")
    arquivo_vendas = st.file_uploader(
        "Envie a planilha de vendas", type=["xlsx", "xlsm"], key="up_vendas"
    )

    if arquivo_vendas is not None:
        st.success(f"✅ **Arquivo selecionado:** {arquivo_vendas.name}")
        st.info(
            f"📊 **Tamanho:** {arquivo_vendas.size / 1024:.2f} KB | **Tipo:** {arquivo_vendas.type}"
        )
    else:
        st.warning("⚠️ Nenhum novo arquivo selecionado. O sistema está utilizando o arquivo atual gravado no Supabase.")
