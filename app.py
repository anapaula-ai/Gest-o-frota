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
    
    # Limpeza de Números
    for col in ['Custo de manutenção', 'Quilometragem']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

try:
    df = carregar_dados()
    col_inst, col_placa, col_custo, col_km, col_base = 'Instituição', 'Placa', 'Custo de manutenção', 'Quilometragem', 'Base'

    # --- SIDEBAR ---
    st.sidebar.markdown("### ⚙️ FILTROS")
    inst_lista = ['Todas'] + sorted(list(df[col_inst].unique().astype(str)))
    inst_selecionada = st.sidebar.selectbox("Instituição", inst_lista)
    
    lista_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio']
    meses_reais = [m for m in lista_meses if m in df['Mês Nome'].unique()]
    mes_selecionado = st.sidebar.selectbox("Mês de Análise", meses_reais, index=len(meses_reais)-1 if meses_reais else 0)
    base_lista = ['Todas'] + sorted(list(df[col_base].unique().astype(str)))
    base_selecionada = st.sidebar.selectbox("Base (Filtro)", base_lista)

    # FILTROS GLOBAIS
    df_f = df.copy()
    if inst_selecionada != 'Todas': df_f = df_f[df_f[col_inst] == inst_selecionada]
    if base_selecionada != 'Todas': df_f = df_f[df_f[col_base] == base_selecionada]

    st.title("Gestão de frotas")
    st.write(f"Conectado ao Google Sheets | Análise: **{inst_selecionada}**")

    # --- ABAS ---
    tab1, tab2 = st.tabs(["📊 CONTROLE MENSAL", "🏆 ACUMULADO ANUAL"])

    # --- ABA 1: MENSAL ---
    with tab1:
        df_m = df_f[df_f['Mês Nome'] == mes_selecionado]
        st.write("") 
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Veículos Ativos</div><div class="metric-value" style="color:#00d4ff">{int(df_m[col_placa].nunique())}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">KM no Mês</div><div class="metric-value" style="color:#00d4ff">{float(df_m[col_km].sum()):,.0f}</div></div>', unsafe_allow_html=True)
        with m3:
            custo_m = float(df_m[col_custo].sum())
            st.markdown(f'<div class="metric-card"><div class="metric-label">Custo no Mês</div><div class="metric-value" style="color:#ff4b4b">R$ {custo_m:,.2f}</div></div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Maiores Rodagens (Top 10)")
            rk = df_m.groupby(col_placa)[col_km].sum().nlargest(10).sort_values(ascending=True).reset_index()
            fig1 = px.bar(rk, x=col_km, y=col_placa, orientation='h', text=col_km, color=col_km, color_continuous_scale='Blues', template='plotly_dark')
            fig1.update_traces(textposition='outside', cliponaxis=False, textfont=dict(size=12))
            fig1.update_layout(coloraxis_showscale=False, xaxis_visible=False, yaxis_title="", margin=dict(r=120, l=10, t=30, b=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            st.markdown("#### Maiores Custos (Top 10)")
            rc = df_m.groupby(col_placa)[col_custo].sum().nlargest(10).sort_values(ascending=True).reset_index()
            fig2 = px.bar(rc, x=col_custo, y=col_placa, orientation='h', text=rc[col_custo].apply(lambda x: f'R$ {float(x):,.0f}'), color=col_custo, color_continuous_scale='Reds', template='plotly_dark')
            fig2.update_traces(textposition='outside', cliponaxis=False, textfont=dict(size=12))
            fig2.update_layout(coloraxis_showscale=False, xaxis_visible=False, yaxis_title="", margin=dict(r=140, l=10, t=30, b=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

    # --- ABA 2: ACUMULADO ---
    with tab2:
        st.write("") 
        ca1, ca2, ca3 = st.columns(3)
        with ca1:
            custo_t = float(df_f[col_custo].sum())
            st.markdown(f'<div class="metri
