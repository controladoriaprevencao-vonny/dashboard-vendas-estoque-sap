import streamlit as st

st.set_page_config(
    page_title="Imagens e Ativos - Vonný",
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

st.title("🎨 Gestão de Imagens e Ativos - Vonný")
st.markdown("Espaço reservado para visualização de logotipos e identidade visual da aplicação.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Logotipo Principal")
    try:
        st.image("logo_vonny.png", width=250)
    except Exception:
        st.info("O arquivo `logo_vonny.png` não foi encontrado na raiz do repositório.")

with col2:
    st.markdown("### Ícone do Sistema")
    try:
        st.image("icone.png", width=150)
    except Exception:
        st.info("O arquivo `icone.png` não foi encontrado na raiz do repositório.")
