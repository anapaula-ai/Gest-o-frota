import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Estratégica de Frotas", layout="wide")

# 2. Estilização CSS (Sua versão favorita preservada)
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD !important; }
    [data-testid="stAppViewContainer"] { background-color: #E3F2FD !important; }
    [data-testid="stSidebar"] { background-color: #BBDEFB !important; border-right: 1px solid #90CAF9; }
    h1, h2, h3, p, span, label { color: #1A237E !important; }

    .metric-container {
        background-color: #FFFFFF !important;
        padding: 15px; border-radius: 12px; border: 1px solid #CFD8DC;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05); min-height: 140px;
        display: flex; flex-direction: column; justify-content: center; margin-bottom: 10px;
    }
    .metric-label { color: #546E7A !important; font-size: 10px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px;}
    .metric-value { color: #1A237E !important; font-size: 18px; font-weight: 800; line-height: 1.1; }
    .metric-subtext { color: #333333 !important; font-size: 11px; font-weight: 500; margin-top: 5px; }
    
    .chart-title { height: 50px; display: flex; align-items: center; font-size: 16px; font-weight: 700; color: #1A237E !important; text-align: left; margin-bottom: 5px; }
    .progress-bg { background-color: #EEEEEE !important; border-radius: 10px; width: 100%; height: 8px !important; margin-top: 8px; overflow: hidden; border: 1px solid #E0E0E0; }
    .progress-fill { background-color: #F57C00 !important; height: 8px !important; border-radius: 10px; }

    .stTabs [data-baseweb="tab"] { color: #1A237E !important; font-weight: 600; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #F57C00 !important; background-color: rgba(255,255,255,0.3) !important; }
    </style>
    """, unsafe_allow_html=True)

# Funções de Formatação
def fmt_br(valor, is_moeda=False):
    if is_moeda: return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{valor:,.0f}".replace(",", ".")

def draw_card(label, value, subtext="", progress=None):
    prog_html = f'<div class="progress-bg"><div class="progress-fill" style="width: {min(progress, 100)}%;"></div></div>' if progress is not None else ""
    st.markdown(f"""<div class="metric-container"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-subtext">{subtext}</div>{prog_html}</div>""", unsafe_allow_html=True)

# 3. Carregamento de Dados (Tratamento para evitar valores zerados)
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        df.columns = [str(c).strip() for c in df.columns]
        
        def clean_num(x):
            if pd.isna(x): return 0.0
            if isinstance(x, (int, float)): return float(x)
            s = str(x).replace('R$', '').replace(' ', '')
            if ',' in s and '.' in s: s = s.replace('.', '').replace(',', '.')
            elif ',' in s: s = s.replace(',', '.')
            return pd.to_numeric(s, errors='coerce') or 0.0

        # Mapeamento dinâmico
        for c in df.columns:
            c_low = c.lower()
            if 'combust' in c_low: df['C_Combustivel'] = df[c].apply(clean_num)
            if 'manut' in c_low and 'custo' in c_low: df['C_Manutencao'] = df[c].apply(clean_num)
            if 'quilom' in c_low: df['KM_Real'] = df[c].apply(clean_num)
            if 'placa' in c_low: df['PLACA_REF'] = df[c]
            if 'refer' in c_low: df['DATA_REF'] = pd.to_datetime(df[c])
            if 'inst' in c_low: df['INST_REF'] = df[c]
            if 'base' in c_low: df['BASE_REF'] = df[c]

        df['Ano_Ref'] = pd.to_numeric(df.get('Ano', 2026), errors='coerce').fillna(2026).astype(int)
        df['Mes_Nome'] = df['DATA_REF'].dt.month.map({1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'})
        df['Mes_Num'] = df['DATA_REF'].dt.month
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()

# ORÇAMENTOS
ORC_M = {"AMES": 987380.00, "IAV": 305434.00}
ORC_C = {"AMES": 1000081.06, "IAV": 264450.00}

if not df.empty:
    # 4. Sidebar
    st.sidebar.markdown("### 🏢 GESTÃO DE FROTAS")
    ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano_Ref"].unique(), reverse=True))
    df_ano = df[df["Ano_Ref"] == ano_sel]
    inst_sel = st.sidebar.multiselect("Instituição", options=sorted(df_ano["INST_REF"].unique()), default=sorted(df_ano["INST_REF"].unique()))
    mes_sel = st.sidebar.selectbox("Mês Competência", options=df_ano.sort_values("Mes_Num")["Mes_Nome"].unique(), index=0)

    # Filtros de Dados
    df_base = df_ano[df_ano["INST_REF"].isin(inst_sel)]
    df_mes = df_base[df_base["Mes_Nome"] == mes_sel]
    mes_num = df_mes["Mes_Num"].iloc[0] if not df_mes.empty else 1
    df_acum = df_base[df_base["Mes_Num"] <= mes_num]
    
    # Separar Veículos Reais
    df_veiculos = df_mes[~df_mes['PLACA_REF'].str.contains('COMBUST', case=False, na=False)]

    # 5. Dashboard
    tab1, tab2, tab3 = st.tabs(["📌 Visão Mensal", "📈 Resumo Acumulado", "📑 Detalhamento"])

    with tab1:
        st.markdown(f"### 📊 Desempenho Mensal - {mes_sel}")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: draw_card("Veículos Ativos", fmt_br(len(df_veiculos["PLACA_REF"].unique())))
        with c2: draw_card("Quilometragem", fmt_br(df_mes['KM_Real'].sum()))
        with c3: draw_card("Custo Manutenção", fmt_br(df_mes['C_Manutencao'].sum(), True))
        with c4: draw_card("Custo Combustível", fmt_br(df_mes['C_Combustivel'].sum(), True))
        with c5:
            orc_m = sum(ORC_M.get(i, 0) for i in inst_sel)
            acum_m = df_acum['C_Manutencao'].sum()
            perc_m = (acum_m / orc_m * 100) if orc_m > 0 else 0
            draw_card("Exec. Manutenção", fmt_br(acum_m, True), f"{perc_m:.1f}% consumido", progress=perc_m)
        with c6:
            orc_c = sum(ORC_C.get(i, 0) for i in inst_sel)
            acum_c = df_acum['C_Combustivel'].sum()
            perc_c = (acum_c / orc_c * 100) if orc_c > 0 else 0
            draw_card("Exec. Combustível", fmt_br(acum_c, True), f"{perc_c:.1f}% consumido", progress=perc_c)

        st.markdown("<br>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="chart-title">Ranking Quilometragem (Veículos)</div>', unsafe_allow_html=True)
            top_km = df_veiculos.nlargest(10, 'KM_Real').sort_values('KM_Real', ascending=True)
            fig_km = px.bar(top_km, x='KM_Real', y='PLACA_REF', orientation='h', text='KM_Real', color_discrete_sequence=['#0288D1'])
            fig_km.update_traces(texttemplate='%{text:,.0f}', textposition='outside', cliponaxis=False)
            fig_km.update_layout(height=400, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=80, r=100), xaxis=dict(showticklabels=False, showgrid=False, range=[0, top_km['KM_Real'].max()*1.3 if not top_km.empty else 1]), yaxis=dict(title=""))
            st.plotly_chart(fig_km, use_container_width=True)
        with g2:
            st.markdown('<div class="chart-title">Ranking Manutenção (Veículos)</div>', unsafe_allow_html=True)
            top_m = df_veiculos.nlargest(10, 'C_Manutencao').sort_values('C_Manutencao', ascending=True)
            fig_m = px.bar(top_m, x='C_Manutencao', y='PLACA_REF', orientation='h', text='C_Manutencao', color_discrete_sequence=['#F57C00'])
            fig_m.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside', cliponaxis=False)
            fig_m.update_layout(height=400, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=80, r=130), xaxis=dict(showticklabels=False, showgrid=False, range=[0, top_m['C_Manutencao'].max()*1.4 if not top_m.empty else 1]), yaxis=dict(title=""))
            st.plotly_chart(fig_m, use_container_width=True)

    with tab2:
        st.title("📈 Resumo Acumulado")
        st.markdown('<div class="chart-title">Evolução Mensal: Manutenção vs Combustível</div>', unsafe_allow_html=True)
        evol = df_acum.groupby(['Mes_Num', 'Mes_Nome']).agg({'C_Manutencao':'sum', 'C_Combustivel':'sum'}).reset_index().sort_values('Mes_Num')
        fig_e = px.line(evol, x='Mes_Nome', y=['C_Manutencao', 'C_Combustivel'], markers=True, color_discrete_map={'C_Manutencao': '#F57C00', 'C_Combustivel': '#388E3C'})
        fig_e.update_layout(height=400, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(title=""), yaxis=dict(title="R$"))
        st.plotly_chart(fig_e, use_container_width=True)

    with tab3:
        st.dataframe(df_mes.drop(columns=['Mes_Num', 'Ano_Ref']), use_container_width=True)
