import streamlit as st

st.markdown("### Upload de Gestão Fixo")

# Função de exemplo para buscar o nome do arquivo atual no Supabase
# Substitua pela lógica real que você usa para consultar o Supabase
def obter_nome_arquivo_ativo(tipo):
    try:
        # Exemplo de consulta ao Supabase Storage ou tabela de metadados:
        # arquivos = supabase.storage.from_("seu-bucket").list()
        # return nome_do_arquivo_encontrado
        
        # EXEMPLO FICTÍCIO (Substitua pela sua chamada real ao Supabase):
        if tipo == "estoque":
            return "estoque_atualizado_2026.xlsx"
        else:
            return "vendas_geral_oficial.xlsx"
    except Exception as e:
        return "Arquivo ativo no Supabase"

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Planilha de Estoque")
    arquivo_estoque = st.file_uploader("Envie a planilha de estoque", type=["xlsx", "xlsm"], key="up_estoque")
    
    # Busca o nome do arquivo que o site está usando atualmente no Supabase
    nome_ativo_estoque = obter_nome_arquivo_ativo("estoque")
    
    if arquivo_estoque is not None:
        st.success(f"✅ **Novo arquivo pronto para envio:** {arquivo_estoque.name}")
    else:
        # Exibe exatamente o arquivo que está em uso pela aplicação
        st.info(f"📂 **Arquivo em uso no sistema (Supabase):** `{nome_ativo_estoque}`")

with col2:
    st.markdown("#### Planilha de Vendas")
    arquivo_vendas = st.file_uploader("Envie a planilha de vendas", type=["xlsx", "xlsm"], key="up_vendas")
    
    # Busca o nome do arquivo de vendas ativo no Supabase
    nome_ativo_vendas = obter_nome_arquivo_ativo("vendas")
    
    if arquivo_vendas is not None:
        st.success(f"✅ **Novo arquivo pronto para envio:** {arquivo_vendas.name}")
    else:
        # Exibe exatamente o arquivo que está em uso pela aplicação
        st.info(f"📂 **Arquivo em uso no sistema (Supabase):** `{nome_ativo_vendas}`")
