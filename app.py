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
    
    /* Configuração da Barra de Progresso */
    .progress-bg { background-color: #E0E0E0; border-radius: 10px; width: 100%; height: 8px; margin-top: 10px; }
    .progress-fill { height: 8px; border-radius: 10px; }
    .bg-normal { background-color: #F57C00; } /* Laranja (Normal) */
    .bg-alert { background-color: #D32F2F !important; } /* Vermelho (Acima de 100%) */
    
    /* NOVO: Estilização dos Indicadores do Raio-X */
    .raiox-container {
        display: flex;
        flex-wrap: wrap;
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #CFD8DC;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .raiox-item {
        flex: 1;
        min-width: 150px;
        text-align: center;
        border-right: 1px solid #E0E0E0;
    }
    .raiox-item:last-child {
        border-right: none;
    }
    .raiox-label {
        color: #546E7A !important;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
    }
    .raiox-value {
        color: #1A237E !important;
        font-size: 20px;
        font-weight: 800;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

ESTILO_TEXTO = dict(size=13, color='#333333', family="Arial, sans-serif")

def fmt_br(valor, is_moeda=False):
    if is_moeda:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{valor:,.0f}".replace(",", ".")

def get_ativos(df):
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
    
    prog_html = ""
    if progress is not None:
        prog_color = "bg-alert" if progress > 100 else "bg-normal"
        prog_html = f'<div class="progress-bg"><div class="progress-fill {prog_color}" style="width: {min(progress, 100)}%;"></div></div>'
    
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
        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 
                    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
        
        df['Quilometragem'] = pd.to_numeric(df['Quilometragem'], errors='coerce').fillna(0)
        df['Custo de manutenção'] = pd.to_numeric(df['Custo de manutenção'], errors='coerce').fillna(0)
        df['Custo de seguro'] = pd.to_numeric(df.get('Custo de seguro', 0), errors='coerce').fillna(0)
        df['Custo de Rastreador'] = pd.to_numeric(df.get('Custo de Rastreador', 0), errors='coerce').fillna(0)
        
        if 'Custo de combustível' in df.columns:
            df['Custo Combustível'] = pd.to_numeric(df['Custo de combustível'], errors='coerce').fillna(0)
        else:
            df['Custo Combustível'] = pd.to_numeric(df.iloc[:, 3], errors='coerce').fillna(0)

        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int) if 'Ano' in df.columns else 2026
        
        if 'Centro de Custo' in df.columns: df['Centro de Custo'] = df['Centro de Custo'].astype(str).str.strip()
        if 'Base' in df.columns: df['Base'] = df['Base'].astype(str).str.strip()
        if 'Instituição' in df.columns: df['Instituição'] = df['Instituição'].astype(str).str.strip()
        if 'Placa' in df.columns: df['Placa'] = df['Placa'].astype(str).str.strip().str.upper().replace('NAN', '')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()

# VERBAS
ORCAMENTOS_MANUT = {"AMES": 987380.00, "IAV": 305434.00}
ORCAMENTOS_COMB = {"AMES": 1000081.06, "IAV": 264450.00}
ORCAMENTOS_SEGURO = {"AMES": 186682.00, "IAV": 115461.00}
ORCAMENTOS_RASTREADOR = {"AMES": 0.00, "IAV": 10194.00} 

if not df.empty:
    st.sidebar.markdown("### 🏢 GESTÃO DE FROTAS")
    ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano"].unique(), reverse=True))
    df_ano = df[df["Ano"] == ano_sel]
    opcoes_inst =["TODAS"] + sorted(df_ano["Instituição"].unique())
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

    df_apenas_comb = df_base[df_base["Placa"].str.startswith("COMBUSTÍVEL", na=False)]
    df_apenas_manut = df_base[~df_base["Placa"].str.startswith("COMBUSTÍVEL", na=False)]

    df_filtrado_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Nome"] == mes_sel]
    mes_num_atual = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
    df_acumulado_ate_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] <= mes_num_atual]
    df_anterior_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] == mes_num_atual - 1]

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📌 Visão Mensal", "📈 Resumo Acumulado", "⛽ Combustível", "🛡️ Custos Fixos", "📑 Detalhamento"])

    with tab1:
        st.markdown(f"### 📊 Desempenho Mensal Manutenção - {mes_sel}")
        c1, c2, c3 = st.columns(3)
        
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
            num_veiculos = len(get_ativos(df_filtrado_mes_manut))
            custo_medio = custo_m / num_veiculos if num_veiculos > 0 else 0
            trend_c = ((custo_m - custo_a) / custo_a * 100) if custo_a > 0 else 0
            draw_card("CUSTO MANUTENÇÃO MENSAL", fmt_br(custo_m, True), f"Média: {fmt_br(custo_medio, True)} /veículo", trend=trend_c)

        if busca_placa:
            st.markdown("---")
            st.markdown(f"#### 🔍 Raio-X do Veículo: {busca_placa}")
            df_veiculo = df_base[df_base["Placa"] == busca_placa].sort_values("Mes_Num")
            
            if not df_veiculo.empty:
                v_gasto_total = df_veiculo['Custo de manutenção'].sum()
                v_km_total = df_veiculo['Quilometragem'].sum()
                v_custo_km = v_gasto_total / v_km_total if v_km_total > 0 else 0
                v_base = df_veiculo['Base'].iloc[-1]
                
                # NOVO CARD DE INDICADORES ALINHADOS
                st.markdown(f"""
                <div class="raiox-container">
                    <div class="raiox-item">
                        <div class="raiox-label">📍 Base atual</div>
                        <div class="raiox-value">{v_base}</div>
                    </div>
                    <div class="raiox-item">
                        <div class="raiox-label">💰 Gasto Total Ano</div>
                        <div class="raiox-value">{fmt_br(v_gasto_total, True)}</div>
                    </div>
                    <div class="raiox-item">
                        <div class="raiox-label">🛣️ KM Total Ano</div>
                        <div class="raiox-value">{fmt_br(v_km_total)}</div>
                    </div>
                    <div class="raiox-item">
                        <div class="raiox-label">📊 Custo por KM</div>
                        <div class="raiox-value">{fmt_br(v_custo_km, True)}/km</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Gráfico com largura total abaixo dos cards
                fig_raiox = px.line(df_veiculo, x='Mes_Nome', y='Custo de manutenção', markers=True, title="Histórico de Gastos (Manutenção)")
                fig_raiox.update_traces(line_color='#0288D1', marker=dict(size=10, color='#1A237E'))
                fig_raiox.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=0))
                st.plotly_chart(fig_raiox, use_container_width=True)
            else:
                st.warning("Veículo não encontrado nesta seleção.")
            st.markdown("---")
        
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="chart-title">Ranking de Quilometragem (Top 10)</div>', unsafe_allow_html=True)
            top10_km = df_filtrado_mes_manut.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig_km = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
            fig_km.update_traces(texttemplate='<b>%{text:,.0f}</b>', textposition='outside', textfont=ESTILO_TEXTO, cliponaxis=False)
            max_km = top10_km['Quilometragem'].max() if not top10_km.empty else 1
            fig_km.update_layout(height=400, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=80, r=100, t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_km * 1.5]), yaxis=dict(tickfont=dict(size=12, color='#333333', family="Arial Black")))
            st.plotly_chart(fig_km, use_container_width=True, config={'displayModeBar': False})
        with g2:
            st.markdown('<div class="chart-title">Ranking de Manutenção (Top 10)</div>', unsafe_allow_html=True)
            top10_custo = df_filtrado_mes_manut.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#F57C00'])
            fig_custo.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO, cliponaxis=False)
            max_c = top10_custo['Custo de manutenção'].max() if not top10_custo.empty else 1
            fig_custo.update_layout(height=400, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=80, r=130, t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_c * 1.7]), yaxis=dict(tickfont=dict(size=12, color='#333333', family="Arial Black")))
            st.plotly_chart(fig_custo, use_container_width=True, config={'displayModeBar': False})

    with tab2:
        st.markdown(f"### 📈 Resumo Acumulado Manutenção - {ano_sel}")
        
        ca1, ca2, ca3 = st.columns(3)
        with ca1:
            orc_total_manut = sum(ORCAMENTOS_MANUT.get(inst, 0) for inst in inst_ativas)
            gasto_total_acum_manut = df_acumulado_ate_mes_manut["Custo de manutenção"].sum()
            perc_manut = (gasto_total_acum_manut / orc_total_manut * 100) if orc_total_manut > 0 else 0
            draw_card("ORÇAMENTO MANUT. (ACUMULADO)", fmt_br(gasto_total_acum_manut, True), f"{perc_manut:.1f}% consumido do ano", progress=perc_manut)
        
        st.markdown("---")
        evol_inst = df_acumulado_ate_mes_manut.groupby(['Mes_Num', 'Mes_Nome', 'Instituição'])['Custo de manutenção'].sum().reset_index().sort_values('Mes_Num')
        fig_evol = px.line(evol_inst, x='Mes_Nome', y='Custo de manutenção', color='Instituição', markers=True, color_discrete_map={"AMES": "#0288D1", "IAV": "#F57C00"})
        st.plotly_chart(fig_evol, use_container_width=True)

        st.markdown("---")
        st.markdown(f'<div class="chart-title">Top 10 Bases com Maior Custo de Manutenção Acumulado (Até {mes_sel})</div>', unsafe_allow_html=True)
        custo_base_acum = df_acumulado_ate_mes_manut.groupby('Base')['Custo de manutenção'].sum().reset_index().nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
        
        if not custo_base_acum.empty:
            fig_base_acum = px.bar(custo_base_acum, x='Custo de manutenção', y='Base', orientation='h', text='Custo de manutenção', color='Custo de manutenção', color_continuous_scale='Blues')
            fig_base_acum.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO, cliponaxis=False)
            max_cb = custo_base_acum['Custo de manutenção'].max()
            fig_base_acum.update_layout(height=400, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=100, r=150, t=0, b=0), showlegend=False, coloraxis_showscale=False, xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_cb * 1.6]), yaxis=dict(tickfont=dict(size=12, color='#333333', family="Arial Black")))
            st.plotly_chart(fig_base_acum, use_container_width=True, config={'displayModeBar': False})

    with tab3:
        st.markdown(f"### ⛽ Gestão de Combustível - {ano_sel}")
        df_comb_mes = df_apenas_comb[df_apenas_comb["Mes_Nome"] == mes_sel]
        df_comb_acum = df_apenas_comb[df_apenas_comb["Mes_Num"] <= mes_num_atual]
        df_comb_anterior = df_apenas_comb[df_apenas_comb["Mes_Num"] == mes_num_atual - 1]

        k1, k2 = st.columns([1, 2])
        with k1:
            orc_total_comb = sum(ORCAMENTOS_COMB.get(inst, 0) for inst in inst_ativas)
            gasto_acum_comb = df_comb_acum["Custo Combustível"].sum()
            gasto_m_comb = df_comb_mes["Custo Combustível"].sum()
            gasto_a_comb = df_comb_anterior["Custo Combustível"].sum()
            perc_comb = (gasto_acum_comb / orc_total_comb * 100) if orc_total_comb > 0 else 0
            trend_comb = ((gasto_m_comb - gasto_a_comb) / gasto_a_comb * 100) if gasto_a_comb > 0 else 0
            draw_card("EXECUÇÃO COMBUSTÍVEL ANUAL", fmt_br(gasto_acum_comb, True), f"Gasto no mês: {fmt_br(gasto_m_comb, True)}", trend=trend_comb, progress=perc_comb)
        
        st.markdown("---")
        st.markdown(f'<div class="chart-title">Ranking de Custos de Combustível por Base - {mes_sel}</div>', unsafe_allow_html=True)
        custo_comb_base = df_comb_mes.groupby('Base')['Custo Combustível'].sum().reset_index().sort_values('Custo Combustível', ascending=True)
        if not custo_comb_base.empty:
            fig_comb = px.bar(custo_comb_base, x='Custo Combustível', y='Base', orientation='h', text='Custo Combustível', color='Custo Combustível', color_continuous_scale='Blues')
            fig_comb.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO, cliponaxis=False)
            max_cc = custo_comb_base['Custo Combustível'].max()
            fig_comb.update_layout(height=max(400, len(custo_comb_base) * 35), separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_cc * 1.6]), yaxis=dict(tickfont=dict(size=12, color='#333333', family="Arial Black")), showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_comb, use_container_width=True, config={'displayModeBar': False})

    with tab4:
        st.markdown(f"### 🛡️ Gestão de Custos Fixos - {ano_sel}")
        df_fixos_acum = df_base[df_base["Mes_Num"] <= mes_num_atual]
        
        orc_seguro = sum(ORCAMENTOS_SEGURO.get(inst, 0) for inst in inst_ativas)
        orc_rastreador = sum(ORCAMENTOS_RASTREADOR.get(inst, 0) for inst in inst_ativas)
        
        gasto_seguro = df_fixos_acum["Custo de seguro"].sum()
        gasto_rastreador = df_fixos_acum["Custo de Rastreador"].sum()
        
        perc_seguro = (gasto_seguro / orc_seguro * 100) if orc_seguro > 0 else 0
        perc_rastreador = (gasto_rastreador / orc_rastreador * 100) if orc_rastreador > 0 else 0
        
        cf1, cf2 = st.columns(2)
        with cf1:
            draw_card("EXECUÇÃO SEGURO DE VEÍCULOS", fmt_br(gasto_seguro, True), f"Orçamento: {fmt_br(orc_seguro, True)}", progress=perc_seguro)
        with cf2:
            draw_card("EXECUÇÃO RASTREADOR", fmt_br(gasto_rastreador, True), f"Orçamento: {fmt_br(orc_rastreador, True)}", progress=perc_rastreador)
            
        st.markdown("---")
        st.markdown('<div class="chart-title">Evolução Mensal de Custos Fixos</div>', unsafe_allow_html=True)
        
        evol_fixos = df_fixos_acum.groupby(['Mes_Nome', 'Mes_Num'])[['Custo de seguro', 'Custo de Rastreador']].sum().reset_index().sort_values('Mes_Num')
        evol_fixos_melted = evol_fixos.melt(id_vars=['Mes_Nome', 'Mes_Num'], 
                                            value_vars=['Custo de seguro', 'Custo de Rastreador'], 
                                            var_name='Tipo Despesa', 
                                            value_name='Custo')
        
        evol_fixos_melted['Tipo Despesa'] = evol_fixos_melted['Tipo Despesa'].map({'Custo de seguro': 'Seguro', 'Custo de Rastreador': 'Rastreador'})
        
        if evol_fixos_melted['Custo'].sum() > 0:
            fig_fixos = px.bar(evol_fixos_melted, x='Mes_Nome', y='Custo', color='Tipo Despesa', barmode='group', color_discrete_map={"Seguro": "#1A237E", "Rastreador": "#0288D1"})
            fig_fixos.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="Custo (R$)", xaxis_title="")
            fig_fixos.update_traces(texttemplate='<b>R$ %{y:,.0f}</b>', textposition='outside', textfont=ESTILO_TEXTO)
            st.plotly_chart(fig_fixos, use_container_width=True)
        else:
            st.info("Nenhum custo de Seguro ou Rastreador lançado nestes meses.")

    with tab5:
        st.markdown("### 📑 Detalhamento dos Dados")
        st.dataframe(df_base.drop(columns=['Mes_Num', 'Ano']), use_container_width=True)
else:
    st.warning("Verifique o arquivo manutencao.xlsx")
