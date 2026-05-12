import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Estratégica de Frotas", layout="wide")

# 2. Estilização CSS (Mantendo seu layout original)
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
    
    .metric-label { color: #546E7A !important; font-size: 11px; font-weight: 700; text-transform: uppercase; height: 35px; display: flex; align-items: center;}
    .metric-value { color: #1A237E !important; font-size: 24px; font-weight: 800; height: 40px; display: flex; align-items: center;}
    .metric-subtext { color: #333333 !important; font-size: 13px; font-weight: 500; height: 25px; display: flex; align-items: center;}
    .trend-container { height: 25px; display: flex; align-items: center; margin-top: 5px; }
    .chart-title { height: 50px; display: flex; align-items: center; font-size: 16px; font-weight: 700; color: #1A237E !important; text-align: left; margin-bottom: 5px; }
    
    .stTabs [data-baseweb="tab"] { color: #1A237E !important; font-weight: 600; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #F57C00 !important; background-color: rgba(255,255,255,0.3) !important; }
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
        color = "color: #388E3C !important;" if (trend <= 0 if is_lower_better else trend >= 0) else "color: #D32F2F !important;"
        icon = "↓" if trend <= 0 else "↑"
        trend_html = f'<div style="{color} font-size: 13px; font-weight: bold;">{icon} {abs(trend):.1f}% vs mês ant.</div>'
    
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtext">{subtext}</div>
            <div class="trend-container">{trend_html}</div>
        </div>
    """, unsafe_allow_html=True)

# 3. Carregamento de Dados
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        
        # Converter vírgulas em pontos para colunas financeiras se forem strings
        cols_financeiras = ['Custo de manutenção', 'Custo de combustível', 'Custo do seguro']
        for col in cols_financeiras:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '.')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 
                    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
        df['Quilometragem'] = pd.to_numeric(df['Quilometragem'], errors='coerce').fillna(0)
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 4. Sidebar
    st.sidebar.markdown("### 🏢 GESTÃO DE FROTAS")
    ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano"].unique(), reverse=True))
    df_ano = df[df["Ano"] == ano_sel]
    
    inst_sel = st.sidebar.multiselect("Instituição", options=sorted(df_ano["Instituição"].unique()), default=sorted(df_ano["Instituição"].unique()))
    busca_placa = st.sidebar.text_input("🔍 Buscar Placa específica", "").upper()
    
    lista_meses = df_ano.sort_values("Mes_Num")["Mes_Nome"].unique()
    mes_sel = st.sidebar.selectbox("Mês Competência", options=lista_meses, index=len(lista_meses)-1)

    # Filtros de Categorização
    df_base = df_ano[df_ano["Instituição"].isin(inst_sel)]
    
    # Filtro flexível para combustível e seguros (aceita com ou sem acento)
    df_apenas_comb = df_base[df_base["Placa"].str.contains("COMBUST[IÍ]VEL", case=False, na=False)]
    df_apenas_seguro = df_base[df_base["Placa"].str.contains("SEGURO", case=False, na=False)]
    
    # Manutenção é tudo que não é combustível nem seguro
    df_apenas_manut = df_base[
        (~df_base["Placa"].str.contains("COMBUST[IÍ]VEL", case=False, na=False)) & 
        (~df_base["Placa"].str.contains("SEGURO", case=False, na=False))
    ]

    # Dados para cálculos de manutenção
    df_filtrado_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Nome"] == mes_sel]
    mes_num_atual = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
    df_anterior_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] == mes_num_atual - 1]

    # 5. DASHBOARD
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📌 Visão Mensal", "📈 Resumo Acumulado", "⛽ Combustível", "🛡️ Seguros", "📑 Detalhamento"])

    with tab1:
        st.markdown(f"### 📊 Desempenho Mensal Manutenção - {mes_sel}")
        c1, c2, c3 = st.columns(3)
        with c1:
            ativos_m = len(df_filtrado_mes_manut["Placa"].unique())
            draw_card("VEÍCULOS ATIVOS", fmt_br(ativos_m))
        with c2:
            km_m = df_filtrado_mes_manut['Quilometragem'].sum()
            draw_card("QUILOMETRAGEM MENSAL", fmt_br(km_m), is_lower_better=False)
        with c3:
            custo_m = df_filtrado_mes_manut['Custo de manutenção'].sum()
            draw_card("CUSTO MANUTENÇÃO MENSAL", fmt_br(custo_m, True))

        st.markdown("<br>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="chart-title">Ranking de Quilometragem (Top 10)</div>', unsafe_allow_html=True)
            top10_km = df_filtrado_mes_manut.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig_km = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
            fig_km.update_traces(texttemplate='<b>%{text:,.0f}</b>', textposition='outside', textfont=ESTILO_TEXTO)
            fig_km.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=80, r=100, t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False))
            st.plotly_chart(fig_km, use_container_width=True)
        with g2:
            st.markdown('<div class="chart-title">Ranking de Manutenção (Top 10)</div>', unsafe_allow_html=True)
            top10_custo = df_filtrado_mes_manut.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#F57C00'])
            fig_custo.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO)
            fig_custo.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=80, r=130, t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False))
            st.plotly_chart(fig_custo, use_container_width=True)

    with tab2:
        st.markdown(f"### 📈 Resumo Acumulado Manutenção - {ano_sel}")
        evol_manut = df_apenas_manut.groupby(['Mes_Num', 'Mes_Nome', 'Instituição'])['Custo de manutenção'].sum().reset_index().sort_values('Mes_Num')
        fig_evol = px.line(evol_manut, x='Mes_Nome', y='Custo de manutenção', color='Instituição', markers=True, color_discrete_map={"AMES": "#0288D1", "IAV": "#F57C00"})
        st.plotly_chart(fig_evol, use_container_width=True)

    with tab3:
        st.markdown(f"### ⛽ Gestão de Combustível - {mes_sel}")
        df_comb_mes = df_apenas_comb[df_apenas_comb["Mes_Nome"] == mes_sel]
        custo_c_m = df_comb_mes["Custo de combustível"].sum()
        draw_card("GASTO COMBUSTÍVEL TOTAL NO MÊS", fmt_br(custo_c_m, True))
        
        st.markdown("---")
        st.markdown('<div class="chart-title">Custos de Combustível por Base</div>', unsafe_allow_html=True)
        custo_comb_base = df_comb_mes.groupby('Base')['Custo de combustível'].sum().reset_index().sort_values('Custo de combustível', ascending=True)
        fig_comb = px.bar(custo_comb_base, x='Custo de combustível', y='Base', orientation='h', text='Custo de combustível', color_discrete_sequence=['#0288D1'])
        fig_comb.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside')
        st.plotly_chart(fig_comb, use_container_width=True)

    with tab4:
        st.markdown(f"### 🛡️ Gestão de Seguros - {mes_sel}")
        # Filtrar dados de seguro para o mês
        df_seguro_mes = df_apenas_seguro[df_apenas_seguro["Mes_Nome"] == mes_sel]
        
        s1, s2 = st.columns([1, 2])
        with s1:
            total_seguro = df_seguro_mes['Custo do seguro'].sum()
            draw_card("TOTAL EM SEGUROS", fmt_br(total_seguro, True), f"Referente a {mes_sel}")
        
        with s2:
            st.markdown('<div class="chart-title">Custo do Seguro por Base</div>', unsafe_allow_html=True)
            custo_seg_base = df_seguro_mes.groupby('Base')['Custo do seguro'].sum().reset_index().sort_values('Custo do seguro', ascending=True)
            if not custo_seg_base.empty:
                fig_seg = px.bar(custo_seg_base, x='Custo do seguro', y='Base', orientation='h', text='Custo do seguro', color_discrete_sequence=['#607D8B'])
                fig_seg.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO)
                fig_seg.update_layout(xaxis=dict(showticklabels=False, showgrid=False), margin=dict(t=0))
                st.plotly_chart(fig_seg, use_container_width=True)
            else:
                st.info("Nenhum dado de seguro encontrado para este mês.")

    with tab5:
        st.markdown("### 📑 Detalhamento dos Dados")
        st.dataframe(df_base.drop(columns=['Mes_Num', 'Ano']), use_container_width=True)
else:
    st.warning("Verifique o arquivo manutencao.xlsx")
