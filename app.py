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
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 10px;
    }
    .metric-label { color: #546E7A !important; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px;}
    .metric-value { color: #1A237E !important; font-size: 24px; font-weight: 800; line-height: 1.1; }
    .metric-subtext { color: #333333 !important; font-size: 13px; font-weight: 500; margin-top: 5px; }
    
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
    .progress-bg { background-color: #E0E0E0; border-radius: 10px; width: 100%; height: 6px; margin-top: 10px; }
    .progress-fill { background-color: #F57C00; height: 6px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Funções de Apoio
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
    
    # NOVO: Filtro de Busca por Placa
    busca_placa = st.sidebar.text_input("🔍 Buscar Placa específica", "").upper()
    
    lista_meses = df_ano.sort_values("Mes_Num")["Mes_Nome"].unique()
    mes_sel = st.sidebar.selectbox("Mês Competência", options=lista_meses, index=len(lista_meses)-1)

    # Aplicação dos Filtros
    df_base = df_ano[df_ano["Instituição"].isin(inst_sel)]
    if busca_placa:
        df_base = df_base[df_base["Placa"].str.contains(busca_placa)]

    df_filtrado_mes = df_base[df_base["Mes_Nome"] == mes_sel]
    mes_num_atual = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
    df_acumulado_ate_mes = df_base[df_base["Mes_Num"] <= mes_num_atual]
    df_anterior = df_base[df_base["Mes_Num"] == mes_num_atual - 1]

    # 5. Dashboard
    tab1, tab2, tab3 = st.tabs(["📌 Visão Mensal", "📈 Resumo Acumulado", "📑 Detalhamento"])

    with tab1:
        st.markdown(f"### 📊 Desempenho Mensal - {mes_sel}")
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            draw_card("VEÍCULOS ATIVOS", fmt_br(len(df_filtrado_mes["Placa"].unique())))
        with c2:
            km_m = df_filtrado_mes['Quilometragem'].sum()
            km_a = df_anterior['Quilometragem'].sum()
            draw_card("QUILOMETRAGEM MENSAL", fmt_br(km_m), trend=((km_m-km_a)/km_a*100) if km_a>0 else 0, is_lower_better=False)
        with c3:
            custo_m = df_filtrado_mes['Custo de manutenção'].sum()
            num_veiculos = len(df_filtrado_mes["Placa"].unique())
            custo_medio = custo_m / num_veiculos if num_veiculos > 0 else 0
            draw_card("CUSTO DE MANUTENÇÃO MENSAL", fmt_br(custo_m, True), f"Média: {fmt_br(custo_medio, True)} /veículo")
        with c4:
            # Cálculo do orçamento apenas das instituições filtradas
            orc_total = sum(ORCAMENTOS.get(inst, 0) for inst in inst_sel)
            gasto_total_acum = df_acumulado_ate_mes["Custo de manutenção"].sum()
            perc = (gasto_total_acum / orc_total * 100) if orc_total > 0 else 0
            draw_card("EXECUÇÃO ORÇAMENTÁRIA ANUAL", fmt_br(gasto_total_acum, True), f"{perc:.1f}% consumido", progress=perc)

        st.markdown("<br>", unsafe_allow_html=True)
        
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="chart-title">Ranking de Quilometragem (Top 10)</div>', unsafe_allow_html=True)
            top10_km = df_filtrado_mes.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig_km = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
            fig_km.update_traces(texttemplate='%{text:,.0f}', textposition='outside', cliponaxis=False)
            fig_km.update_layout(height=400, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                 margin=dict(l=80, r=100, t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, top10_km['Quilometragem'].max()*1.3 if not top10_km.empty else 1]), yaxis=dict(title=""))
            st.plotly_chart(fig_km, use_container_width=True, config={'displayModeBar': False})
            
        with g2:
            st.markdown('<div class="chart-title">Ranking de Custos de Manutenção (Top 10)</div>', unsafe_allow_html=True)
            top10_custo = df_filtrado_mes.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#F57C00'])
            fig_custo.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside', cliponaxis=False)
            fig_custo.update_layout(height=400, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                    margin=dict(l=80, r=130, t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, top10_custo['Custo de manutenção'].max()*1.4 if not top10_custo.empty else 1]), yaxis=dict(title=""))
            st.plotly_chart(fig_custo, use_container_width=True, config={'displayModeBar': False})

    with tab2:
        st.markdown(f"### 📈 Resumo Acumulado {ano_sel}")
        st.markdown('<div class="chart-title">Evolução dos Custos vs. Cota Mensal Planejada</div>', unsafe_allow_html=True)
        
        evol_inst = df_acumulado_ate_mes.groupby(['Mes_Num', 'Mes_Nome', 'Instituição'])['Custo de manutenção'].sum().reset_index().sort_values('Mes_Num')
        fig_evol = px.line(evol_inst, x='Mes_Nome', y='Custo de manutenção', color='Instituição', markers=True, color_discrete_map={"AMES": "#0288D1", "IAV": "#F57C00"})
        
        # ADIÇÃO: Linha de Cota Mensal (Orçamento Total / 12)
        cota_mensal = orc_total / 12 if orc_total > 0 else 0
        fig_evol.add_hline(y=cota_mensal, line_dash="dash", line_color="#D32F2F", 
                           annotation_text=f"Cota Mensal: {fmt_br(cota_mensal, True)}", 
                           annotation_position="top left")

        fig_evol.update_layout(height=400, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20), xaxis=dict(title=""), yaxis=dict(title="Custo Total (R$)", showgrid=True, gridcolor='#E0E0E0'))
        st.plotly_chart(fig_evol, use_container_width=True)

        st.markdown("---")
        st.markdown('<div class="chart-title">Top 10 Bases com Maior Custo de Manutenção (Acumulado)</div>', unsafe_allow_html=True)
        custo_base = df_acumulado_ate_mes.groupby('Base')['Custo de manutenção'].sum().reset_index().nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
        fig_base = px.bar(custo_base, x='Custo de manutenção', y='Base', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#1A237E'])
        fig_base.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside', cliponaxis=False)
        fig_base.update_layout(height=400, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=100, r=150, t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, custo_base['Custo de manutenção'].max()*1.3 if not custo_base.empty else 1]), yaxis=dict(title=""))
        st.plotly_chart(fig_base, use_container_width=True, config={'displayModeBar': False})

    with tab3:
        st.markdown("### 📑 Detalhamento dos Dados")
        st.dataframe(df_filtrado_mes.drop(columns=['Mes_Num', 'Ano']), use_container_width=True)
        csv = df_filtrado_mes.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Dados Filtrados (CSV)", csv, f"frota_extracao.csv", "text/csv")
else:
    st.warning("Verifique o arquivo manutencao.xlsx")
