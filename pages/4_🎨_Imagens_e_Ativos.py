import streamlit as st

st.title("🎨 Gestão de Imagens e Ativos - Vonný")
st.markdown("Espaço reservado para visualização de logotipos e identidade visual da aplicação.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Logotipo Principal")
    try:
        st.image("logo_vonny.png", width=250)
    except Exception:
        st.info("O arquivo `logo_vonny.png` não foi encontrado na raiz do repositório. Faça o upload dele na raiz do GitHub se desejar exibi-lo.")

with col2:
    st.markdown("### Ícone do Sistema")
    try:
        st.image("icone.png", width=150)
    except Exception:
        st.info("O arquivo `icone.png` não foi encontrado na raiz do repositório.")
