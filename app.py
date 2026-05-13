import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Estratégica de Frotas", layout="wide")

# 2. Estilização CSS (A SUA ORIGINAL)
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD !important; }
    [data-testid="stAppViewContainer"] { background-color: #E3F2FD !important; }
    [data-testid="stSidebar"] { background-color: #BBDEFB !important; border-right: 1px solid #90CAF9; }
    h1, h2, h3, p, span, label { color: #1A237E !important; }
    .metric-container { background-color: #FFFFFF !important; padding: 20px; border-radius: 12px; border: 1px solid #CFD8DC; box-shadow: 0px 2px 8px rgba(0,0,0,0.05); height: 200px; display: flex; flex-direction: column; justify-content: flex-start; margin-bottom: 10px; }
    .metric-label { color: #546E7A !important; font-size: 11px; font-weight: 700; text-transform: uppercase; height: 35px; display: flex; align-items: center; }
    .metric-value { color: #1A237E !important; font-size: 24px; font-weight: 800; height: 40px; display: flex; align-items: center; }
    .metric-subtext { color: #333333 !important; font-size: 13px; font-weight: 500; height: 25px; display: flex; align-items: center; }
    .trend-container { height: 25px; display: flex; align-items: center; margin-top: 5px; }
    .chart-title { height: 50px; display: flex; align-items: center; font-size: 16px; font-weight: 700; color: #1A237E !important; text-align: left; margin-bottom: 5px; }
    .stTabs [data-baseweb="tab"] { color: #1A237E !important; font-weight: 600; }
    .stTabs[aria-selected="true"] { border-bottom: 3px solid #F57C00 !important; background-color: rgba(255,255,255,0.3) !important; }
    .trend-up { color: #D32F2F !important; font-size: 13px; font-weight: bold; }
    .trend-down { color: #388E3C !important; font-size: 13px; font-weight: bold; }
    .progress-bg { background-color: #E0E0E0; border-radius: 10px; width: 100%; height: 8px; margin-top: 10px; }
    .progress-fill { background-color: #F57C00; height: 8px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

ESTILO_TEXTO = dict(size=13, color='#333333', family="Arial, sans-serif")

def fmt_br(valor, is_moeda=False):
    if is_moeda: return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{valor:,.0f}".replace(",", ".")

def get_ativos(df):
    return df[(df["Placa"].str.len() == 7) & (~df["Placa"].str.contains("COMBUSTÍVEL|SEGURO|FINANC|CONSÓRCIO", case=False, na=True))]["Placa"].unique()

def draw_card(label, value, subtext="", trend=None, is_lower_better=True, progress=None):
    trend_html = ""
    if trend is not None and trend != 0:
        color = "trend-down" if (trend <= 0 if is_lower_better else trend >= 0) else "trend-up"
        icon = "↓" if trend <= 0 else "↑"
        trend_html = f'<div class="{color}">{icon} {abs(trend):.1f}% vs mês ant.</div>'
    prog_html = f'<div class="progress-bg"><div class="progress-fill" style="width: {min(progress, 100)}%;"></div></div>' if progress is not None else ""
    st.markdown(f'<div class="metric-container"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-subtext">{subtext}</div><div class="trend-container">{trend_html}</div>{prog_html}</div>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
        df['Quilometragem'] = pd.to_numeric(df['Quilometragem'], errors='coerce').fillna(0)
        df['Custo de manutenção'] = pd.to_numeric(df['Custo de manutenção'], errors='coerce').fillna(0)
        df['Custo de seguro'] = pd.to_numeric(df['Custo de seguro'], errors='coerce').fillna(0)
        df['Custo de Rastreador'] = pd.to_numeric(df['Custo de Rastreador'], errors='coerce').fillna(0)
        df['Custo Combustível'] = pd.to_numeric(df.iloc[:, 3], errors='coerce').fillna(0)
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int)
        if 'Placa' in df.columns: df['Placa'] = df['Placa'].astype(str).str.strip().str.upper()
        return df
    except: return pd.DataFrame()

df = load_data()
ORCAMENTOS_MANUT = {"AMES": 987380.00, "IAV": 305434.00}
ORCAMENTOS_COMB = {"AMES": 1000081.06, "IAV": 264450.00}
ORCAMENTOS_SEGURO = {"AMES": 186682.00, "IAV": 115461.00}
ORCAMENTOS_RAST = {"AMES": 0, "IAV": 10194.00}

if not df.empty:
    ano_sel = st.sidebar.selectbox("Ano", sorted(df["Ano"].unique(), reverse=True))
    inst_sel = st.sidebar.selectbox("Instituição", ["TODAS"] + sorted(df["Instituição"].unique()))
    inst_ativas = df["Instituição"].unique() if inst_sel == "TODAS" else [inst_sel]
    df_base = df[(df["Ano"] == ano_sel) & (df["Instituição"].isin(inst_ativas))]
    mes_sel = st.sidebar.selectbox("Mês Competência", df_base.sort_values("Mes_Num")["Mes_Nome"].unique())
    mes_num_atual = df_base[df_base["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
    
    # Adicionando aba nova
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📌 Visão Mensal", "📈 Resumo Acumulado", "⛽ Combustível", "🛡️ Custos Fixos", "📑 Detalhamento"])

    with tab1:
        st.markdown(f"### 📊 Desempenho Mensal Manutenção - {mes_sel}")
        c1, c2, c3, c4 = st.columns(4)
        df_filtrado_mes_manut = df_base[(df_base["Mes_Nome"] == mes_sel) & (~df_base["Placa"].str.startswith("COMBUSTÍVEL"))]
        with c1: draw_card("VEÍCULOS ATIVOS", len(get_ativos(df_filtrado_mes_manut)))
        with c2: draw_card("KM MENSAL", fmt_br(df_filtrado_mes_manut['Quilometragem'].sum()))
        with c3: draw_card("CUSTO MANUT.", fmt_br(df_filtrado_mes_manut['Custo de manutenção'].sum(), True))
        with c4: draw_card("ORÇAMENTO", fmt_br(df_base[df_base["Mes_Num"]<=mes_num_atual]['Custo de manutenção'].sum(), True))
        
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="chart-title">Ranking de Quilometragem (Top 10)</div>', unsafe_allow_html=True)
            top10_km = df_filtrado_mes_manut.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig_km = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
            fig_km.update_traces(texttemplate='<b>%{text:,.0f}</b>', textposition='outside', textfont=ESTILO_TEXTO)
            st.plotly_chart(fig_km, use_container_width=True)
        with g2:
            st.markdown('<div class="chart-title">Ranking de Manutenção (Top 10)</div>', unsafe_allow_html=True)
            top10_custo = df_filtrado_mes_manut.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#F57C00'])
            fig_custo.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO)
            st.plotly_chart(fig_custo, use_container_width=True)

    with tab2:
        st.markdown(f"### 📈 Resumo Acumulado Manutenção")
        df_acum = df_base[df_base["Mes_Num"] <= mes_num_atual].groupby(['Mes_Nome', 'Mes_Num', 'Instituição'])['Custo de manutenção'].sum().reset_index().sort_values('Mes_Num')
        st.plotly_chart(px.line(df_acum, x='Mes_Nome', y='Custo de manutenção', color='Instituição', markers=True), use_container_width=True)

    with tab3:
        st.markdown(f"### ⛽ Gestão de Combustível")
        df_comb = df_base[df_base["Mes_Num"] <= mes_num_atual]
        st.plotly_chart(px.bar(df_comb.groupby('Base')['Custo Combustível'].sum().reset_index(), x='Custo Combustível', y='Base', orientation='h'), use_container_width=True)

    with tab4:
        st.markdown("### 🛡️ Gestão de Custos Fixos")
        df_fixos = df_base[df_base["Mes_Num"] <= mes_num_atual]
        c1, c2 = st.columns(2)
        with c1: draw_card("CUSTO SEGURO", fmt_br(df_fixos['Custo de seguro'].sum(), True))
        with c2: draw_card("CUSTO RASTREADOR", fmt_br(df_fixos['Custo de Rastreador'].sum(), True))
        st.plotly_chart(px.line(df_fixos.groupby('Mes_Nome')[['Custo de seguro', 'Custo de Rastreador']].sum().reset_index(), x='Mes_Nome', y=['Custo de seguro', 'Custo de Rastreador'], markers=True), use_container_width=True)

    with tab5:
        st.dataframe(df_base, use_container_width=True)
