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
            background-color: #0a0a0a;
            border-radius: 4px 4px 0px 0px;
            color: #bbbbbb;
            padding: 8px 16px;
            border: 1px solid #1f1f1f;
            font-size: 14px;
        }
        .stTabs [aria-selected="true"] { border-top: 2px solid #00d4ff !important; color: #ffffff !important; font-weight: bold; }
        .metric-card {
            background-color: #0d0d0d;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #1f1f1f;
            text-align: center;
        }
        .metric-label { color: #888888; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }
        .metric-value { font-size: 26px; font-weight: 700; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. CARREGAMENTO DOS DADOS (Direto do Google Sheets)
@st.cache_data(ttl=600) # O sistema limpa o cache a cada 10 minutos para buscar novos dados
def carregar_dados():
    # Link que você me enviou, convertido para formato de dados (CSV)
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPclWfjRAP7bxzua2p02XeAubJ_7V2BJrn31MbMZWhZIzVjVLTDjpeYiJVtWmNSw/pub?output=csv"
    
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    
    # Tratamento de Datas
    df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
    traducao_meses = {'January':'Janeiro', 'February':'Fevereiro', 'March':'Março', 'April':'Abril', 'May':'Maio'}
    df['Mês Nome'] = df['Mês Referência'].dt.month_name().map(traducao_meses)
    
    # Tratamento de Custos (converte formato brasileiro 1.000,00 para número)
    if df['Custo de manutenção'].dtype == 'object':
        df['Custo de manutenção'] = df['Custo de manutenção'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
    
    return df

try:
    df = carregar_dados()
    col_inst, col_placa, col_custo, col_km, col_base = 'Instituição', 'Placa', 'Custo de manutenção', 'Quilometragem', 'Base'

    # --- SIDEBAR ---
    st.sidebar.markdown("### ⚙️ FILTROS")
    inst_lista = ['Todas'] + list(df[col_inst].unique())
    inst_selecionada = st.sidebar.selectbox("Instituição", inst_lista)
    
    ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio']
    meses_reais = [m for m in ordem_meses if m in df['Mês Nome'].unique()]
    mes_selecionado = st.sidebar.selectbox("Mês de Análise", meses_reais, index=len(meses_reais)-1)
    base_selecionada = st.sidebar.selectbox("Base (Filtro)", ['Todas'] + list(df[col_base].unique()))

    # FILTROS GLOBAIS
    df_f = df.copy()
    if inst_selecionada != 'Todas': df_f = df_f[df_f[col_inst] == inst_selecionada]
    if base_selecionada != 'Todas': df_f = df_f[df_f[col_base] == base_selecionada]

    st.title("Gestão de frotas")
    st.write(f"Conectado em tempo real com Google Sheets | Análise: **{inst_selecionada}**")

    # --- ABAS ---
    tab1, tab2 = st.tabs(["📊 CONTROLE MENSAL", "🏆 ACUMULADO ANUAL"])

    # --- ABA 1: MENSAL ---
    with tab1:
        df_m = df_f[df_f['Mês Nome'] == mes_selecionado]
        st.write("") 
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f'<div class="metric-card"><div class="metric-label">Veículos Ativos</div><div class="metric-value" style="color:#00d4ff">{df_m[col_placa].nunique()}</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card"><div class="metric-label">KM no Mês</div><div class="metric-value" style="color:#00d4ff">{df_m[col_km].sum():,.0f}</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card"><div class="metric-label">Custo no Mês</div><div class="metric-value" style="color:#ff4b4b">R$ {df_m[col_custo].sum():,.2f}</div></div>', unsafe_allow_html=True)

        st.write("")
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
            fig2 = px.bar(rc, x=col_custo, y=col_placa, orientation='h', text=rc[col_custo].apply(lambda x: f'R$ {x:,.0f}'), color=col_custo, color_continuous_scale='Reds', template='plotly_dark')
            fig2.update_traces(textposition='outside', cliponaxis=False, textfont=dict(size=12))
            fig2.update_layout(coloraxis_showscale=False, xaxis_visible=False, yaxis_title="", margin=dict(r=140, l=10, t=30, b=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

    # --- ABA 2: ACUMULADO ---
    with tab2:
        st.write("") 
        ca1, ca2, ca3 = st.columns(3)
        with ca1: st.markdown(f'<div class="metric-card"><div class="metric-label">Custo Total Acumulado</div><div class="metric-value" style="color:#ff4b4b">R$ {df_f[col_custo].sum():,.2f}</div></div>', unsafe_allow_html=True)
        with ca2: st.markdown(f'<div class="metric-card"><div class="metric-label">KM Total Acumulado</div><div class="metric-value" style="color:#00d4ff">{df_f[col_km].sum():,.0f} KM</div></div>', unsafe_allow_html=True)
        with ca3:
            media = df_f[col_custo].sum() / df_f[col_km].sum() if df_f[col_km].sum() > 0 else 0
            st.markdown(f'<div class="metric-card"><div class="metric-label">Custo Médio por KM</div><div class="metric-value" style="color:#ffffff">R$ {media:.2f}</div></div>', unsafe_allow_html=True)

        st.write("")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### Maiores Rodagens por Base (Top 10)")
            rbk = df_f.groupby(col_base)[col_km].sum().nlargest(10).sort_values(ascending=True).reset_index()
            fig3 = px.bar(rbk, x=col_km, y=col_base, orientation='h', text=rbk[col_km].apply(lambda x: f'{x:,.0f}'), color=col_km, color_continuous_scale='Blues', template='plotly_dark')
            fig3.update_traces(textposition='outside', cliponaxis=False, textfont=dict(size=12))
            fig3.update_layout(coloraxis_showscale=False, xaxis_visible=False, yaxis_title="", margin=dict(r=120, l=10, t=30, b=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig3, use_container_width=True)
        with col_b:
            st.markdown("#### Maiores Custos por Base (Top 10)")
            rbc = df_f.groupby(col_base)[col_custo].sum().nlargest(10).sort_values(ascending=True).reset_index()
            fig4 = px.bar(rbc, x=col_custo, y=col_base, orientation='h', text=rbc[col_custo].apply(lambda x: f'R$ {x:,.0f}'), color=col_custo, color_continuous_scale='Reds', template='plotly_dark')
            fig4.update_traces(textposition='outside', cliponaxis=False, textfont=dict(size=12))
            fig4.update_layout(coloraxis_showscale=False, xaxis_visible=False, yaxis_title="", margin=dict(r=140, l=10, t=30, b=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao conectar com Google Sheets: {e}")
    
