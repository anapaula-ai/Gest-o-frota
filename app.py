import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Gestão de frotas", layout="wide", initial_sidebar_state="expanded")

# 2. ESTILO DARK PREMIUM (CSS)
st.markdown("""
    <style>
        .stApp { background-color: #000000; color: #ffffff; }
        [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #1f1f1f; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #0a0a0a; border-radius: 4px 4px 0px 0px;
            color: #bbbbbb; padding: 8px 16px; border: 1px solid #1f1f1f; font-size: 14px;
        }
        .stTabs [aria-selected="true"] { border-top: 2px solid #00d4ff !important; color: #ffffff !important; font-weight: bold; }
        .metric-card {
            background-color: #0d0d0d; padding: 20px; border-radius: 12px;
            border: 1px solid #1f1f1f; text-align: center;
        }
        .metric-label { color: #888888; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }
        .metric-value { font-size: 26px; font-weight: 700; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. CARREGAMENTO E LIMPEZA DOS DADOS
@st.cache_data(ttl=60)
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPclWfjRAP7bxzua2p02XeAubJ_7V2BJrn31MbMZWhZIzVjVLTDjpeYiJVtWmNSw/pub?output=csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    
    # Tratamento de Datas
    df['Mês Referência'] = pd.to_datetime(df['Mês Referência'], errors='coerce')
    traducao_meses = {'January':'Janeiro', 'February':'Fevereiro', 'March':'Março', 'April':'Abril', 'May':'Maio'}
    df['Mês Nome'] = df['Mês Referência'].dt.month_name().map(traducao_meses)
    
    # --- LIMPEZA DE NÚMEROS (O Corretor do Erro) ---
    for col in ['Custo de manutenção', 'Quilometragem']:
        if col in df.columns:
            # Transforma em string, tira R$, tira pontos de milhar, troca vírgula por ponto
            df[col] = df[col].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip()
            # Converte para número real. Se der erro em alguma linha, vira 0.
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

try:
    df = carregar_dados()
    col_inst, col_placa, col_custo, col_km, col_base = 'Instituição', 'Placa', 'Custo de manutenção', 'Quilometragem', 'Base'

    # --- SIDEBAR ---
    st.sidebar.markdown("### ⚙️ FILTROS")
    inst_lista = ['Todas'] + sorted(list(df[col_inst].unique()))
    inst_selecionada = st.sidebar.selectbox("Instituição", inst_lista)
    
    lista_meses = ['Janeiro
    
