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
    </style>
""",
    unsafe_allow_html=True,
)

if AMBIENTE_STAGING:
    st.warning("⚠️ **ATENÇÃO: Você está acessando a versão de testes (Staging).**")

st.title("📊 Dashboard Executivo - Vonný")
st.markdown("Bem-vindo ao sistema de relatórios gerenciais integrados ao SAP e hospedados no Supabase.")
st.markdown("Utilize o menu lateral esquerdo para navegar entre os módulos do sistema:")

st.markdown("<br>", unsafe_allow_html=True)

# Definindo as páginas de forma oficial e segura para o Streamlit
paginas = {
    "Navegação": [
        st.Page("pages/1_Upload_e_Formatacao.py", title="Central de Uploads", icon="📤"),
        st.Page("pages/2_Relatorio_Vendas.py", title="Relatório de Vendas", icon="📈"),
        st.Page("pages/3_Relatorio_Estoque.py", title="Relatório de Estoque", icon="📦"),
        st.Page("pages/4_Imagens_e_Ativos.py", title="Imagens e Ativos", icon="🎨"),
    ]
}

pg = st.navigation(paginas)
pg.run()
