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
st.markdown("Utilize o **menu lateral esquerdo** para navegar entre a Central de Uploads e os Relatórios.")

st.markdown("<br>", unsafe_allow_html=True)

# Abordagem limpa baseada na navegação nativa do Streamlit
st.info("""
📂 **Como navegar no sistema:**
- Acesse o **menu lateral esquerdo** (barra lateral do Streamlit) para alternar livremente entre:
  * **Upload e Formatação**
  * **Relatório de Vendas**
  * **Relatório de Estoque**
  * **Imagens e Ativos**
""")
