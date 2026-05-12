import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Estratégica de Frotas", layout="wide")

# 2. Estilização CSS (Mantida fiel ao original)
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD !important; }
    [data-testid="stAppViewContainer"] { background-color: #E3F2FD !important; }
    [data-testid="stSidebar"] { background-color: #BBDEFB !important; border-right: 1px solid #90CAF9; }
    h1, h2, h3, p, span, label { color: #1A237E !important; }

    .metric-container {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #CFD8DC;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        margin-bottom: 10px;
    }
    
    .metric-label { 
        color: #546E7A !important; 
        font-size: 11px; 
        font-weight: 700; 
        text-transform: uppercase; 
        height: 35px;
        display: flex;
        align-items: center;
    }
    .metric-value { 
        color: #1A237E !important; 
        font-size: 24px; 
        font-weight: 800; 
        height: 40px;
        display: flex;
        align-items: center;
    }
    .metric-subtext { 
        color: #333333 !important; 
        font-size: 13px; 
        font-weight: 500; 
        height: 25px;
        display: flex;
        align-items: center;
    }
    
    .trend-container {
        height: 25px;
        display: flex;
        align-items: center;
        margin-top: 5px;
    }

    .chart-title {
        height: 50px; 
        display: flex; 
        align-items: center; 
        font-size: 16px; 
        font-weight: 700; 
        color: #1A237E !important; 
        text-align: left;
        margin-bottom: 5px;
    }

    .stTabs [data-baseweb="tab"] { color: #1A237E !important; font-weight: 600; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #F57C00 !important; background-color: rgba(255,255,255,0.3) !important; }

    .trend-up { color: #D32F2F !important; font-size: 13px; font-weight: bold; }
    .trend-down { color: #388E3C !important; font-size: 13px; font-weight: bold; }
    .progress-bg { background-color: #E0E0E0; border-radius: 10px; width: 100%; height: 8px; margin-top: 10px; }
    .progress-fill { background-color: #F57C00; height: 8px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

ESTILO_TEXTO = dict(size=13, color='#333333', family="Arial, sans-serif")

# Funções de Apoio
def fmt_br(valor, is_moeda=False):
    if is_moeda:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{valor:,.0f}".replace(",", ".")

def draw_card(label, value, subtext="", trend=None, is_lower_better=True, progress=None):
    trend_html = ""
    if trend is not None and trend != 0:
        color = "trend-down" if (trend <= 0 if is_lower_better else trend >= 0) else "trend-up"
        icon = "↓" if trend <= 0 else "↑"
        trend_html = f'<div class="{color}">{icon} {abs(trend):.1f}% vs mês ant.</div>'
    
    prog_html = f'<div class="progress-bg"><div class="progress-fill" style="width: {min(progress, 100)}%;"></div></div>' if progress is not None else ""
    
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtext">{subtext}</div>
            <div class="trend-container">{trend_html}</div>
            {prog_html}
        </div>
    """, unsafe_allow_html=True)

# 3. Carregamento de Dados
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 
                    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
        df['Quilometragem'] = pd.to_numeric(df['Quilometragem'], errors='coerce').fillna(0)
        df['Custo de manutenção'] = pd.to_numeric(df['Custo de manutenção'], errors='coerce').fillna(0)
        df['Custo Combustível'] = pd.to_numeric(df.iloc[:, 3], errors='coerce').fillna(0)
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int) if 'Ano' in df.columns else 2026
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()

ORCAMENTOS_MANUT = {"AMES": 987380.00, "IAV": 305434.00}
ORCAMENTOS_COMB = {"AMES": 1000081.06, "IAV": 264450.00}

if not df.empty:
    # 4. Sidebar
    st.sidebar.markdown("### 🏢 GESTÃO DE FROTAS")
    ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano"].unique(), reverse=True))
    df_ano = df[df["Ano"] == ano_sel]
    
    inst_sel = st.sidebar.multiselect("Instituição", options=sorted(df_ano["Instituição"].unique()), default=sorted(df_ano["Instituição"].unique()))
    busca_placa = st.sidebar.text_input("🔍 Buscar Placa específica", "").upper()
    
    lista_meses = df_ano.sort_values("Mes_Num")["Mes_Nome"].unique()
    mes_sel = st.sidebar.selectbox("Mês Competência", options=lista_meses, index=len(lista_meses)-1)

    # Filtros Refinados (Combustível, Seguro e Manutenção)
    df_base = df_ano[df_ano["Instituição"].isin(inst_sel)]
    
    # Identificação por palavras-chave (considerando acentos e case-insensitive)
    df_apenas_comb = df_base[df_base["Placa"].str.contains("COMBUSTI", case=False, na=False)]
    df_apenas_seguro = df_base[df_base["Placa"].str.contains("SEGURO", case=False, na=False)]
    
    # Manutenção é tudo que NÃO é combustível e NÃO é seguro
    df_apenas_manut = df_base[
        (~df_base["Placa"].str.contains("COMBUSTI", case=False, na=False)) & 
        (~df_base["Placa"].str.contains("SEGURO", case=False, na=False))
    ]

    # Dados para Visão Mensal (Manutenção)
    df_filtrado_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Nome"] == mes_sel]
    mes_num_atual = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
    df_acumulado_ate_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] <= mes_num_atual]
    df_anterior_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] == mes_num_atual - 1]

    # 5. Dashboard
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📌 Visão Mensal", "📈 Resumo Acumulado", "⛽ Combustível", "🛡️ Seguros", "📑 Detalhamento"])

    with tab1:
        st.markdown(f"### 📊 Desempenho Mensal Manutenção - {mes_sel}")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            ativos_m = len(df_filtrado_mes_manut["Placa"].unique())
            ativos_a = len(df_anterior_manut["Placa"].unique())
            trend_at = ((ativos_m - ativos_a) / ativos_a * 100) if ativos_a > 0 else 0
            draw_card("VEÍCULOS ATIVOS", fmt_br(ativos_m), trend=trend_at, is_lower_better=False)
        with c2:
            km_m = df_filtrado_mes_manut['Quilometragem'].sum()
            km_a = df_anterior_manut['Quilometragem'].sum()
            draw_card("QUILOMETRAGEM MENSAL", fmt_br(km_m), trend=((km_m-km_a)/km_a*100) if km_a>0 else 0, is_lower_better=False)
        with c3:
            custo_m = df_filtrado_mes_manut['Custo de manutenção'].sum()
            custo_a = df_anterior_manut['Custo de manutenção'].sum()
            num_veiculos = len(df_filtrado_mes_manut["Placa"].unique())
            custo_medio = custo_m / num_veiculos if num_veiculos > 0 else 0
            trend_c = ((custo_m - custo_a) / custo_a * 100) if custo_a > 0 else 0
            draw_card("CUSTO MANUTENÇÃO MENSAL", fmt_br(custo_m, True), f"Média: {fmt_br(custo_medio, True)} /veículo", trend=trend_c)
        with c4:
            orc_total_manut = sum(ORCAMENTOS_MANUT.get(inst, 0) for inst in inst_sel)
            gasto_total_acum_manut = df_acumulado_ate_mes_manut["Custo de manutenção"].sum()
            perc_manut = (gasto_total_acum_manut / orc_total_manut * 100) if orc_total_manut > 0 else 0
            draw_card("ORÇAMENTO MANUTENÇÃO", fmt_br(gasto_total_acum_manut, True), f"{perc_manut:.1f}% consumido", progress=perc_manut)

    with tab2:
        st.markdown(f"### 📈 Resumo Acumulado Manutenção - {ano_sel}")
        evol_inst = df_acumulado_ate_mes_manut.groupby(['Mes_Num', 'Mes_Nome', 'Instituição'])['Custo de manutenção'].sum().reset_index().sort_values('Mes_Num')
        fig_evol = px.line(evol_inst, x='Mes_Nome', y='Custo de manutenção', color='Instituição', markers=True, color_discrete_map={"AMES": "#0288D1", "IAV": "#F57C00"})
        st.plotly_chart(fig_evol, use_container_width=True)

    with tab3:
        st.markdown(f"### ⛽ Gestão de Combustível - {ano_sel}")
        df_comb_mes = df_apenas_comb[df_apenas_comb["Mes_Nome"] == mes_sel]
        df_comb_acum = df_apenas_comb[df_apenas_comb["Mes_Num"] <= mes_num_atual]
        df_comb_anterior = df_apenas_comb[df_apenas_comb["Mes_Num"] == mes_num_atual - 1]

        k1, k2 = st.columns([1, 2])
        with k1:
            orc_total_comb = sum(ORCAMENTOS_COMB.get(inst, 0) for inst in inst_sel)
            gasto_m_comb = df_comb_mes["Custo Combustível"].sum()
            gasto_a_comb = df_comb_anterior["Custo Combustível"].sum()
            trend_comb = ((gasto_m_comb - gasto_a_comb) / gasto_a_comb * 100) if gasto_a_comb > 0 else 0
            draw_card("GASTO COMBUSTÍVEL MENSAL", fmt_br(gasto_m_comb, True), f"Referente a {mes_sel}", trend=trend_comb)
        
        st.markdown("---")
        custo_comb_base = df_comb_mes.groupby('Base')['Custo Combustível'].sum().reset_index().sort_values('Custo Combustível', ascending=True)
        if not custo_comb_base.empty:
            fig_comb = px.bar(custo_comb_base, x='Custo Combustível', y='Base', orientation='h', text='Custo Combustível', color_discrete_sequence=['#0288D1'])
            fig_comb.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside')
            st.plotly_chart(fig_comb, use_container_width=True)

    with tab4:
        st.markdown(f"### 🛡️ Gestão de Seguros - {mes_sel}")
        # Filtro de seguros para o mês selecionado
        df_seguro_mes = df_apenas_seguro[df_apenas_seguro["Mes_Nome"] == mes_sel]
        df_seguro_anterior = df_apenas_seguro[df_apenas_seguro["Mes_Num"] == mes_num_atual - 1]
        
        s1, s2 = st.columns([1, 2])
        with s1:
            custo_seg_m = df_seguro_mes['Custo de manutenção'].sum()
            custo_seg_a = df_seguro_anterior['Custo de manutenção'].sum()
            trend_seg = ((custo_seg_m - custo_seg_a) / custo_seg_a * 100) if custo_seg_a > 0 else 0
            draw_card("TOTAL EM SEGUROS", fmt_br(custo_seg_m, True), f"Competência: {mes_sel}", trend=trend_seg)

        st.markdown("---")
        st.markdown(f'<div class="chart-title">Distribuição de Custos de Seguro por Base - {mes_sel}</div>', unsafe_allow_html=True)
        
        # Agrupamento por Base
        custo_seg_base = df_seguro_mes.groupby('Base')['Custo de manutenção'].sum().reset_index().sort_values('Custo de manutenção', ascending=True)
        
        if not custo_seg_base.empty:
            fig_seg = px.bar(custo_seg_base, x='Custo de manutenção', y='Base', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#607D8B'])
            fig_seg.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO, cliponaxis=False)
            max_s = custo_seg_base['Custo de manutenção'].max()
            fig_seg.update_layout(height=max(400, len(custo_seg_base) * 40), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                 xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_s * 1.4]),
                                 yaxis=dict(tickfont=dict(size=12, color='#333333', family="Arial Black")))
            st.plotly_chart(fig_seg, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Sem dados de seguros lançados para este mês.")

    with tab5:
        st.markdown("### 📑 Detalhamento dos Dados")
        st.dataframe(df_base.drop(columns=['Mes_Num', 'Ano']), use_container_width=True)
else:
    st.warning("Verifique o arquivo manutencao.xlsx")
