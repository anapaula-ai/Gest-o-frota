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
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 10px;
    }
    
    .metric-label { color: #546E7A !important; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }
    .metric-value { color: #1A237E !important; font-size: 26px; font-weight: 800; }
    .metric-subtext { color: #333333 !important; font-size: 13px; font-weight: 500; margin-top: 2px; }
    
    .progress-bg { background-color: #E0E0E0; border-radius: 10px; width: 100%; height: 8px; margin-top: 15px; }
    .progress-fill { background-color: #F57C00; height: 8px; border-radius: 10px; }
    
    .trend-up { color: #D32F2F !important; font-size: 13px; font-weight: bold; }
    .trend-down { color: #388E3C !important; font-size: 13px; font-weight: bold; }

    .chart-title { font-size: 18px; font-weight: 700; color: #1A237E !important; margin: 20px 0 10px 0; }
    </style>
    """, unsafe_allow_html=True)

ESTILO_TEXTO = dict(size=12, color='#333333', family="Arial Black")

# Funções de Apoio
def fmt_br(valor, is_moeda=False):
    if is_moeda:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{valor:,.0f}".replace(",", ".")

def get_ativos(df):
    # Considera apenas placas com 7 dígitos e remove as "placas virtuais"
    return df[
        (df["Placa"].str.len() == 7) & 
        (~df["Placa"].str.contains("COMBUSTÍVEL|SEGURO|RASTREADOR|FINANC", case=False, na=True))
    ]["Placa"].unique()

def draw_card(label, value, subtext="", trend=None, is_lower_better=True, progress=None):
    trend_html = ""
    if trend is not None and trend != 0:
        color = "trend-down" if (trend <= 0 if is_lower_better else trend >= 0) else "trend-up"
        icon = "↓" if trend <= 0 else "↑"
        trend_html = f'<div class="{color}">{icon} {abs(trend):.1f}% vs mês ant.</div>'
    
    prog_html = ""
    if progress is not None:
        prog_html = f'<div class="progress-bg"><div class="progress-fill" style="width: {min(progress, 100):.1f}%;"></div></div>'
    
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtext">{subtext}</div>
            {trend_html}
            {prog_html}
        </div>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        df.columns = df.columns.str.strip()
        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
        
        colunas_financeiras = ['Quilometragem', 'Custo de manutenção', 'Custo de combustível', 'Custo de seguro']
        for col in colunas_financeiras:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0
                
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int)
        df['Placa'] = df['Placa'].astype(str).str.strip().str.upper().replace('NAN', '')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()
ORCAMENTOS_MANUT = {"AMES": 987380.00, "IAV": 305434.00}
ORCAMENTOS_COMB = {"AMES": 1000081.06, "IAV": 264450.00}
ORCAMENTOS_SEGURO = {"AMES": 186682.00, "IAV": 15382.00}

if not df.empty:
    # --- Sidebar ---
    st.sidebar.markdown("### 🏢 GESTÃO DE FROTAS")
    ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano"].unique(), reverse=True))
    df_ano = df[df["Ano"] == ano_sel]
    
    inst_sel = st.sidebar.selectbox("Instituição", options=["TODAS"] + sorted(df_ano["Instituição"].unique()))
    df_inst = df_ano.copy() if inst_sel == "TODAS" else df_ano[df_ano["Instituição"] == inst_sel]
    inst_ativas = df_ano["Instituição"].unique() if inst_sel == "TODAS" else [inst_sel]

    col_cc = 'Base' if 'Base' in df.columns else 'Centro de Custo'
    cc_sel = st.sidebar.selectbox("Centro de Custo / Base", options=["TODOS"] + sorted(df_inst[col_cc].dropna().unique()))
    df_base = df_inst.copy() if cc_sel == "TODOS" else df_inst[df_inst[col_cc] == cc_sel]
    
    meses_disponiveis = df_ano.sort_values("Mes_Num")["Mes_Nome"].unique()
    mes_sel = st.sidebar.selectbox("Mês Competência", options=meses_disponiveis, index=len(meses_disponiveis)-1)

    # Lógica de Filtros por Placa
    df_manut_anual = df_base[~df_base["Placa"].str.contains("COMBUSTÍVEL|SEGURO|RASTREADOR", case=False, na=False)]
    df_manut_mes = df_manut_anual[df_manut_anual["Mes_Nome"] == mes_sel]
    mes_num_atual = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
    df_manut_acum = df_manut_anual[df_manut_anual["Mes_Num"] <= mes_num_atual]
    df_manut_ant = df_manut_anual[df_manut_anual["Mes_Num"] == mes_num_atual - 1]

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📌 Visão Mensal", "📈 Acumulado", "⛽ Combustível", "🛡️ Seguro", "📑 Detalhes"])

    with tab1:
        st.markdown(f"### 📊 Manutenção Mensal - {mes_sel}")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            at_m = len(get_ativos(df_manut_mes))
            at_a = len(get_ativos(df_manut_ant))
            tr_at = ((at_m - at_a) / at_a * 100) if at_a > 0 else 0
            draw_card("VEÍCULOS ATIVOS", fmt_br(at_m), trend=tr_at, is_lower_better=False)
        with c2:
            km_m = df_manut_mes['Quilometragem'].sum()
            km_a = df_manut_ant['Quilometragem'].sum()
            draw_card("KM MENSAL", fmt_br(km_m), trend=((km_m-km_a)/km_a*100) if km_a>0 else 0, is_lower_better=False)
        with c3:
            cs_m = df_manut_mes['Custo de manutenção'].sum()
            cs_a = df_manut_ant['Custo de manutenção'].sum()
            draw_card("CUSTO MANUTENÇÃO", fmt_br(cs_m, True), f"Média: {fmt_br(cs_m/at_m if at_m>0 else 0, True)}", trend=((cs_m-cs_a)/cs_a*100) if cs_a>0 else 0)
        with c4:
            orc_m = sum(ORCAMENTOS_MANUT.get(i, 0) for i in inst_ativas)
            gst_m = df_manut_acum["Custo de manutenção"].sum()
            perc_m = (gst_m/orc_m*100) if orc_m>0 else 0
            draw_card("ORÇAMENTO ACUMULADO", fmt_br(gst_m, True), f"{perc_m:.1f}% consumido", progress=perc_m)

        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="chart-title">Ranking KM (Top 10)</div>', unsafe_allow_html=True)
            top_km = df_manut_mes.nlargest(10, 'Quilometragem').sort_values('Quilometragem')
            fig_km = px.bar(top_km, x='Quilometragem', y='Placa', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
            fig_km.update_traces(texttemplate='<b>%{text:,.0f}</b>', textposition='outside', cliponaxis=False)
            fig_km.update_layout(height=400, margin=dict(l=80, r=100), xaxis=dict(showticklabels=False, range=[0, top_km['Quilometragem'].max()*1.3 if not top_km.empty else 1]))
            st.plotly_chart(fig_km, use_container_width=True)
        with g2:
            st.markdown('<div class="chart-title">Ranking Manutenção (Top 10)</div>', unsafe_allow_html=True)
            top_cs = df_manut_mes.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção')
            fig_cs = px.bar(top_cs, x='Custo de manutenção', y='Placa', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#F57C00'])
            fig_cs.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', cliponaxis=False)
            fig_cs.update_layout(height=400, margin=dict(l=80, r=120), xaxis=dict(showticklabels=False, range=[0, top_cs['Custo de manutenção'].max()*1.4 if not top_cs.empty else 1]))
            st.plotly_chart(fig_cs, use_container_width=True)

    with tab3:
        st.markdown(f"### ⛽ Gestão de Combustível - Ano {ano_sel}")
        df_comb_anual = df_inst[df_inst["Placa"].str.contains("COMBUSTÍVEL", case=False, na=False)]
        orc_c = sum(ORCAMENTOS_COMB.get(i, 0) for i in inst_ativas)
        gst_c = df_comb_anual["Custo de combustível"].sum()
        perc_c = (gst_c/orc_c*100) if orc_c>0 else 0
        c_c1, _ = st.columns([1, 2])
        with c_c1:
            draw_card("EXECUÇÃO COMBUSTÍVEL ANUAL", fmt_br(gst_c, True), f"Verba: {fmt_br(orc_c, True)}", progress=perc_c)
        
        st.markdown('<div class="chart-title">Combustível por Base (Acumulado Ano)</div>', unsafe_allow_html=True)
        cb_base = df_comb_anual.groupby(col_cc)['Custo de combustível'].sum().reset_index().sort_values('Custo de combustível')
        fig_cb = px.bar(cb_base, x='Custo de combustível', y=col_cc, orientation='h', text='Custo de combustível', color='Custo de combustível', color_continuous_scale='Blues')
        fig_cb.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', cliponaxis=False)
        fig_cb.update_layout(height=max(400, len(cb_base)*30), margin=dict(l=250, r=100), xaxis=dict(showticklabels=False), coloraxis_showscale=False)
        st.plotly_chart(fig_cb, use_container_width=True)

    with tab4:
        st.markdown(f"### 🛡️ Gestão de Seguro - Ano {ano_sel}")
        df_seg_anual = df_inst[df_inst["Placa"].str.contains("SEGURO", case=False, na=False)]
        verba_s = sum(ORCAMENTOS_SEGURO.get(i, 0) for i in inst_ativas)
        gasto_s = df_seg_anual["Custo de seguro"].sum()
        perc_s = (gasto_s / verba_s * 100) if verba_s > 0 else 0
        
        cs1, _ = st.columns([1, 2])
        with cs1:
            draw_card("EXECUÇÃO SEGURO ANUAL", fmt_br(gasto_s, True), f"Verba: {fmt_br(verba_s, True)} ({perc_s:.1f}%)", progress=perc_s)
        
        st.markdown('<div class="chart-title">Ranking de Custos de Seguro por Base</div>', unsafe_allow_html=True)
        seg_base = df_seg_anual.groupby(col_cc)['Custo de seguro'].sum().reset_index().sort_values('Custo de seguro')
        if not seg_base.empty:
            fig_seg = px.bar(seg_base, x='Custo de seguro', y=col_cc, orientation='h', text='Custo de seguro', color='Custo de seguro', color_continuous_scale='Blues')
            fig_seg.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', cliponaxis=False)
            fig_seg.update_layout(height=max(400, len(seg_base)*35), margin=dict(l=250, r=120), xaxis=dict(showticklabels=False, range=[0, seg_base['Custo de seguro'].max()*1.4]), coloraxis_showscale=False)
            st.plotly_chart(fig_seg, use_container_width=True)

    with tab5:
        st.markdown("### 📑 Detalhamento dos Dados")
        st.dataframe(df_base, use_container_width=True)

else:
    st.warning("Verifique o arquivo manutencao.xlsx")
