# Verifique se esta parte do código no carregamento de dados está assim:
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        
        # Converte para numérico e remove valores vazios (NaN) para não dar erro nos cálculos
        df['Quilometragem'] = pd.to_numeric(df['Quilometragem'], errors='coerce').fillna(0)
        df['Custo de manutenção'] = pd.to_numeric(df['Custo de manutenção'], errors='coerce').fillna(0)
        
        # Garante que a coluna Ano seja tratada como número inteiro
        if 'Ano' in df.columns:
            df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int)
        else:
            df['Ano'] = 2026 # Fallback caso a coluna mude de nome
            
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()
