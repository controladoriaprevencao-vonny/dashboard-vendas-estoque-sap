import streamlit as st

AMBIENTE_STAGING = True

st.set_page_config(
    page_title="Dashboard Executivo - Vonný" + (" [STAGING]" if AMBIENTE_STAGING else ""),
    page_icon="icone.png",
    layout="wide",
)

st.markdown(
    """
    <style>
    header[data-testid="stHeader"] { background-color: #E6007E !important; }
    section[data-testid="stSidebar"] { border-right: 1px solid #F5CCD8; }
    h1, h2, h3 { color: #C5006B !important; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; }
    .stButton>button {
        width: 100%; background-color: #555555 !important; color: #FFFFFF !important;
        font-weight: bold !important; border-radius: 6px; height: 48px; border: none; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #333333 !important; color: #FFFFFF !important; }
    </style>
""",
    unsafe_allow_html=True,
)

if AMBIENTE_STAGING:
    st.warning("⚠️ **ATENÇÃO: Você está acessando a versão de testes (Staging).**")

st.title("📊 Dashboard Executivo - Vonný")
st.markdown("Bem-vindo ao sistema de relatórios gerenciais integrados ao SAP e hospedados no Supabase.")
st.markdown("Utilize o **menu lateral esquerdo** para navegar entre a Central de Uploads e os Relatórios.")

st.markdown("<br>", unsafe_allow_html=True)
st.info("💡 **Dica de Navegação:** O menu de páginas na barra lateral esquerda está pronto e estruturado para alternar entre as telas de forma rápida e sem erros.")
