import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Estratégica de Frotas", layout="wide")

# 2. Estilização CSS (Design Corporativo Consolidado)
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

# 3. Carregamento de Dados (Limpeza Robusta de Valores)
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        
        # Padroniza nomes das colunas (remove espaços e busca termos-chave)
        df.columns = [str(c).strip() for c in df.columns]
        for c in df.columns:
            if 'combust' in c.lower(): df = df.rename(columns={c: 'Custo de Combustível'})
            if 'manut' in c.lower() and 'custo' in c.lower(): df = df.rename(columns={c: 'Custo de manutenção'})

        # Função para limpar R$, pontos e vírgulas
        def clean_val(x):
            if pd.isna(x): return 0
            if isinstance(x, (int, float)): return float(x)
            s = str(x).replace('R$', '').replace(' ', '')
            if ',' in s and '.' in s: s = s.replace('.', '').replace(',', '.')
            elif ',' in s: s = s.replace(',', '.')
            return pd.to_numeric(s, errors='coerce')

        # Aplica a limpeza nas colunas financeiras
        if 'Custo de Combustível' in df.columns:
            df['Custo de Combustível'] = df['Custo de Combustível'].apply(clean_val).fillna(0)
        else:
            df['Custo de Combustível'] = 0.0

        if 'Custo de manutenção' in df.columns:
            df['Custo de manutenção'] = df['Custo de manutenção'].apply(clean_val).fillna(0)
        else:
            df['Custo de manutenção'] = 0.0

        df['Quilometragem'] = pd.to_numeric(df.get('Quilometragem', 0), errors='coerce').fillna(0)

        # Tratamento de Datas e Meses
        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
        
        # Tratamento de Ano
        if 'Ano' in df.columns:
            df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int)
        else:
            df['Ano'] = 2026
            
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()

# DEFINIÇÃO DOS ORÇAMENTOS (AMES e IAV separados)
ORC_MANUTENCAO = {"AMES": 987380.00, "IAV": 305434.00}
ORC_COMBUSTIVEL = {"AMES": 1000081.06, "IAV": 264450.00}

