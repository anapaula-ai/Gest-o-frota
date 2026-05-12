import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Estratégica de Frotas", layout="wide")

# 2. Estilização CSS (Restaurada para o layout original exato)
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
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 10px;
    }
    
    .metric-label { color: #546E7A !important; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;}
    .metric-value { color: #1A237E !important; font-size: 26px; font-weight: 800; margin-bottom: 4px;}
    .metric-subtext { color: #333333 !important; font-size: 13px; font-weight: 500; }
    
    .stTabs [data-baseweb="tab"] { color: #1A237E !important; font-weight: 600; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #F57C00 !important; background-color: rgba(255,255,255,0.3) !important; }
    
    .chart-title { font-size: 16px; font-weight: 700; color: #1A237E !important; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

ESTILO_TEXTO = dict(size=13, color='#333333', family="Arial, sans-serif")

# Funções de Apoio
def fmt_br(valor, is_moeda=False):
    if is_moeda:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{valor:,.0f}".replace(",", ".")

def draw_card(label, value, subtext=""):
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtext">{subtext}</div>
        </div>
    """, unsafe_allow_html=True)

# 3. Carregamento e Limpeza de Dados
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        
        # Função para limpar valores financeiros (remove aspas, troca vírgula por ponto)
        def clean_val(val):
            if isinstance(val, str):
                return val.replace('"', '').replace(' ', '').replace(',', '.')
            return val

        # Colunas para limpar
        cols_to_fix = ['Custo de manutenção', 'Custo de combustível', 'Custo do seguro', 'Quilometragem']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = df[col].apply(clean_val)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 
                    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
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
    busca_placa = st.sidebar.text_input("🔍 Buscar Placa", "").upper()
    
    lista_meses = df_ano.sort_values("Mes_Num")["Mes_Nome"].unique()
    mes_sel = st.sidebar.selectbox("Mês Competência", options=lista_meses, index=len(lista_meses)-1)

    # Filtros de Categorização
    df_base = df_ano[df_ano["Instituição"].isin(inst_sel)]
    
    # Classificação por nome da Placa
    df_apenas_comb = df_base[df_base["Placa"].str.contains("COMBUST", case=False, na=False)]
    df_apenas_seguro = df_base[df_base["Placa"].str.contains("SEGURO", case=False, na=False)]
    df_apenas_manut = df_base[
        (~df_base["Placa"].str.contains("COMBUST", case=False, na=False)) & 
        (~df_base["Placa"].str.contains("SEGURO", case=False, na=False))
    ]

    # Dados Filtrados pelo Mês para Manutenção
    df_m_manut = df_apenas_manut[df_apenas_manut["Mes_Nome"] == mes_sel]

    # 5. DASHBOARD
    tabs = st.tabs(["📌 Visão Mensal", "📈 Acumulado", "⛽ Combustível", "🛡️ Seguros", "📑 Detalhes"])

    with tabs[0]:
        st.markdown(f"### 📊 Resumo Manutenção - {mes_sel}")
        c1, c2, c3 = st.columns(3)
        with c1:
            draw_card("VEÍCULOS ATIVOS", fmt_br(len(df_m_manut["Placa"].unique())))
        with c2:
            draw_card("QUILOMETRAGEM MENSAL", fmt_br(df_m_manut['Quilometragem'].sum()))
        with c3:
            draw_card("CUSTO MANUTENÇÃO", fmt_br(df_m_manut['Custo de manutenção'].sum(), True))

        st.markdown("<br>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="chart-title">Ranking KM (Top 10)</div>', unsafe_allow_html=True)
            top_km = df_m_manut.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig1 = px.bar(top_km, x='Quilometragem', y='Placa', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
            fig1.update_layout(height=350, margin=dict(t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False))
            st.plotly_chart(fig1, use_container_width=True)
        with g2:
            st.markdown('<div class="chart-title">Ranking Manutenção (Top 10)</div>', unsafe_allow_html=True)
            top_custo = df_m_manut.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig2 = px.bar(top_custo, x='Custo de manutenção', y='Placa', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#F57C00'])
            fig2.update_traces(texttemplate='R$ %{text:,.2f}')
            fig2.update_layout(height=350, margin=dict(t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False))
            st.plotly_chart(fig2, use_container_width=True)

    with tabs[1]:
        st.markdown("### 📈 Evolução de Gastos Acumulados")
        evol = df_apenas_manut.groupby(['Mes_Num', 'Mes_Nome', 'Instituição'])['Custo de manutenção'].sum().reset_index().sort_values('Mes_Num')
        fig3 = px.line(evol, x='Mes_Nome', y='Custo de manutenção', color='Instituição', markers=True)
        st.plotly_chart(fig3, use_container_width=True)

    with tabs[2]:
        st.markdown(f"### ⛽ Combustível - {mes_sel}")
        df_c_mes = df_apenas_comb[df_apenas_comb["Mes_Nome"] == mes_sel]
        draw_card("TOTAL COMBUSTÍVEL MÊS", fmt_br(df_c_mes['Custo de combustível'].sum(), True))
        
        custo_c_base = df_c_mes.groupby('Base')['Custo de combustível'].sum().reset_index().sort_values('Custo de combustível', ascending=True)
        fig4 = px.bar(custo_c_base, x='Custo de combustível', y='Base', orientation='h', text='Custo de combustível', color_discrete_sequence=['#1A237E'])
        fig4.update_traces(texttemplate='R$ %{text:,.2f}')
        st.plotly_chart(fig4, use_container_width=True)

    with tabs[3]:
        st.markdown(f"### 🛡️ Seguros - {mes_sel}")
        df_s_mes = df_apenas_seguro[df_apenas_seguro["Mes_Nome"] == mes_sel]
        
        sc1, sc2 = st.columns([1, 2])
        with sc1:
            draw_card("TOTAL EM SEGUROS", fmt_br(df_s_mes['Custo do seguro'].sum(), True), f"Referente a {mes_sel}")
        with sc2:
            st.markdown('<div class="chart-title">Custo do Seguro por Base</div>', unsafe_allow_html=True)
            custo_s_base = df_s_mes.groupby('Base')['Custo do seguro'].sum().reset_index().sort_values('Custo do seguro', ascending=True)
            if not custo_s_base.empty:
                fig5 = px.bar(custo_s_base, x='Custo do seguro', y='Base', orientation='h', text='Custo do seguro', color_discrete_sequence=['#607D8B'])
                fig5.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
                fig5.update_layout(xaxis=dict(showticklabels=False, showgrid=False), margin=dict(t=0))
                st.plotly_chart(fig5, use_container_width=True)
            else:
                st.info("Nenhum dado de seguro encontrado.")

    with tabs[4]:
        st.markdown("### 📑 Base de Dados")
        st.dataframe(df_base.drop(columns=['Mes_Num', 'Ano']), use_container_width=True)
else:
    st.warning("Verifique se o arquivo manutencao.xlsx está correto.")
