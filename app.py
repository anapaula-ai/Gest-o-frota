import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Estratégica de Frotas", layout="wide")

# 2. Estilização CSS
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
    
    .metric-label { color: #546E7A !important; font-size: 11px; font-weight: 700; text-transform: uppercase; height: 35px; display: flex; align-items: center; }
    .metric-value { color: #1A237E !important; font-size: 24px; font-weight: 800; height: 40px; display: flex; align-items: center; }
    .metric-subtext { color: #333333 !important; font-size: 13px; font-weight: 500; height: 25px; display: flex; align-items: center; }
    
    .trend-container { height: 25px; display: flex; align-items: center; margin-top: 5px; }
    .chart-title { height: 50px; display: flex; align-items: center; font-size: 16px; font-weight: 700; color: #1A237E !important; text-align: left; margin-bottom: 5px; }

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

def get_ativos(df):
    # Considera apenas placas com 7 caracteres e ignora termos virtuais
    return df[
        (df["Placa"].str.len() == 7) & 
        (~df["Placa"].str.contains("COMBUSTÍVEL|SEGURO|FINANC|CONSÓRCIO|RASTREADOR", case=False, na=True))
    ]["Placa"].unique()

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

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        # LIMPEZA DE COLUNAS: Remove espaços extras nos nomes das colunas (ex: "Custo de seguro ")
        df.columns = df.columns.str.strip()

        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 
                    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
        
        # Conversão segura de colunas numéricas (usa 0 se a coluna não existir ou estiver com erro)
        cols_para_converter = {
            'Quilometragem': 'Quilometragem',
            'Custo de manutenção': 'Custo de manutenção',
            'Custo de combustível': 'Custo de combustível',
            'Custo de seguro': 'Custo de seguro'
        }
        
        for col_excel, col_nova in cols_para_converter.items():
            if col_excel in df.columns:
                df[col_nova] = pd.to_numeric(df[col_excel], errors='coerce').fillna(0)
            else:
                df[col_nova] = 0.0

        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int) if 'Ano' in df.columns else 2026
        
        # Limpeza de strings
        for col in ['Centro de Custo', 'Base', 'Instituição']:
            if col in df.columns: df[col] = df[col].astype(str).str.strip()
            
        if 'Placa' in df.columns: 
            df['Placa'] = df['Placa'].astype(str).str.strip().str.upper().replace('NAN', '')
        
        return df
    except Exception as e:
        st.error(f"Erro crítico ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()

# Definição de Orçamentos
ORCAMENTOS_MANUT = {"AMES": 987380.00, "IAV": 305434.00}
ORCAMENTOS_COMB = {"AMES": 1000081.06, "IAV": 264450.00}
ORCAMENTOS_SEGURO = {"AMES": 186682.00, "IAV": 15382.00}

if not df.empty:
    # 4. Sidebar
    st.sidebar.markdown("### 🏢 GESTÃO DE FROTAS")
    ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano"].unique(), reverse=True))
    df_ano = df[df["Ano"] == ano_sel]
    
    opcoes_inst = ["TODAS"] + sorted(df_ano["Instituição"].unique())
    inst_sel = st.sidebar.selectbox("Instituição", options=opcoes_inst)
    
    if inst_sel == "TODAS":
        df_temp_inst = df_ano.copy()
        inst_ativas = df_ano["Instituição"].unique()
    else:
        df_temp_inst = df_ano[df_ano["Instituição"] == inst_sel]
        inst_ativas = [inst_sel]
    
    col_cc = 'Centro de Custo' if 'Centro de Custo' in df.columns else 'Base'
    opcoes_cc = ["TODOS"] + sorted(df_temp_inst[col_cc].dropna().unique())
    cc_sel = st.sidebar.selectbox("Centro de Custo / Base", options=opcoes_cc)
    
    df_base = df_temp_inst.copy() if cc_sel == "TODOS" else df_temp_inst[df_temp_inst[col_cc] == cc_sel]
    busca_placa = st.sidebar.text_input("🔍 Buscar Placa específica", "").upper().strip()
    
    lista_meses = df_ano.sort_values("Mes_Num")["Mes_Nome"].unique()
    mes_sel = st.sidebar.selectbox("Mês Competência", options=lista_meses, index=len(lista_meses)-1)

    # Separação de Dados para análise
    df_apenas_manut = df_base[~df_base["Placa"].str.contains("COMBUSTÍVEL|SEGURO|RASTREADOR", case=False, na=False)]
    df_filtrado_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Nome"] == mes_sel]
    mes_num_atual = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
    df_acumulado_ate_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] <= mes_num_atual]
    df_anterior_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] == mes_num_atual - 1]

    # 5. Dashboard - ABAS
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📌 Visão Mensal", "📈 Resumo Acumulado", "⛽ Combustível", "🛡️ Seguro", "📑 Detalhamento"])

    with tab1:
        st.markdown(f"### 📊 Desempenho Mensal Manutenção - {mes_sel}")
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            ativos_m = len(get_ativos(df_filtrado_mes_manut))
            ativos_a = len(get_ativos(df_anterior_manut))
            trend_at = ((ativos_m - ativos_a) / ativos_a * 100) if ativos_a > 0 else 0
            draw_card("VEÍCULOS ATIVOS", fmt_br(ativos_m), trend=trend_at, is_lower_better=False)
        
        with c2:
            km_m = df_filtrado_mes_manut['Quilometragem'].sum()
            km_a = df_anterior_manut['Quilometragem'].sum()
            draw_card("QUILOMETRAGEM MENSAL", fmt_br(km_m), trend=((km_m-km_a)/km_a*100) if km_a>0 else 0, is_lower_better=False)
        
        with c3:
            custo_m = df_filtrado_mes_manut['Custo de manutenção'].sum()
            custo_a = df_anterior_manut['Custo de manutenção'].sum()
            custo_medio = custo_m / ativos_m if ativos_m > 0 else 0
            trend_c = ((custo_m - custo_a) / custo_a * 100) if custo_a > 0 else 0
            draw_card("CUSTO MANUTENÇÃO MENSAL", fmt_br(custo_m, True), f"Média: {fmt_br(custo_medio, True)} /veículo", trend=trend_c)
        
        with c4:
            orc_total_manut = sum(ORCAMENTOS_MANUT.get(inst, 0) for inst in inst_ativas)
            gasto_total_acum_manut = df_acumulado_ate_mes_manut["Custo de manutenção"].sum()
            perc_manut = (gasto_total_acum_manut / orc_total_manut * 100) if orc_total_manut > 0 else 0
            draw_card("ORÇAMENTO MANUTENÇÃO", fmt_br(gasto_total_acum_manut, True), f"{perc_manut:.1f}% consumido", progress=perc_manut)

        if busca_placa:
            st.markdown("---")
            st.markdown(f"#### 🔍 Raio-X do Veículo: {busca_placa}")
            df_veiculo = df_base[df_base["Placa"] == busca_placa].sort_values("Mes_Num")
            if not df_veiculo.empty:
                rv1, rv2 = st.columns([2, 1])
                with rv1:
                    fig_raiox = px.line(df_veiculo, x='Mes_Nome', y='Custo de manutenção', markers=True, title="Histórico de Gastos (Manutenção)")
                    fig_raiox.update_traces(line_color='#0288D1', marker=dict(size=10, color='#1A237E'))
                    st.plotly_chart(fig_raiox, use_container_width=True)
                with rv2:
                    st.info(f"📍 **Base:** {df_veiculo['Base'].iloc[-1]}\n\n💰 **Gasto Total Ano:** {fmt_br(df_veiculo['Custo de manutenção'].sum(), True)}\n\n🛣️ **KM Total Ano:** {fmt_br(df_veiculo['Quilometragem'].sum())}")
            st.markdown("---")

        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="chart-title">Ranking de Quilometragem (Top 10)</div>', unsafe_allow_html=True)
            top10_km = df_filtrado_mes_manut.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig_km = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
            fig_km.update_traces(texttemplate='<b>%{text:,.0f}</b>', textposition='outside', textfont=ESTILO_TEXTO)
            st.plotly_chart(fig_km, use_container_width=True, config={'displayModeBar': False})
        with g2:
            st.markdown('<div class="chart-title">Ranking de Manutenção (Top 10)</div>', unsafe_allow_html=True)
            top10_custo = df_filtrado_mes_manut.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#F57C00'])
            fig_custo.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO)
            st.plotly_chart(fig_custo, use_container_width=True, config={'displayModeBar': False})

    with tab2:
        st.markdown(f"### 📈 Resumo Acumulado Manutenção - {ano_sel}")
        evol_inst = df_acumulado_ate_mes_manut.groupby(['Mes_Num', 'Mes_Nome', 'Instituição'])['Custo de manutenção'].sum().reset_index().sort_values('Mes_Num')
        fig_evol = px.line(evol_inst, x='Mes_Nome', y='Custo de manutenção', color='Instituição', markers=True, color_discrete_map={"AMES": "#0288D1", "IAV": "#F57C00"})
        st.plotly_chart(fig_evol, use_container_width=True)

    with tab3:
        st.markdown(f"### ⛽ Gestão de Combustível - {ano_sel}")
        df_comb = df_base[df_base["Placa"].str.startswith("COMBUSTÍVEL", na=False)]
        df_comb_mes = df_comb[df_comb["Mes_Nome"] == mes_sel]
        df_comb_acum = df_comb[df_comb["Mes_Num"] <= mes_num_atual]
        
        k1, k2 = st.columns([1, 2])
        with k1:
            orc_comb = sum(ORCAMENTOS_COMB.get(inst, 0) for inst in inst_ativas)
            gasto_comb = df_comb_acum["Custo de combustível"].sum()
            perc_comb = (gasto_comb / orc_comb * 100) if orc_comb > 0 else 0
            draw_card("EXECUÇÃO COMBUSTÍVEL ANUAL", fmt_br(gasto_comb, True), f"{perc_comb:.1f}% consumido", progress=perc_comb)
        
        st.markdown("---")
        st.markdown('<div class="chart-title">Custos de Combustível por Base</div>', unsafe_allow_html=True)
        custo_comb_base = df_comb_mes.groupby('Base')['Custo de combustível'].sum().reset_index().sort_values('Custo de combustível', ascending=True)
        fig_comb = px.bar(custo_comb_base, x='Custo de combustível', y='Base', orientation='h', text='Custo de combustível', color='Custo de combustível', color_continuous_scale='Blues')
        fig_comb.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO)
        fig_comb.update_layout(showlegend=False, coloraxis_showscale=False, xaxis=dict(showticklabels=False))
        st.plotly_chart(fig_comb, use_container_width=True)

    with tab4:
        st.markdown(f"### 🛡️ Gestão de Seguro - {ano_sel}")
        df_seguro_filter = df_base[df_base["Placa"].str.startswith("SEGURO", na=False)]
        
        if not df_seguro_filter.empty:
            gasto_total_seguro = df_seguro_filter["Custo de seguro"].sum()
            orc_seguro = sum(ORCAMENTOS_SEGURO.get(inst, 0) for inst in inst_ativas)
            perc_seguro = (gasto_total_seguro / orc_seguro * 100) if orc_seguro > 0 else 0
            
            s1, s2 = st.columns([1, 3])
            with s1:
                draw_card("EXECUÇÃO SEGURO ANUAL", fmt_br(gasto_total_seguro, True), f"{perc_seguro:.1f}% consumido", progress=perc_seguro)
            
            st.markdown("---")
            st.markdown('<div class="chart-title">Ranking de Custos de Seguro por Base</div>', unsafe_allow_html=True)
            custo_seg_base = df_seguro_filter.groupby('Base')['Custo de seguro'].sum().reset_index().sort_values('Custo de seguro', ascending=True)
            
            fig_seguro = px.bar(custo_seg_base, x='Custo de seguro', y='Base', orientation='h', text='Custo de seguro', color='Custo de seguro', color_continuous_scale='Blues')
            fig_seguro.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO)
            fig_seguro.update_layout(showlegend=False, coloraxis_showscale=False, xaxis=dict(showticklabels=False))
            st.plotly_chart(fig_seguro, use_container_width=True)
        else:
            st.info("Nenhum lançamento de seguro encontrado para os filtros selecionados.")

    with tab5:
        st.markdown("### 📑 Detalhamento dos Dados")
        st.dataframe(df_base.drop(columns=['Mes_Num', 'Ano']), use_container_width=True)
        csv = df_base.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Dados Filtrados (CSV)", data=csv, file_name='dados_frota.csv', mime='text/csv')
else:
    st.warning("Verifique o arquivo manutencao.xlsx")