if not df.empty:
    # 4. Sidebar
    st.sidebar.markdown("### 🏢 GESTÃO DE FROTAS")
    if st.sidebar.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()

    ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano"].unique(), reverse=True))
    df_ano = df[df["Ano"] == ano_sel]
    
    inst_sel = st.sidebar.multiselect("Instituição", options=sorted(df_ano["Instituição"].unique()), default=sorted(df_ano["Instituição"].unique()))
    lista_meses = df_ano.sort_values("Mes_Num")["Mes_Nome"].unique()
    mes_sel = st.sidebar.selectbox("Mês Competência", options=lista_meses, index=len(lista_meses)-1)

    # Lógica de Filtros
    df_base = df_ano[df_ano["Instituição"].isin(inst_sel)]
    df_filtrado_mes = df_base[df_base["Mes_Nome"] == mes_sel]
    mes_num_atual = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
    df_acumulado_ate_mes = df_base[df_base["Mes_Num"] <= mes_num_atual]
    
    # Lógica de Placa Virtual (Ignora "COMBUSTÍVEL" nos rankings de veículos)
    df_veiculos_mes = df_filtrado_mes[~df_filtrado_mes['Placa'].str.contains('COMBUSTÍVEL', na=False, case=False)]

    # 5. Estrutura de Abas
    tab1, tab2, tab3 = st.tabs(["📌 Visão Mensal", "📈 Resumo Acumulado", "📑 Detalhamento"])

    with tab1:
        st.markdown(f"### 📊 Desempenho Mensal - {mes_sel}")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        with c1: draw_card("Veículos Ativos", fmt_br(len(df_veiculos_mes["Placa"].unique())))
        with c2: draw_card("Quilometragem Mensal", fmt_br(df_filtrado_mes['Quilometragem'].sum()))
        with c3: draw_card("Custo Manutenção (Mês)", fmt_br(df_filtrado_mes['Custo de manutenção'].sum(), True))
        with c4: draw_card("Custo Combustível (Mês)", fmt_br(df_filtrado_mes['Custo de Combustível'].sum(), True))
        
        with c5:
            orc_m = sum(ORC_MANUTENCAO.get(inst, 0) for inst in inst_sel)
            acum_m = df_acumulado_ate_mes['Custo de manutenção'].sum()
            perc_m = (acum_m / orc_m * 100) if orc_m > 0 else 0
            draw_card("Exec. Manutenção (Ano)", fmt_br(acum_m, True), f"{perc_m:.1f}% consumido", progress=perc_m)
            
        with c6:
            orc_c = sum(ORC_COMBUSTIVEL.get(inst, 0) for inst in inst_sel)
            acum_c = df_acumulado_ate_mes['Custo de Combustível'].sum()
            perc_c = (acum_c / orc_c * 100) if orc_c > 0 else 0
            draw_card("Exec. Combustível (Ano)", fmt_br(acum_c, True), f"{perc_c:.1f}% consumido", progress=perc_c)

        st.markdown("<br>", unsafe_allow_html=True)
        
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="chart-title">Ranking de Quilometragem (Veículos)</div>', unsafe_allow_html=True)
            top10_km = df_veiculos_mes.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig_km = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
            fig_km.update_traces(texttemplate='%{text:,.0f}', textposition='outside', cliponaxis=False)
            fig_km.update_layout(height=350, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=100, t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False, range=[0, top10_km['Quilometragem'].max()*1.3 if not top10_km.empty else 1]), yaxis=dict(title=""))
            st.plotly_chart(fig_km, use_container_width=True)
        with g2:
            st.markdown('<div class="chart-title">Ranking de Custos Manutenção (Veículos)</div>', unsafe_allow_html=True)
            top10_m = df_veiculos_mes.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig_m = px.bar(top10_m, x='Custo de manutenção', y='Placa', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#F57C00'])
            fig_m.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside', cliponaxis=False)
            fig_m.update_layout(height=350, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=120, t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False, range=[0, top10_m['Custo de manutenção'].max()*1.4 if not top10_m.empty else 1]), yaxis=dict(title=""))
            st.plotly_chart(fig_m, use_container_width=True)

        st.markdown('<div class="chart-title">Ranking de Bases por Custo de Combustível (Mês)</div>', unsafe_allow_html=True)
        ranking_base_c = df_filtrado_mes.groupby('Base')['Custo de Combustível'].sum().reset_index().nlargest(10, 'Custo de Combustível').sort_values('Custo de Combustível', ascending=True)
        fig_b_c = px.bar(ranking_base_c, x='Custo de Combustível', y='Base', orientation='h', text='Custo de Combustível', color_discrete_sequence=['#388E3C'])
        fig_b_c.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside', cliponaxis=False)
        fig_b_c.update_layout(height=450, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=150, t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False, range=[0, ranking_base_c['Custo de Combustível'].max()*1.3 if not ranking_base_c.empty else 1]), yaxis=dict(title=""))
        st.plotly_chart(fig_b_c, use_container_width=True)

    with tab2:
        st.title("📈 Resumo Acumulado")
        evol_mes = df_acumulado_ate_mes.groupby(['Mes_Num', 'Mes_Nome']).agg({'Custo de manutenção':'sum', 'Custo de Combustível':'sum'}).reset_index().sort_values('Mes_Num')
        fig_e = px.line(evol_mes, x='Mes_Nome', y=['Custo de manutenção', 'Custo de Combustível'], markers=True, color_discrete_map={'Custo de manutenção': '#F57C00', 'Custo de Combustível': '#388E3C'})
        fig_e.update_layout(height=400, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(title=""), yaxis=dict(title="R$"))
        st.plotly_chart(fig_e, use_container_width=True)

    with tab3:
        st.markdown("### 📑 Detalhamento dos Dados")
        st.dataframe(df_filtrado_mes.drop(columns=['Mes_Num', 'Ano']), use_container_width=True)
else:
    st.info("Aguardando carregamento do arquivo 'manutencao.xlsx'.")
