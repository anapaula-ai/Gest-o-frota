import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Estratégica de Frotas", layout="wide")

# 2. Estilização CSS (Design Corporativo Looker Style)
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD; color: #333333; }
    [data-testid="stSidebar"] { background-color: #BBDEFB; border-right: 1px solid #90CAF9; }
    
    /* Cards de KPI */
    .metric-container {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #CFD8DC;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        min-height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-label { color: #546E7A; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;}
    .metric-value { color: #1A237E; font-size: 28px; font-weight: 800; line-height: 1.1; }
    .metric-subtext { color: #333333; font-size: 14px; font-weight: 500; margin-top: 5px; }
    
    /* Tendências e Barras */
    .trend-up { color: #D32F2F; font-size: 14px; font-weight: bold; }
    .trend-down { color: #388E3C; font-size: 14px; font-weight: bold; }
    .progress-bg { background-color: #E0E0E0; border-radius: 10px; width: 100%; height: 8px; margin-top: 12px; }
    .progress-fill { background-color: #F57C00; height: 8px; border-radius: 10px; }

    /* Estilo de Abas */
    .stTabs [data-baseweb="tab"] { color: #1A237E; font-weight: 600; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #F57C00 !important; }

    /* Títulos */
    h3 { text-align: left !important; color: #1A237E !important; font-weight: 700 !important; margin-bottom: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# Funções de Formatação
def fmt_br(valor, is_moeda=False):
    if is_moeda:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{valor:,.0f}".replace(",", ".")

def draw_card(label, value, subtext="", trend=None, is_lower_better=True, progress=None):
    trend_html = ""
    if trend is not None:
        color = "trend-down" if (trend <= 0 if is_lower_better else trend >= 0) else "trend-up"
        icon = "↓" if trend <= 0 else "↑"
        trend_html = f'<div class="{color}">{icon} {abs(trend):.1f}% vs mês ant.</div>'
    prog_html = f'<div class="progress-bg"><div class="progress-fill" style="width: {min(progress, 100)}%;"></div></div>' if progress is not None else ""
    st.markdown(f"""<div class="metric-container"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-subtext">{subtext}</div>{trend_html}{prog_html}</div>""", unsafe_allow_html=True)

# 3. Dados
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
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int) if 'Ano' in df.columns else 2026
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()
ORCAMENTOS = {"AMES": 987380.00, "IAV": 305434.00}

if not df.empty:
    # 4. Sidebar
    st.sidebar.markdown("### 🏢 GESTÃO DE FROTAS")
    ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano"].unique(), reverse=True))
    df_ano = df[df["Ano"] == ano_sel]
    inst_sel = st.sidebar.multiselect("Instituição", options=sorted(df_ano["Instituição"].unique()), default=sorted(df_ano["Instituição"].unique()))
    lista_meses = df_ano.sort_values("Mes_Num")["Mes_Nome"].unique()
    mes_sel = st.sidebar.selectbox("Mês Competência", options=lista_meses, index=len(lista_meses)-1)

    # Filtros
    df_filtrado_mes = df_ano[(df_ano["Instituição"].isin(inst_sel)) & (df_ano["Mes_Nome"] == mes_sel)]
    mes_num_atual = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
    df_acumulado_ate_mes = df_ano[(df_ano["Instituição"].isin(inst_sel)) & (df_ano["Mes_Num"] <= mes_num_atual)]

    # 5. Estrutura de Abas
    tab1, tab2, tab3 = st.tabs(["📌 Visão Mensal", "📈 Resumo Acumulado", "📑 Detalhamento"])

    with tab1:
        st.title(f"📊 Desempenho Mensal - {mes_sel}")
        c1, c2, c3, c4 = st.columns(4)
        with c1: draw_card("VEÍCULOS ATIVOS", fmt_br(len(df_filtrado_mes["Placa"].unique())))
        with c2:
            km_m = df_filtrado_mes['Quilometragem'].sum()
            km_a = df_ano[(df_ano["Instituição"].isin(inst_sel)) & (df_ano["Mes_Num"] == mes_num_atual - 1)]['Quilometragem'].sum()
            draw_card("QUILOMETRAGEM MENSAL", fmt_br(km_m), trend=((km_m - km_a)/km_a*100) if km_a > 0 else 0, is_lower_better=False)
        with c3:
            custo_m = df_filtrado_mes['Custo de manutenção'].sum()
            custo_a = df_ano[(df_ano["Instituição"].isin(inst_sel)) & (df_ano["Mes_Num"] == mes_num_atual - 1)]['Custo de manutenção'].sum()
            draw_card("CUSTO DE MANUTENÇÃO MENSAL", fmt_br(custo_m, True), trend=((custo_m - custo_a)/custo_a*100) if custo_a > 0 else 0)
        with c4:
            gasto_total = df_acumulado_ate_mes["Custo de manutenção"].sum()
            orc_total = sum(ORCAMENTOS.get(inst, 0) for inst in inst_sel)
            perc = (gasto_total / orc_total * 100) if orc_total > 0 else 0
            draw_card("EXECUÇÃO ORÇAMENTÁRIA ANUAL", fmt_br(gasto_total, True), f"{perc:.1f}% consumido", progress=perc)

        st.markdown("---")
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("Ranking de Quilometragem (Top 10)")
            top10_km = df_filtrado_mes.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig_km = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
            fig_km.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_km.update_layout(separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=100, t=10, b=10), xaxis=dict(showticklabels=False, showgrid=False, zeroline=False), yaxis=dict(title=""))
            st.plotly_chart(fig_km, use_container_width=True, config={'displayModeBar': False})
        with g2:
            st.subheader("Ranking de Custos (Top 10)")
            top10_custo = df_filtrado_mes.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#F57C00'])
            fig_custo.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
            fig_custo.update_layout(separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=120, t=10, b=10), xaxis=dict(showticklabels=False, showgrid=False, zeroline=False), yaxis=dict(title=""))
            st.plotly_chart(fig_custo, use_container_width=True, config={'displayModeBar': False})

    with tab2:
        st.title(f"📈 Resumo Acumulado {ano_sel}")
        
        # Gráfico de Evolução Mensal por Instituição
        st.subheader("Evolução dos Custos de Manutenção por Instituição")
        evol_inst = df_acumulado_ate_mes.groupby(['Mes_Num', 'Mes_Nome', 'Instituição'])['Custo de manutenção'].sum().reset_index().sort_values('Mes_Num')
        fig_evol = px.line(evol_inst, x='Mes_Nome', y='Custo de manutenção', color='Instituição', markers=True, 
                           color_discrete_map={"AMES": "#0288D1", "IAV": "#F57C00"})
        fig_evol.update_layout(separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=40),
                               xaxis=dict(title="Mês de Referência"), yaxis=dict(title="Custo Total (R$)", showgrid=True, gridcolor='#E0E0E0'))
        st.plotly_chart(fig_evol, use_container_width=True)

        st.markdown("---")
        
        # Ranking de Bases
        st.subheader("Ranking de Bases com Maior Custo de Manutenção")
        custo_base = df_acumulado_ate_mes.groupby('Base')['Custo de manutenção'].sum().reset_index().sort_values('Custo de manutenção', ascending=True)
        fig_base = px.bar(custo_base, x='Custo de manutenção', y='Base', orientation='h', text='Custo de manutenção',
                          color_discrete_sequence=['#1A237E'])
        fig_base.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
        fig_base.update_layout(separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=150, t=10, b=10),
                               xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, custo_base['Custo de manutenção'].max() * 1.3]),
                               yaxis=dict(title="", tickfont=dict(size=12)))
        st.plotly_chart(fig_base, use_container_width=True, config={'displayModeBar': False})

    with tab3:
        st.title("📑 Detalhamento dos Dados")
        st.markdown("Dados filtrados de acordo com as seleções da barra lateral.")
        st.dataframe(df_filtrado_mes.drop(columns=['Mes_Num', 'Ano']), use_container_width=True)
        
        # Botão de Download
        csv = df_filtrado_mes.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Dados Filtrados (CSV)", csv, f"frota_{mes_sel}_{ano_sel}.csv", "text/csv")
else:
    st.info("Carregue o arquivo 'manutencao.xlsx' para iniciar.")
