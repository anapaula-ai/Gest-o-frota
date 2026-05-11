import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Estratégica de Frotas", layout="wide")

# 2. Estilização CSS (Looker Style Consolidado)
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD !important; }
    [data-testid="stAppViewContainer"] { background-color: #E3F2FD !important; }
    [data-testid="stSidebar"] { background-color: #BBDEFB !important; border-right: 1px solid #90CAF9; }
    h1, h2, h3, p, span, label { color: #1A237E !important; }

    .metric-container {
        background-color: #FFFFFF !important;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #CFD8DC;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 10px;
    }
    .metric-label { color: #546E7A !important; font-size: 10px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px;}
    .metric-value { color: #1A237E !important; font-size: 20px; font-weight: 800; line-height: 1.1; }
    .metric-subtext { color: #333333 !important; font-size: 11px; font-weight: 500; margin-top: 5px; }
    
    .chart-title { height: 45px; display: flex; align-items: center; font-size: 16px; font-weight: 700; color: #1A237E !important; margin-bottom: 10px; }
    .progress-bg { background-color: #EEEEEE !important; border-radius: 10px; width: 100%; height: 8px !important; margin-top: 8px; overflow: hidden; border: 1px solid #E0E0E0; }
    .progress-fill { background-color: #F57C00 !important; height: 8px !important; border-radius: 10px; }

    .stTabs [data-baseweb="tab"] { color: #1A237E !important; font-weight: 600; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #F57C00 !important; }
    </style>
    """, unsafe_allow_html=True)

# Funções de Formatação
def fmt_br(valor, is_moeda=False):
    if is_moeda:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{valor:,.0f}".replace(",", ".")

def draw_card(label, value, subtext="", progress=None):
    prog_html = f'<div class="progress-bg"><div class="progress-fill" style="width: {min(progress, 100)}%;"></div></div>' if progress is not None else ""
    st.markdown(f"""<div class="metric-container"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-subtext">{subtext}</div>{prog_html}</div>""", unsafe_allow_html=True)

# 3. Carregamento de Dados (ULTRA ROBUSTO)
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        df.columns = [str(c).strip() for c in df.columns]

        # Função para limpar números (converte 1.000,50 ou 1000,50 para 1000.50)
        def clean_num(x):
            if pd.isna(x): return 0.0
            if isinstance(x, (int, float)): return float(x)
            s = str(x).replace('R$', '').replace(' ', '')
            if ',' in s and '.' in s: s = s.replace('.', '').replace(',', '.')
            elif ',' in s: s = s.replace(',', '.')
            return pd.to_numeric(s, errors='coerce') or 0.0

        # Mapeamento dinâmico de colunas por nome aproximado
        for c in df.columns:
            c_low = c.lower()
            if 'combust' in c_low: df['Custo_Combustivel'] = df[c].apply(clean_num)
            if 'manut' in c_low and 'custo' in c_low: df['Custo_Manutencao'] = df[c].apply(clean_num)
            if 'placa' in c_low: df['PLACA'] = df[c]
            if 'base' in c_low: df['BASE'] = df[c]
            if 'refer' in c_low: df['DATA'] = pd.to_datetime(df[c])
            if 'inst' in c_low: df['INST'] = df[c]
            if 'quilom' in c_low: df['KM'] = df[c].apply(clean_num)

        # Garantir que as colunas existam mesmo se o Excel estiver com nomes diferentes
        for col in ['Custo_Combustivel', 'Custo_Manutencao', 'KM']:
            if col not in df.columns: df[col] = 0.0

        # Meses
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['Mes_Nome'] = df['DATA'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['DATA'].dt.month
        df['Ano'] = pd.to_numeric(df.get('Ano', 2026), errors='coerce').fillna(2026).astype(int)
            
        return df
    except Exception as e:
        st.error(f"Erro ao ler Excel: {e}")
        return pd.DataFrame()

df = load_data()

# ORÇAMENTOS
ORC_MANUTENCAO = {"AMES": 987380.00, "IAV": 305434.00}
ORC_COMBUSTIVEL = {"AMES": 1000081.06, "IAV": 264450.00}

if not df.empty:
    st.sidebar.markdown("### 🏢 GESTÃO DE FROTAS")
    if st.sidebar.button("🔄 Atualizar Dashboard"):
        st.cache_data.clear()
        st.rerun()

    ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano"].unique(), reverse=True))
    df_ano = df[df["Ano"] == ano_sel]
    inst_sel = st.sidebar.multiselect("Instituição", options=sorted(df_ano["INST"].unique()), default=sorted(df_ano["INST"].unique()))
    lista_meses = df_ano.sort_values("Mes_Num")["Mes_Nome"].unique()
    mes_sel = st.sidebar.selectbox("Mês Competência", options=lista_meses, index=len(lista_meses)-1)

    # Filtragem
    df_base = df_ano[df_ano["INST"].isin(inst_sel)]
    df_filtrado_mes = df_base[df_base["Mes_Nome"] == mes_sel]
    mes_num_atual = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
    df_acumulado_ate_mes = df_base[df_base["Mes_Num"] <= mes_num_atual]
    
    # Placas virtuais (ignoradas em rankings de veículo)
    is_virtual = df_filtrado_mes['PLACA'].str.contains('COMBUST', case=False, na=False)
    df_veiculos_mes = df_filtrado_mes[~is_virtual]

    # Dashboard
    tab1, tab2, tab3 = st.tabs(["📌 Visão Mensal", "📈 Resumo Acumulado", "📑 Detalhamento"])

    with tab1:
        st.markdown(f"### 📊 Desempenho Mensal - {mes_sel}")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        with c1: draw_card("Veículos Ativos", fmt_br(len(df_veiculos_mes["PLACA"].unique())))
        with c2: draw_card("Quilometragem Mensal", fmt_br(df_filtrado_mes['KM'].sum()))
        with c3: draw_card("Custo Manutenção (Mês)", fmt_br(df_filtrado_mes['Custo_Manutencao'].sum(), True))
        with c4: draw_card("Custo Combustível (Mês)", fmt_br(df_filtrado_mes['Custo_Combustivel'].sum(), True))
        
        with c5:
            orc_m = sum(ORC_MANUTENCAO.get(inst, 0) for inst in inst_sel)
            acum_m = df_acumulado_ate_mes['Custo_Manutencao'].sum()
            perc_m = (acum_m / orc_m * 100) if orc_m > 0 else 0
            draw_card("Exec. Manutenção (Ano)", fmt_br(acum_m, True), f"{perc_m:.1f}% consumido", progress=perc_m)
            
        with c6:
            orc_c = sum(ORC_COMBUSTIVEL.get(inst, 0) for inst in inst_sel)
            acum_c = df_acumulado_ate_mes['Custo_Combustivel'].sum()
            perc_c = (acum_c / orc_c * 100) if orc_c > 0 else 0
            draw_card("Exec. Combustível (Ano)", fmt_br(acum_c, True), f"{perc_c:.1f}% consumido", progress=perc_c)

        st.markdown("<br>", unsafe_allow_html=True)
        
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="chart-title">Ranking de Quilometragem (Veículos)</div>', unsafe_allow_html=True)
            top10_km = df_veiculos_mes.nlargest(10, 'KM').sort_values('KM', ascending=True)
            fig_km = px.bar(top10_km, x='KM', y='PLACA', orientation='h', text='KM', color_discrete_sequence=['#0288D1'])
            fig_km.update_traces(texttemplate='%{text:,.0f}', textposition='outside', cliponaxis=False)
            fig_km.update_layout(height=350, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=100), xaxis=dict(showticklabels=False, showgrid=False, range=[0, top10_km['KM'].max()*1.3 if not top10_km.empty else 1]), yaxis=dict(title=""))
            st.plotly_chart(fig_km, use_container_width=True)
        with g2:
            st.markdown('<div class="chart-title">Ranking de Custos Manutenção (Veículos)</div>', unsafe_allow_html=True)
            top10_m = df_veiculos_mes.nlargest(10, 'Custo_Manutencao').sort_values('Custo_Manutencao', ascending=True)
            fig_m = px.bar(top10_m, x='Custo_Manutencao', y='PLACA', orientation='h', text='Custo_Manutencao', color_discrete_sequence=['#F57C00'])
            fig_m.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside', cliponaxis=False)
            fig_m.update_layout(height=350, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=120), xaxis=dict(showticklabels=False, showgrid=False, range=[0, top10_m['Custo_Manutencao'].max()*1.4 if not top10_m.empty else 1]), yaxis=dict(title=""))
            st.plotly_chart(fig_m, use_container_width=True)

        st.markdown('<div class="chart-title">Ranking de Bases por Custo de Combustível (Mês)</div>', unsafe_allow_html=True)
        ranking_base_c = df_filtrado_mes.groupby('BASE')['Custo_Combustivel'].sum().reset_index().nlargest(10, 'Custo_Combustivel').sort_values('Custo_Combustivel', ascending=True)
        fig_b_c = px.bar(ranking_base_c, x='Custo_Combustivel', y='BASE', orientation='h', text='Custo_Combustivel', color_discrete_sequence=['#388E3C'])
        fig_b_c.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside', cliponaxis=False)
        fig_b_c.update_layout(height=450, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=150), xaxis=dict(showticklabels=False, showgrid=False, range=[0, ranking_base_c['Custo_Combustivel'].max()*1.3 if not ranking_base_c.empty else 1]), yaxis=dict(title=""))
        st.plotly_chart(fig_b_c, use_container_width=True)

    with tab2:
        st.title("📈 Resumo Acumulado Anual")
        evol_mes = df_acumulado_ate_mes.groupby(['Mes_Num', 'Mes_Nome']).agg({'Custo_Manutencao':'sum', 'Custo_Combustivel':'sum'}).reset_index().sort_values('Mes_Num')
        fig_e = px.line(evol_mes, x='Mes_Nome', y=['Custo_Manutencao', 'Custo_Combustível'], markers=True, color_discrete_map={'Custo_Manutencao': '#F57C00', 'Custo_Combustivel': '#388E3C'})
        fig_e.update_layout(height=400, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(title=""), yaxis=dict(title="R$"))
        st.plotly_chart(fig_e, use_container_width=True)

    with tab3:
        st.dataframe(df_filtrado_mes.drop(columns=['Mes_Num', 'Ano']), use_container_width=True)
