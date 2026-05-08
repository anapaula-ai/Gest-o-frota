import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO BÁSICA
st.set_page_config(page_title="Gestão de frotas", layout="wide")

# 2. ESTILO SIMPLIFICADO (Para evitar erros de colagem)
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #050505; }
    .metric-box {
        background-color: #0a0a0a; padding: 20px; border-radius: 10px;
        border: 1px solid #1f1f1f; text-align: center; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 3. FUNÇÃO DE DADOS
@st.cache_data(ttl=60)
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPclWfjRAP7bxzua2p02XeAubJ_7V2BJrn31MbMZWhZIzVjVLTDjpeYiJVtWmNSw/pub?output=csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df['Mês Referência'] = pd.to_datetime(df['Mês Referência'], errors='coerce')
    meses_map = {'January':'Janeiro', 'February':'Fevereiro', 'March':'Março', 'April':'Abril', 'May':'Maio'}
    df['Mês Nome'] = df['Mês Referência'].dt.month_name().map(meses_map)
    for col in ['Custo de manutenção', 'Quilometragem']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

# 4. EXECUÇÃO DO DASHBOARD
try:
    df = carregar_dados()
    
    # Filtros na Lateral
    st.sidebar.title("Filtros")
    inst = st.sidebar.selectbox("Instituição", ['Todas'] + sorted(list(df['Instituição'].unique().astype(str))))
    mes = st.sidebar.selectbox("Mês", ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio'], index=3)
    base = st.sidebar.selectbox("Base", ['Todas'] + sorted(list(df['Base'].unique().astype(str))))

    # Aplicar Filtros
    df_f = df.copy()
    if inst != 'Todas': df_f = df_f[df_f['Instituição'] == inst]
    if base != 'Todas': df_f = df_f[df_f['Base'] == base]

    st.title("📊 Gestão de frotas")
    tab1, tab2 = st.tabs(["Mensal", "Acumulado"])

    with tab1:
        df_m = df_f[df_f['Mês Nome'] == mes]
        col1, col2, col3 = st.columns(3)
        col1.metric("Veículos", int(df_m['Placa'].nunique()))
        col2.metric("KM Total", f"{df_m['Quilometragem'].sum():,.0f}")
        col3.metric("Custo Total", f"R$ {df_m['Custo de manutenção'].sum():,.2f}")
        
        c1, c2 = st.columns(2)
        with c1:
            rk = df_m.groupby('Placa')['Quilometragem'].sum().nlargest(10).reset_index()
            fig1 = px.bar(rk, x='Quilometragem', y='Placa', orientation='h', title="Top 10 KM", template='plotly_dark')
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            rc = df_m.groupby('Placa')['Custo de manutenção'].sum().nlargest(10).reset_index()
            fig2 = px.bar(rc, x='Custo de manutenção', y='Placa', orientation='h', title="Top 10 Custos", template='plotly_dark')
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.header("Resumo Geral Acumulado")
        a1, a2 = st.columns(2)
        a1.metric("CUSTO ACUMULADO", f"R$ {df_f['Custo de manutenção'].sum():,.2f}")
        a2.metric("KM ACUMULADO", f"{df_f['Quilometragem'].sum():,.0f} KM")
        
        ba1, ba2 = st.columns(2)
        with ba1:
            rbc = df_f.groupby('Base')['Custo de manutenção'].sum().nlargest(10).reset_index()
            st.plotly_chart(px.bar(rbc, x='Custo de manutenção', y='Base', orientation='h', title="Custo por Base", template='plotly_dark'), use_container_width=True)
        with ba2:
            rbk = df_f.groupby('Base')['Quilometragem'].sum().nlargest(10).reset_index()
            st.plotly_chart(px.bar(rbk, x='Quilometragem', y='Base', orientation='h', title="KM por Base", template='plotly_dark'), use_container_width=True)

except Exception as e:
    st.error(f"Erro: {e}")
