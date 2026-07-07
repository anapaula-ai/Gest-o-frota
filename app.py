import streamlit as st
import pandas as pd
import plotly.express as px
import time  # Adicionado para forçar atualização do cache do Google

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Logística", layout="wide")

# ==========================================
# 2. TELA DE LOGIN E SEGURANÇA
# ==========================================
# Crie a sua senha aqui embaixo:
SENHA_ACESSO = "Log2026@"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# Estilo global (CSS)
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
        min-height: 200px; 
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        margin-bottom: 10px;
    }
    
    .metric-label { color: #546E7A !important; font-size: 11px; font-weight: 700; text-transform: uppercase; height: 35px; display: flex; align-items: center; }
    .metric-value { color: #1A237E !important; font-size: 24px; font-weight: 800; height: 40px; display: flex; align-items: center; }
    
    .metric-subtext { color: #333333 !important; font-size: 13px; font-weight: 500; min-height: 25px; display: block; line-height: 1.5; margin-top: 8px; }
    .trend-container { height: 25px; display: flex; align-items: center; margin-top: 5px; }
    .chart-title { height: 50px; display: flex; align-items: center; font-size: 16px; font-weight: 700; color: #1A237E !important; text-align: left; margin-bottom: 5px; }

    /* ==========================================
       ESTILO DAS ABAS (TABS COMO BOTÕES PROPORCIONAIS)
       ========================================== */
    /* Container mestre */
    div[data-testid="stTabs"] {
        overflow: visible !important;
    }

    div[data-testid="stTabs"] > div {
        overflow: visible !important;
    }

    /* Esconde a linha original inferior das abas */
    div[data-baseweb="tab-highlight"], 
    div[data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Container flexível que organiza os botões (Força a quebra de linha) */
    div[data-baseweb="tab-list"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
        width: 100% !important;
        justify-content: stretch !important;
        border-bottom: none !important;
        padding-bottom: 15px !important;
    }

    /* Formato de cada Aba (transformada em Botão) */
    button[data-baseweb="tab"] {
        flex: 1 1 18% !important; /* Estica de forma igual. Ocupa aprox. 20% da tela (5 botões por linha) */
        min-width: 140px !important; /* Para não ficar muito fino no celular */
        background-color: #FFFFFF !important; 
        border: 1px solid #CFD8DC !important; 
        border-radius: 8px !important; 
        padding: 10px !important; 
        margin: 0 !important;
        height: auto !important;
        min-height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
    }

    /* Ajuste do Texto dentro dos Botões */
    button[data-baseweb="tab"] p {
        color: #1A237E !important; 
        font-weight: 700 !important; 
        font-size: 14px !important;
        margin: 0 !important;
        white-space: normal !important; /* Permite quebrar o texto se for longo */
        text-align: center !important;
        line-height: 1.2 !important;
    }

    /* Efeito de passar o mouse */
    button[data-baseweb="tab"]:hover {
        background-color: #F0F4F8 !important;
        border-color: #90CAF9 !important;
        transform: translateY(-2px) !important;
    }

    /* Quando o botão está Selecionado (Aba Ativa) */
    button[data-baseweb="tab"][aria-selected="true"] { 
        background-color: #1A237E !important; 
        border-color: #1A237E !important; 
        box-shadow: 0px 4px 10px rgba(26, 35, 126, 0.2) !important;
    }

    /* Cor do texto quando a Aba está Ativa */
    button[data-baseweb="tab"][aria-selected="true"] p { 
        color: #FFFFFF !important; 
    }
    /* ========================================== */

    .trend-up { color: #D32F2F !important; font-size: 13px; font-weight: bold; }
    .trend-down { color: #388E3C !important; font-size: 13px; font-weight: bold; }
    .progress-bg { background-color: #E0E0E0; border-radius: 10px; width: 100%; height: 8px; margin-top: 10px; }
    .progress-fill { height: 8px; border-radius: 10px; }
    .bg-normal { background-color: #F57C00; } 
    .bg-alert { background-color: #D32F2F !important; } 
    
    .raiox-container { display: flex; flex-wrap: wrap; background-color: #FFFFFF !important; padding: 20px; border-radius: 12px; border: 1px solid #CFD8DC; box-shadow: 0px 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; gap: 10px; }
    .raiox-item { flex: 1; min-width: 130px; text-align: center; border-right: 1px solid #E0E0E0; }
    .raiox-item:last-child { border-right: none; }
    .raiox-label { color: #546E7A !important; font-size: 12px; font-weight: 700; text-transform: uppercase; }
    .raiox-value { color: #1A237E !important; font-size: 20px; font-weight: 800; margin-top: 5px; }
    
    .stDownloadButton button { background-color: #F57C00 !important; color: white !important; font-weight: 600 !important; border-radius: 8px !important; }
    .stDownloadButton button:hover { background-color: #E65100 !important; }
    </style>
""", unsafe_allow_html=True)

# Se não estiver logado, mostra a tela de bloqueio
if not st.session_state["autenticado"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div style="background-color: white; padding: 40px; border-radius: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); text-align: center;">
            <h2 style="color: #1A237E; margin-bottom: 5px;">🏢 LOGÍSTICA</h2>
            <p style="color: #546E7A; margin-bottom: 30px;">Acesso Restrito</p>
        """, unsafe_allow_html=True)
        
        senha_digitada = st.text_input("🔑 Digite a senha para acessar:", type="password")
        
        if st.button("Desbloquear Painel", use_container_width=True):
            if senha_digitada == SENHA_ACESSO:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")
                
        st.markdown("</div>", unsafe_allow_html=True)

# Se estiver logado, mostra o App inteiro
else:
    # Botão de Logout na barra lateral
    st.sidebar.markdown("### 🏢 LOGÍSTICA")
    if st.sidebar.button("🔒 Sair / Bloquear App"):
        st.session_state["autenticado"] = False
        st.rerun()
        
    # --- NOVO BOTÃO DE FORÇAR ATUALIZAÇÃO ---
    if st.sidebar.button("🔄 Forçar Atualização"):
        st.cache_data.clear() # Limpa o cache das planilhas
        st.rerun()            # Recarrega a página
    # ----------------------------------------
    
    st.sidebar.markdown("---")

    ESTILO_TEXTO = dict(size=13, color='#333333', family="Arial, sans-serif")

    def fmt_br(valor, is_moeda=False):
        if is_moeda:
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{valor:,.0f}".replace(",", ".")

    def get_ativos(df):
        excluir_pattern = "COMBUS|SEGUR|FINANC|CONSÓRC|RASTR|LOGIST|MANUT|MENSAL|TAXA"
        return df[
            (~df["Placa"].astype(str).str.contains(excluir_pattern, case=False, na=True)) &
            (df["Placa"].astype(str).str.strip() != "") & 
            (df["Placa"].astype(str).str.upper() != "NAN") &
            (df["Placa"].astype(str).str.strip() != "0")
        ]["Placa"].unique()

    def draw_card(label, value, subtext="", trend=None, is_lower_better=True, progress=None, progress_text=""):
        trend_html = ""
        if trend is not None and trend != 0:
            color = "trend-down" if (trend <= 0 if is_lower_better else trend >= 0) else "trend-up"
            icon = "↓" if trend <= 0 else "↑"
            trend_html = f'<div class="{color}">{icon} {abs(trend):.1f}% vs mês ant.</div>'
        
        prog_html = ""
        if progress is not None:
            prog_color = "bg-alert" if progress > 100 else "bg-normal"
            prog_html = f'<div class="progress-bg"><div class="progress-fill {prog_color}" style="width: {min(progress, 100)}%;"></div></div><div style="font-size: 13.5px; color: #333333; margin-top: 6px; font-weight: 500;">{progress_text}</div>'
        
        html_card = f"""
    <div class="metric-container">
    <div class="metric-label">{label}</div>
    <div class="metric-value">{value}</div>
    <div class="metric-subtext">{subtext}</div>
    <div class="trend-container">{trend_html}</div>
    {prog_html}
    </div>
    """
        st.markdown(html_card, unsafe_allow_html=True)

    def to_float(serie):
        def clean_val(x):
            try:
                if pd.isna(x): return 0.0
                if isinstance(x, (int, float)): return float(x)
                x = str(x).upper().replace('R$', '').replace(' ', '').strip()
                if x == '': return 0.0
                
                if '.' in x and ',' in x:
                    if x.rfind(',') > x.rfind('.'):
                        x = x.replace('.', '').replace(',', '.')
                    else:
                        x = x.replace(',', '')
                elif ',' in x:
                    x = x.replace(',', '.')
                    
                return float(x)
            except:
                return 0.0
        return serie.apply(clean_val)

    @st.cache_data(ttl=60) # Tempo de cache reduzido
    def load_ipva_data():
        try:
            url_ipva_base = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVMBTwRCrEvDUddWeUaIIpdSiA27cuPhHeArqAa_I3b_E8Fa_43lKg5hhSh2StAQddZQIXFFlM-zn-/pub?gid=398571100&single=true&output=csv"
            url_ipva = f"{url_ipva_base}&t={int(time.time())}" # Anti-cache
            
            df_ipva = pd.read_csv(url_ipva, decimal=',', sep=',')
            
            if 'Ipva estimado' in df_ipva.columns:
                df_ipva['Ipva estimado'] = to_float(df_ipva['Ipva estimado'])
                
            return df_ipva
            
        except Exception as e:
            st.error(f"Erro ao carregar dados de IPVA: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=60) # Tempo de cache reduzido
    def load_data():
        try:
            url_base = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVMBTwRCrEvDUddWeUaIIpdSiA27cuPhHeArqAa_I3b_E8Fa_43lKg5hhSh2StAQddZQIXFFlM-zn-/pub?output=csv"
            url_planilha = f"{url_base}&t={int(time.time())}" # Anti-cache do Google
            
            if ".csv" in url_planilha.lower() or "output=csv" in url_planilha.lower():
                df = pd.read_csv(url_planilha, decimal=',', thousands='.')
            else:
                df = pd.read_excel(url_planilha)
            
            # --- CORREÇÃO DO FORMATO DE DATA: Removido o dayfirst=True ---
            df['Mês Referência'] = pd.to_datetime(df['Mês Referência'], errors='coerce')
            
            meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 
                        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
            df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
            df['Mes_Num'] = df['Mês Referência'].dt.month
            
            df['Quilometragem'] = to_float(df['Quilometragem'])
            df['Custo de manutenção'] = to_float(df['Custo de manutenção'])
            df['Custo de seguro'] = to_float(df.get('Custo de seguro', 0))
            df['Custo de Rastreador'] = to_float(df.get('Custo de Rastreador', 0))
            
            if 'Custo de combustível' in df.columns:
                df['Custo Combustível'] = to_float(df['Custo de combustível'])
            else:
                df['Custo Combustível'] = to_float(df.iloc[:, 3])

            df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int) if 'Ano' in df.columns else 2026
            
            if 'Centro de Custo' in df.columns: df['Centro de Custo'] = df['Centro de Custo'].astype(str).str.strip()
            if 'Base' in df.columns: df['Base'] = df['Base'].astype(str).str.strip()
            if 'Instituição' in df.columns: df['Instituição'] = df['Instituição'].astype(str).str.strip()
            
            if 'Modelo' in df.columns: 
                df['Modelo'] = df['Modelo'].astype(str).str.strip().replace(['0', '0.0', 'nan', 'NAN', 'None'], '-')
            else:
                df['Modelo'] = '-'
                
            if 'Motorista' in df.columns: 
                df['Motorista'] = df['Motorista'].astype(str).str.strip().replace(['0', '0.0', 'nan', 'NAN', 'None'], '-')
            else:
                df['Motorista'] = '-'
            
            if 'Placa' in df.columns: 
                df['Placa'] = df['Placa'].astype(str).str.strip().str.upper()
                df['Placa'] = df['Placa'].replace(['NAN', 'NONE'], '')
            
            return df
        except Exception as e:
            st.error(f"Erro ao carregar dados. Verifique se o link está correto: {e}")
            return pd.DataFrame()

    df = load_data()

    # VERBAS (Definidas apenas para 2026)
    ORCAMENTOS_MANUT_2026 = {"AMES": 987380.00, "IAV": 305434.00}
    ORCAMENTOS_COMB_2026 = {"AMES": 1000081.06, "IAV": 264450.00}
    ORCAMENTOS_SEGURO_2026 = {"AMES": 186682.00, "IAV": 115461.00}
    ORCAMENTOS_RASTREADOR_2026 = {"AMES": 0.00, "IAV": 10194.00} 

    if not df.empty:
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
        
        df_base_completa = df_temp_inst.copy() if cc_sel == "TODOS" else df_temp_inst[df_temp_inst[col_cc] == cc_sel]
        
        pattern_digitais = "VEÍCUL|VEICUL|ALUGAD|MOTO|KOMBI|TRICICLO|REBOQUE|SPRINTER|ÔNIBUS|ONIBUS|MICRO"
        
        mask_reais = ~df_base_completa["Placa"].astype(str).str.contains(pattern_digitais, case=False, na=True)
        df_base = df_base_completa[mask_reais]

        placas_disponiveis = get_ativos(df_base)
        opcoes_placas = [""] + sorted(placas_disponiveis)
        
        busca_placa = st.sidebar.selectbox(
            "🔍 Buscar Placa específica", 
            options=opcoes_placas, 
            index=0,
            help="Clique e comece a digitar a placa para pesquisar"
        ).upper().strip()
        
        lista_meses = df_ano.sort_values("Mes_Num")["Mes_Nome"].unique()
        mes_sel = st.sidebar.selectbox("Mês Competência", options=lista_meses, index=len(lista_meses)-1)

        df_apenas_comb = df_base[df_base["Placa"].str.startswith("COMBUSTÍVEL", na=False)]
        df_apenas_manut = df_base[~df_base["Placa"].str.startswith("COMBUSTÍVEL", na=False)]

        df_filtrado_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Nome"] == mes_sel]
        mes_num_atual = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
        df_acumulado_ate_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] <= mes_num_atual]
        df_anterior_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] == mes_num_atual - 1]

        # =======================================================
        # ABAS REORGANIZADAS
        # =======================================================
        tab1, tab2, tab3, tab4, tab5, tab8, tab6, tab9, tab7 = st.tabs([
            "📌 Visão Mensal", 
            "📈 Resumo Acumulado", 
            "⛽ Combustível", 
            "🛡️ Seguro/Rastreadores", 
            "📍 Raio-X da Base", 
            "🛣️ Mapa de KM", 
            "📋 Relação da Frota", 
            "📅 Veículos & IPVA",
            "📑 Detalhamento"
        ])

        with tab1:
            st.markdown(f"### 📊 Manutenção e Quilometragem — Desempenho Mensal | {mes_sel}/{ano_sel}")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                ativos_ano = len(get_ativos(df_base)) 
                draw_card("VEÍCULOS ATIVOS", fmt_br(ativos_ano), is_lower_better=False)
            
            with c2:
                km_m = df_filtrado_mes_manut['Quilometragem'].sum()
                km_a = df_anterior_manut['Quilometragem'].sum()
                trend_km = ((km_m-km_a)/km_a*100) if km_a>0 else 0
                draw_card("QUILOMETRAGEM MENSAL", fmt_br(km_m), trend=trend_km, is_lower_better=False)
            
            with c3:
                custo_m = df_filtrado_mes_manut['Custo de manutenção'].sum()
                custo_a = df_anterior_manut['Custo de manutenção'].sum()
                ativos_mes = len(get_ativos(df_filtrado_mes_manut)) 
                custo_medio = custo_m / ativos_mes if ativos_mes > 0 else 0
                trend_c = ((custo_m - custo_a) / custo_a * 100) if custo_a > 0 else 0
                draw_card("CUSTO MANUTENÇÃO MENSAL", fmt_br(custo_m, True), f"Média: {fmt_br(custo_medio, True)} /veículo ativo", trend=trend_c)

            if busca_placa:
                st.markdown("---")
                st.markdown(f"#### 🔍 Raio-X do Veículo: {busca_placa}")
                
                df_veiculo = df_base[df_base["Placa"] == busca_placa].sort_values("Mes_Num")
                
                if not df_veiculo.empty:
                    v_gasto_total = df_veiculo['Custo de manutenção'].sum()
                    v_km_total = df_veiculo['Quilometragem'].sum()
                    v_custo_km = v_gasto_total / v_km_total if v_km_total > 0 else 0
                    v_base = df_veiculo['Base'].iloc[-1]
                    
                    st.markdown(f"""
                    <div class="raiox-container">
                        <div class="raiox-item">
                            <div class="raiox-label">📍 Base atual</div>
                            <div class="raiox-value" style="font-size: 16px;">{v_base}</div>
                        </div>
                        <div class="raiox-item">
                            <div class="raiox-label">💰 Gasto Total Ano</div>
                            <div class="raiox-value" style="font-size: 16px;">{fmt_br(v_gasto_total, True)}</div>
                        </div>
                        <div class="raiox-item">
                            <div class="raiox-label">🛣️ KM Total Ano</div>
                            <div class="raiox-value" style="font-size: 16px;">{fmt_br(v_km_total)}</div>
                        </div>
                        <div class="raiox-item">
                            <div class="raiox-label">📊 Custo por KM</div>
                            <div class="raiox-value" style="font-size: 16px;">{fmt_br(v_custo_km, True)}/km</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    fig_raiox = px.line(df_veiculo, x='Mes_Nome', y='Custo de manutenção', markers=True, title="Histórico de Gastos (Manutenção)")
                    fig_raiox.update_traces(line_color='#0288D1', marker=dict(size=10, color='#1A237E'))
                    fig_raiox.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=0))
                    st.plotly_chart(fig_raiox, use_container_width=True)
                else:
                    st.warning("Nenhum dado financeiro ou de KM encontrado para esta Placa no período.")
                st.markdown("---")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            g1, g2 = st.columns(2)
            
            mask_veiculos_reais = (
                (~df_filtrado_mes_manut["Placa"].astype(str).str.contains("COMBUS|SEGUR|FINANC|CONSÓRC|RASTR|LOGIST|MANUT|MENSAL|TAXA", case=False, na=True)) &
                (df_filtrado_mes_manut["Placa"].astype(str).str.strip() != "") &
                (df_filtrado_mes_manut["Placa"].astype(str).str.upper() != "NAN") &
                (df_filtrado_mes_manut["Placa"].astype(str).str.strip() != "0")
            )
            df_top10 = df_filtrado_mes_manut[mask_veiculos_reais]

            with g1:
                st.markdown('<div class="chart-title">Top 10 veículos | Maior Quilometragem</div>', unsafe_allow_html=True)
                top10_km = df_top10[df_top10['Quilometragem'] > 0].nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
                
                if not top10_km.empty:
                    top10_km['Placa_Base'] = "<b>" + top10_km['Placa'] + "</b><br><span style='font-size:9.5px; color:#888888; font-weight:normal;'>" + top10_km['Base'] + "</span>"
                    fig_km = px.bar(top10_km, x='Quilometragem', y='Placa_Base', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
                    fig_km.update_traces(texttemplate='<b>%{text:,.0f}</b>', textposition='outside', textfont=ESTILO_TEXTO, cliponaxis=False)
                    max_km = top10_km['Quilometragem'].max() if not top10_km.empty else 1
                    fig_km.update_layout(height=450, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(r=150, l=10, t=10, b=10), xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_km * 1.4]), yaxis=dict(automargin=True, tickfont=dict(size=13, color='#333333', family="Arial, sans-serif"), title=""))
                    st.plotly_chart(fig_km, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("Nenhum dado para exibir neste mês.")
                
            with g2:
                st.markdown('<div class="chart-title">Top 10 veículos | Maior Custo de Manutenção</div>', unsafe_allow_html=True)
                top10_custo = df_top10[df_top10['Custo de manutenção'] > 0].nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
                
                if not top10_custo.empty and top10_custo['Custo de manutenção'].sum() > 0:
                    top10_custo['Placa_Base'] = "<b>" + top10_custo['Placa'] + "</b><br><span style='font-size:9.5px; color:#888888; font-weight:normal;'>" + top10_custo['Base'] + "</span>"
                    fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa_Base', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#F57C00'])
                    fig_custo.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO, cliponaxis=False)
                    max_c = top10_custo['Custo de manutenção'].max() if not top10_custo.empty else 1
                    fig_custo.update_layout(height=450, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(r=150, l=10, t=10, b=10), xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_c * 1.4]), yaxis=dict(automargin=True, tickfont=dict(size=13, color='#333333', family="Arial, sans-serif"), title=""))
                    st.plotly_chart(fig_custo, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("Nenhum custo lançado neste mês.")

        with tab2:
            st.markdown(f"### 📈 Manutenção e Quilometragem — Desempenho Acumulado | {ano_sel}")
            
            ca1, ca2, ca3 = st.columns(3)
            with ca1:
                gasto_total_acum_manut = df_acumulado_ate_mes_manut["Custo de manutenção"].sum()
                
                if ano_sel == 2026:
                    orc_total_manut = sum(ORCAMENTOS_MANUT_2026.get(inst, 0) for inst in inst_ativas)
                    saldo_manut = orc_total_manut - gasto_total_acum_manut
                    perc_manut = (gasto_total_acum_manut / orc_total_manut * 100) if orc_total_manut > 0 else 0
                    sub_manut = f"Orçamento Anual: <b>{fmt_br(orc_total_manut, True)}</b>"
                    prog_text_manut = f"{perc_manut:.1f}% &middot; Saldo {fmt_br(saldo_manut, True)}"
                    draw_card("EXECUÇÃO MANUT. (ACUMULADO)", fmt_br(gasto_total_acum_manut, True), sub_manut, progress=perc_manut, progress_text=prog_text_manut)
                else:
                    sub_manut = "Orçamento Anual: <b>A definir</b>"
                    draw_card("CUSTO DE MANUT. (ACUMULADO)", fmt_br(gasto_total_acum_manut, True), sub_manut)
                
            with ca2:
                km_acumulado = df_acumulado_ate_mes_manut['Quilometragem'].sum()
                sub_km = f"Total rodado em {ano_sel} até {mes_sel}"
                draw_card("QUILOMETRAGEM ACUMULADA", fmt_br(km_acumulado), subtext=sub_km, is_lower_better=False)
            
            st.markdown("---")
            
            st.markdown('<div class="chart-title">Evolução Mensal do Custo de Manutenção</div>', unsafe_allow_html=True)
            evol_inst = df_acumulado_ate_mes_manut.groupby(['Mes_Num', 'Mes_Nome', 'Instituição'])['Custo de manutenção'].sum().reset_index().sort_values('Mes_Num')
            
            if not evol_inst.empty:
                fig_evol = px.bar(evol_inst, x='Mes_Nome', y='Custo de manutenção', color='Instituição', 
                                  barmode='group', text='Custo de manutenção',
                                  color_discrete_map={"AMES": "#0288D1", "IAV": "#F57C00"})
                
                fig_evol.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO)
                max_c_evol = evol_inst['Custo de manutenção'].max() if not evol_inst.empty else 1
                
                fig_evol.update_layout(height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                       margin=dict(r=10, l=10, t=20, b=10),
                                       yaxis=dict(title="Custo no Mês (R$)", showgrid=True, gridcolor='#E0E0E0', range=[0, max_c_evol * 1.25]),
                                       xaxis=dict(title=""),
                                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""),
                                       separators=',.')
                st.plotly_chart(fig_evol, use_container_width=True, config={'displayModeBar': False})

            st.markdown("---")
            st.markdown('<div class="chart-title">Top 10 bases | Maior Custo de Manutenção Acumulado</div>', unsafe_allow_html=True)
            custo_base_acum = df_acumulado_ate_mes_manut.groupby('Base')['Custo de manutenção'].sum().reset_index().nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            
            if not custo_base_acum.empty and custo_base_acum['Custo de manutenção'].sum() > 0:
                fig_base_acum = px.bar(custo_base_acum, x='Custo de manutenção', y='Base', orientation='h', text='Custo de manutenção', color='Custo de manutenção', color_continuous_scale='Blues')
                fig_base_acum.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO, cliponaxis=False)
                max_cb = custo_base_acum['Custo de manutenção'].max()
                
                fig_base_acum.update_layout(height=450, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(r=150, l=10, t=10, b=10), showlegend=False, coloraxis_showscale=False, xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_cb * 1.4]), yaxis=dict(tickfont=dict(size=12, color='#333333', family="Arial, sans-serif")))
                st.plotly_chart(fig_base_acum, use_container_width=True, config={'displayModeBar': False})

        with tab3:
            st.markdown(f"### ⛽ Gestão de Combustível | {ano_sel}")
            df_comb_mes = df_apenas_comb[df_apenas_comb["Mes_Nome"] == mes_sel]
            df_comb_acum = df_apenas_comb[df_apenas_comb["Mes_Num"] <= mes_num_atual]
            df_comb_anterior = df_apenas_comb[df_apenas_comb["Mes_Num"] == mes_num_atual - 1]

            k1, k2 = st.columns(2)
            with k1:
                gasto_m_comb = df_comb_mes["Custo Combustível"].sum()
                gasto_a_comb = df_comb_anterior["Custo Combustível"].sum()
                trend_comb = ((gasto_m_comb - gasto_a_comb) / gasto_a_comb * 100) if gasto_a_comb > 0 else 0
                sub_comb_m = f"Gasto exclusivo em {mes_sel}"
                draw_card("CUSTO COMBUSTÍVEL MENSAL", fmt_br(gasto_m_comb, True), sub_comb_m, trend=trend_comb)
                
            with k2:
                gasto_acum_comb = df_comb_acum["Custo Combustível"].sum()
                if ano_sel == 2026:
                    orc_total_comb = sum(ORCAMENTOS_COMB_2026.get(inst, 0) for inst in inst_ativas)
                    saldo_comb = orc_total_comb - gasto_acum_comb
                    perc_comb = (gasto_acum_comb / orc_total_comb * 100) if orc_total_comb > 0 else 0
                    sub_comb = f"Orçamento Anual: <b>{fmt_br(orc_total_comb, True)}</b>"
                    prog_text_comb = f"{perc_comb:.1f}% &middot; Saldo {fmt_br(saldo_comb, True)}"
                    draw_card("EXECUÇÃO COMBUSTÍVEL ANUAL", fmt_br(gasto_acum_comb, True), sub_comb, progress=perc_comb, progress_text=prog_text_comb)
                else:
                    sub_comb = "Orçamento Anual: <b>A definir</b>"
                    draw_card("CUSTO COMBUSTÍVEL (ACUMULADO)", fmt_br(gasto_acum_comb, True), sub_comb)
            
            st.markdown("---")
            
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.markdown(f'<div class="chart-title">Top 10 Bases | Custo de Combustível em {mes_sel}/{ano_sel}</div>', unsafe_allow_html=True)
                custo_comb_base_mes = df_comb_mes.groupby('Base')['Custo Combustível'].sum().reset_index().nlargest(10, 'Custo Combustível').sort_values('Custo Combustível', ascending=True)
                
                if not custo_comb_base_mes.empty and custo_comb_base_mes['Custo Combustível'].sum() > 0:
                    fig_comb_mes = px.bar(custo_comb_base_mes, x='Custo Combustível', y='Base', orientation='h', text='Custo Combustível', color_discrete_sequence=['#0288D1'])
                    fig_comb_mes.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO, cliponaxis=False)
                    max_cc_m = custo_comb_base_mes['Custo Combustível'].max()
                    fig_comb_mes.update_layout(height=450, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(r=150, l=10, t=10, b=10), xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_cc_m * 1.4]), yaxis=dict(tickfont=dict(size=12, color='#333333', family="Arial, sans-serif"), title=""), showlegend=False)
                    st.plotly_chart(fig_comb_mes, use_container_width=True, config={'displayModeBar': False})
            
            with col_g2:
                st.markdown(f'<div class="chart-title">Top 10 Bases | Custo de Combustível Acumulado em {ano_sel}</div>', unsafe_allow_html=True)
                custo_comb_base_acum = df_comb_acum.groupby('Base')['Custo Combustível'].sum().reset_index().nlargest(10, 'Custo Combustível').sort_values('Custo Combustível', ascending=True)
                
                if not custo_comb_base_acum.empty and custo_comb_base_acum['Custo Combustível'].sum() > 0:
                    fig_comb_acum = px.bar(custo_comb_base_acum, x='Custo Combustível', y='Base', orientation='h', text='Custo Combustível', color_discrete_sequence=['#F57C00'])
                    fig_comb_acum.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO, cliponaxis=False)
                    max_cc_a = custo_comb_base_acum['Custo Combustível'].max()
                    fig_comb_acum.update_layout(height=450, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(r=150, l=10, t=10, b=10), xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_cc_a * 1.4]), yaxis=dict(tickfont=dict(size=12, color='#333333', family="Arial, sans-serif"), title=""), showlegend=False)
                    st.plotly_chart(fig_comb_acum, use_container_width=True, config={'displayModeBar': False})

        with tab4:
            st.markdown(f"### 🛡️ Seguro/Rastreadores | {ano_sel}")
            df_fixos_acum = df_base[df_base["Mes_Num"] <= mes_num_atual]
            
            gasto_seguro = df_fixos_acum["Custo de seguro"].sum()
            gasto_rastreador = df_fixos_acum["Custo de Rastreador"].sum()
            
            cf1, cf2 = st.columns(2)
            
            with cf1:
                if ano_sel == 2026:
                    orc_seguro = sum(ORCAMENTOS_SEGURO_2026.get(inst, 0) for inst in inst_ativas)
                    saldo_seguro = orc_seguro - gasto_seguro
                    perc_seguro = (gasto_seguro / orc_seguro * 100) if orc_seguro > 0 else 0
                    sub_seguro = f"Orçamento Anual: <b>{fmt_br(orc_seguro, True)}</b>"
                    prog_text_seguro = f"{perc_seguro:.1f}% &middot; Saldo {fmt_br(saldo_seguro, True)}"
                    draw_card("EXECUÇÃO SEGURO DE VEÍCULOS", fmt_br(gasto_seguro, True), sub_seguro, progress=perc_seguro, progress_text=prog_text_seguro)
                else:
                    sub_seguro = "Orçamento Anual: <b>A definir</b>"
                    draw_card("CUSTO COM SEGURO", fmt_br(gasto_seguro, True), sub_seguro)

            with cf2:
                if ano_sel == 2026:
                    orc_rastreador = sum(ORCAMENTOS_RASTREADOR_2026.get(inst, 0) for inst in inst_ativas)
                    saldo_rastreador = orc_rastreador - gasto_rastreador
                    perc_rastreador = (gasto_rastreador / orc_rastreador * 100) if orc_rastreador > 0 else 0
                    sub_rastreador = f"Orçamento Anual: <b>{fmt_br(orc_rastreador, True)}</b>"
                    prog_text_rastreador = f"{perc_rastreador:.1f}% &middot; Saldo {fmt_br(saldo_rastreador, True)}"
                    draw_card("EXECUÇÃO RASTREADOR", fmt_br(gasto_rastreador, True), sub_rastreador, progress=perc_rastreador, progress_text=prog_text_rastreador)
                else:
                    sub_rastreador = "Orçamento Anual: <b>A definir</b>"
                    draw_card("CUSTO COM RASTREADOR", fmt_br(gasto_rastreador, True), sub_rastreador)
                
            st.markdown("---")
            st.markdown('<div class="chart-title">Evolução Mensal de Seguro e Rastreadores</div>', unsafe_allow_html=True)
            
            evol_fixos = df_fixos_acum.groupby(['Mes_Nome', 'Mes_Num'])[['Custo de seguro', 'Custo de Rastreador']].sum().reset_index().sort_values('Mes_Num')
            evol_fixos_melted = evol_fixos.melt(id_vars=['Mes_Nome', 'Mes_Num'], 
                                                value_vars=['Custo de seguro', 'Custo de Rastreador'], 
                                                var_name='Tipo Despesa', 
                                                value_name='Custo')
            
            evol_fixos_melted['Tipo Despesa'] = evol_fixos_melted['Tipo Despesa'].map({'Custo de seguro': 'Seguro', 'Custo de Rastreador': 'Rastreador'})
            
            if evol_fixos_melted['Custo'].sum() > 0:
                fig_fixos = px.bar(evol_fixos_melted, x='Mes_Nome', y='Custo', color='Tipo Despesa', barmode='group', color_discrete_map={"Seguro": "#1A237E", "Rastreador": "#0288D1"})
                
                max_f = evol_fixos_melted['Custo'].max()
                fig_fixos.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                        yaxis=dict(title="Custo (R$)", showgrid=True, gridcolor='#E0E0E0', range=[0, max_f * 1.3]), xaxis_title="",
                                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""),
                                        separators=',.')
                
                fig_fixos.update_traces(texttemplate='<b>R$ %{y:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO)
                st.plotly_chart(fig_fixos, use_container_width=True)
            else:
                st.info("Nenhum custo de Seguro ou Rastreador lançado nestes meses.")

        with tab5:
            st.markdown(f"### 📍 Raio-X da Base | {ano_sel}")
            
            df_acum_geral = df_base[df_base['Mes_Num'] <= mes_num_atual]
            
            df_manut_acum_geral = df_acum_geral[~df_acum_geral["Placa"].str.startswith("COMBUSTÍVEL", na=False)]
            manut_por_base = df_manut_acum_geral.groupby(col_cc)['Custo de manutenção'].sum().reset_index()
            
            df_comb_acum_geral = df_acum_geral[df_acum_geral["Placa"].str.startswith("COMBUSTÍVEL", na=False)]
            comb_por_base = df_comb_acum_geral.groupby(col_cc)['Custo Combustível'].sum().reset_index()
            
            mask_validas = (
                (df_manut_acum_geral["Placa"].astype(str).str.strip() != "") &
                (df_manut_acum_geral["Placa"].astype(str).str.upper() != "NAN") &
                (df_manut_acum_geral["Placa"].astype(str).str.strip() != "0")
            )
            veic_por_base = df_manut_acum_geral[mask_validas].groupby(col_cc)['Placa'].nunique().reset_index().rename(columns={'Placa': 'Qtd Veículos'})
            
            df_resumo_bases = pd.merge(veic_por_base, manut_por_base, on=col_cc, how='outer')
            df_resumo_bases = pd.merge(df_resumo_bases, comb_por_base, on=col_cc, how='outer').fillna(0)
            df_resumo_bases['Custo Total Acumulado'] = df_resumo_bases['Custo de manutenção'] + df_resumo_bases['Custo Combustível']
            
            df_resumo_bases['Custo de manutenção'] = df_resumo_bases['Custo de manutenção'].round(2)
            df_resumo_bases['Custo Combustível'] = df_resumo_bases['Custo Combustível'].round(2)
            df_resumo_bases['Custo Total Acumulado'] = df_resumo_bases['Custo Total Acumulado'].round(2)
            
            df_resumo_bases.rename(columns={
                col_cc: 'Base / Centro de Custo',
                'Custo de manutenção': f'Manutenção Acumulada (Até {mes_sel})',
                'Custo Combustível': f'Combustível Acumulado (Até {mes_sel})',
                'Custo Total Acumulado': f'Custo Total Acumulado (Até {mes_sel})'
            }, inplace=True)
            
            col_sel, col_btn = st.columns([2, 1])
            with col_sel:
                base_raiox = st.selectbox("🔍 Selecione a Base para análise detalhada:", sorted(df_base[col_cc].dropna().unique()))
            
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                csv_resumo = df_resumo_bases.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
                st.download_button(
                    label="📥 Baixar Resumo de Todas as Bases",
                    data=csv_resumo,
                    file_name=f"Resumo_Custos_por_Base_{mes_sel}_{ano_sel}.csv",
                    mime="text/csv",
                    key="btn_download_resumo_bases"
                )
            
            if base_raiox:
                df_rx_base = df_base[df_base[col_cc] == base_raiox]
                df_rx_mes = df_rx_base[df_rx_base['Mes_Nome'] == mes_sel]
                df_rx_acum = df_rx_base[df_rx_base['Mes_Num'] <= mes_num_atual]
                
                km_mes = df_rx_mes['Quilometragem'].sum()
                km_acum = df_rx_acum['Quilometragem'].sum()
                
                manut_mes = df_rx_mes['Custo de manutenção'].sum()
                manut_acum = df_rx_acum['Custo de manutenção'].sum()
                
                comb_mes = df_rx_mes['Custo Combustível'].sum()
                comb_acum = df_rx_acum['Custo Combustível'].sum()
                
                total_mes = manut_mes + comb_mes
                total_acum = manut_acum + comb_acum
                
                cpk_mes = total_mes / km_mes if km_mes > 0 else 0
                cpk_acum = total_acum / km_acum if km_acum > 0 else 0
                
                df_rx_manut_acum = df_rx_acum[~df_rx_acum["Placa"].str.startswith("COMBUSTÍVEL", na=False)]
                qtd_veiculos_base = df_rx_manut_acum.loc[
                    (df_rx_manut_acum["Placa"].astype(str).str.strip() != "") &
                    (df_rx_manut_acum["Placa"].astype(str).str.upper() != "NAN") &
                    (df_rx_manut_acum["Placa"].astype(str).str.strip() != "0"),
                    'Placa'
                ].nunique()
                
                st.markdown(f"""
                <div class="raiox-container">
                    <div class="raiox-item">
                        <div class="raiox-label">🚘 Veículos</div>
                        <div class="raiox-value">{qtd_veiculos_base}</div>
                        <div style="font-size:13px; color:#546E7A; margin-top:8px; font-weight: 600;">Ativos na Base</div>
                    </div>
                    <div class="raiox-item">
                        <div class="raiox-label">🛣️ KM Rodado (Mês)</div>
                        <div class="raiox-value">{fmt_br(km_mes)}</div>
                        <div style="font-size:13px; color:#546E7A; margin-top:8px; font-weight: 600;">Acumulado: {fmt_br(km_acum)}</div>
                    </div>
                    <div class="raiox-item">
                        <div class="raiox-label">🔧 Manutenção (Mês)</div>
                        <div class="raiox-value">{fmt_br(manut_mes, True)}</div>
                        <div style="font-size:13px; color:#546E7A; margin-top:8px; font-weight: 600;">Acumulado: {fmt_br(manut_acum, True)}</div>
                    </div>
                    <div class="raiox-item">
                        <div class="raiox-label">⛽ Combustível (Mês)</div>
                        <div class="raiox-value">{fmt_br(comb_mes, True)}</div>
                        <div style="font-size:13px; color:#546E7A; margin-top:8px; font-weight: 600;">Acumulado: {fmt_br(comb_acum, True)}</div>
                    </div>
                    <div class="raiox-item">
                        <div class="raiox-label">💰 Custo Total (Mês)</div>
                        <div class="raiox-value">{fmt_br(total_mes, True)}</div>
                        <div style="font-size:13px; color:#546E7A; margin-top:8px; font-weight: 600;">Acumulado: {fmt_br(total_acum, True)}</div>
                    </div>
                    <div class="raiox-item">
                        <div class="raiox-label">📊 Custo por KM (Mês)</div>
                        <div class="raiox-value">{fmt_br(cpk_mes, True)}</div>
                        <div style="font-size:13px; color:#546E7A; margin-top:8px; font-weight: 600;">Acumulado: {fmt_br(cpk_acum, True)}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # ---------------------------------------------------------
                # INÍCIO DA NOVA TABELA PARA O GESTOR DA BASE
                # ---------------------------------------------------------
                st.markdown(f"#### 🚘 Detalhamento para o Gestor | {base_raiox}")
                
                padrao_exclusao_rx = "COMBUS|SEGUR|FINANC|CONSÓRC|RASTR|LOGIST|MANUT|MENSAL|TAXA|VEÍCUL|VEICUL|ALUGAD|MOTO|KOMBI|TRICICLO|REBOQUE|SPRINTER|ÔNIBUS|ONIBUS|MICRO"
                
                df_veic_acum = df_rx_acum[~df_rx_acum["Placa"].astype(str).str.contains(padrao_exclusao_rx, case=False, na=True)]
                df_veic_mes = df_rx_mes[~df_rx_mes["Placa"].astype(str).str.contains(padrao_exclusao_rx, case=False, na=True)]
                
                resumo_mes = df_veic_mes.groupby("Placa").agg({
                    "Quilometragem": "sum",
                    "Custo de manutenção": "sum"
                }).rename(columns={"Quilometragem": f"KM ({mes_sel})", "Custo de manutenção": f"Custo Manutenção ({mes_sel})"})
                
                resumo_acum = df_veic_acum.groupby("Placa").agg({
                    "Quilometragem": "sum",
                    "Custo de manutenção": "sum"
                }).rename(columns={"Quilometragem": "KM (Acumulado)", "Custo de manutenção": "Custo Manutenção (Acumulado)"})
                
                df_placas = pd.merge(resumo_mes, resumo_acum, on="Placa", how="right").fillna(0).reset_index()
                
                df_placas = df_placas[
                    (df_placas["Placa"].astype(str).str.strip() != "") &
                    (df_placas["Placa"].astype(str).str.upper() != "NAN") &
                    (df_placas["Placa"].astype(str).str.strip() != "0")
                ]
                
                df_placas = df_placas.sort_values("Custo Manutenção (Acumulado)", ascending=False)
                
                # ADICIONA A LINHA DE COMBUSTÍVEL NO FINAL DA TABELA
                comb_mes_val = df_rx_mes[df_rx_mes["Placa"].str.startswith("COMBUSTÍVEL", na=False)]['Custo Combustível'].sum()
                comb_acum_val = df_rx_acum[df_rx_acum["Placa"].str.startswith("COMBUSTÍVEL", na=False)]['Custo Combustível'].sum()
                
                if comb_mes_val > 0 or comb_acum_val > 0:
                    linha_combustivel = pd.DataFrame([{
                        "Placa": "⛽ COMBUSTÍVEL DA BASE",
                        f"KM ({mes_sel})": 0,
                        f"Custo Manutenção ({mes_sel})": comb_mes_val,
                        "KM (Acumulado)": 0,
                        "Custo Manutenção (Acumulado)": comb_acum_val
                    }])
                    df_placas = pd.concat([df_placas, linha_combustivel], ignore_index=True)
                
                # Botão de Download que vai conter a linha do combustível
                col_btn_placas, col_espaco = st.columns([1, 2])
                with col_btn_placas:
                    csv_placas = df_placas.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
                    st.download_button(
                        label=f"📥 Baixar Relatório do Gestor (Placas + Combustível)",
                        data=csv_placas,
                        file_name=f"Relatorio_Gestor_{base_raiox.replace(' ', '_')}_{mes_sel}_{ano_sel}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Pinta a linha do combustível de laranja na tela para dar destaque visual
                def highlight_fuel(row):
                    if "⛽" in str(row['Placa']):
                        return ['background-color: #FFF3E0; font-weight: bold; color: #E65100'] * len(row)
                    return [''] * len(row)
                
                df_styled_placas = df_placas.style.apply(highlight_fuel, axis=1)
                
                st.dataframe(
                    df_styled_placas, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Placa": st.column_config.TextColumn("Placa", width="medium"),
                        f"KM ({mes_sel})": st.column_config.NumberColumn(f"KM ({mes_sel})", format="%.0f"),
                        f"Custo Manutenção ({mes_sel})": st.column_config.NumberColumn(f"Custo Manutenção ({mes_sel})", format="R$ %.2f"),
                        "KM (Acumulado)": st.column_config.NumberColumn("KM (Acumulado)", format="%.0f"),
                        "Custo Manutenção (Acumulado)": st.column_config.NumberColumn("Custo Manutenção (Acumulado)", format="R$ %.2f"),
                    }
                )
                # ---------------------------------------------------------
                # FIM DO NOVO CÓDIGO DA TABELA DE PLACAS
                # ---------------------------------------------------------

        with tab8:
            st.markdown(f"### 🛣️ Mapa de Quilometragem | {ano_sel}")
            st.markdown("Visão em matriz da quilometragem rodada por veículo e por base, com totais consolidados ao longo dos meses.")
            
            # Utiliza df_base_completa e remove placas que não são veículos
            mask_km = (
                (~df_base_completa["Placa"].astype(str).str.contains(pattern_digitais, case=False, na=True)) &
                (df_base_completa["Placa"].astype(str).str.strip() != "") &
                (df_base_completa["Placa"].astype(str).str.upper() != "NAN") &
                (df_base_completa["Placa"].astype(str).str.strip() != "0")
            )
            df_km_matrix = df_base_completa[mask_km]
            
            if not df_km_matrix.empty:
                # Cria a tabela dinâmica (Pivot Table)
                pt_km = pd.pivot_table(
                    df_km_matrix,
                    values='Quilometragem',
                    index=['Instituição', col_cc, 'Placa'],
                    columns='Mes_Num',
                    aggfunc='sum',
                    fill_value=0
                ).reset_index()
                
                # Mapeia números dos meses para nomes curtos
                meses_map = {1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN', 
                             7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'}
                
                meses_presentes = sorted([c for c in pt_km.columns if isinstance(c, int)])
                nomes_meses_presentes = [meses_map.get(m, str(m)) for m in meses_presentes]
                
                # Renomeia colunas para os nomes dos meses
                renames = {m: meses_map.get(m, str(m)) for m in meses_presentes}
                pt_km.rename(columns=renames, inplace=True)
                
                # Adiciona coluna de TOTAL
                pt_km['TOTAL'] = pt_km[nomes_meses_presentes].sum(axis=1)
                pt_km = pt_km.sort_values(['Instituição', col_cc, 'Placa'])
                
                # ==========================================
                # Construção da Tabela com Subtotais
                # ==========================================
                linhas_subtotal = []
                for inst in pt_km['Instituição'].unique():
                    df_inst = pt_km[pt_km['Instituição'] == inst]
                    for base in df_inst[col_cc].unique():
                        df_b = df_inst[df_inst[col_cc] == base]
                        
                        # Linhas normais da Base
                        for _, row in df_b.iterrows():
                            linhas_subtotal.append(row.to_dict())
                        
                        # Linha de Subtotal da Base
                        subtotal_dict = {'Instituição': inst, col_cc: base, 'Placa': 'Subtotal'}
                        for mes in nomes_meses_presentes:
                            subtotal_dict[mes] = df_b[mes].sum()
                        subtotal_dict['TOTAL'] = df_b['TOTAL'].sum()
                        linhas_subtotal.append(subtotal_dict)
                    
                    # Linha de Total da Instituição
                    total_inst_dict = {'Instituição': inst, col_cc: '', 'Placa': f'TOTAL {inst}'}
                    for mes in nomes_meses_presentes:
                        total_inst_dict[mes] = df_inst[mes].sum()
                    total_inst_dict['TOTAL'] = df_inst['TOTAL'].sum()
                    linhas_subtotal.append(total_inst_dict)
                
                # Linha de Total Geral (Final da Planilha)
                total_geral_dict = {'Instituição': '', col_cc: '', 'Placa': 'TOTAL GERAL'}
                for mes in nomes_meses_presentes:
                    total_geral_dict[mes] = pt_km[mes].sum()
                total_geral_dict['TOTAL'] = pt_km['TOTAL'].sum()
                linhas_subtotal.append(total_geral_dict)
                
                df_km_subtotals = pd.DataFrame(linhas_subtotal)
                
                # Função para estilizar visualmente a tabela na tela do App
                def highlight_subtotals(row):
                    placa = str(row['Placa']).upper()
                    if 'SUBTOTAL' in placa:
                        return ['background-color: #E3F2FD; font-weight: bold; color: #1A237E'] * len(row)
                    elif 'TOTAL' in placa:
                        return ['background-color: #1A237E; color: white; font-weight: bold'] * len(row)
                    return [''] * len(row)
                
                # Função de formatação para retirar casas decimais e adicionar ponto de milhar
                def format_br_int(val):
                    try: return f"{int(val):,.0f}".replace(",", ".")
                    except: return "0"
                
                # Aplica as formatações e colorações
                format_dict = {c: format_br_int for c in nomes_meses_presentes + ['TOTAL']}
                df_styled = df_km_subtotals.style.apply(highlight_subtotals, axis=1).format(format_dict)
                
                # Exibe botão de Download e Tabela
                col_btn_km1, col_btn_km2 = st.columns([2, 1])
                with col_btn_km2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    csv_km = df_km_subtotals.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
                    st.download_button(
                        label="📥 Baixar Mapa de KM em Excel/CSV",
                        data=csv_km,
                        file_name=f"Mapa_Quilometragem_Completo_{inst_sel}_{ano_sel}.csv",
                        mime="text/csv",
                        key="btn_download_km"
                    )
                
                st.dataframe(df_styled, use_container_width=True, height=600, hide_index=True)
                
            else:
                st.warning("Nenhum dado de quilometragem encontrado para esta seleção.")

        with tab6:
            st.markdown(f"### 📋 Relação da Frota | {ano_sel}")
            st.markdown("Lista atualizada da frota genérica vinculada às bases, segmentada por categoria em uma única planilha.")
            
            # Puxamos as PLACAS DIGITAIS
            pattern_digitais = "VEÍCUL|VEICUL|ALUGAD|MOTO|KOMBI|TRICICLO|REBOQUE|SPRINTER|ÔNIBUS|ONIBUS|MICRO"
            mask_frota_aba = df_base_completa["Placa"].astype(str).str.contains(pattern_digitais, case=False, na=False)
            
            df_frota = df_base_completa[mask_frota_aba].copy()
            
            if not df_frota.empty:
                df_frota_unica = df_frota.sort_values("Mes_Num", ascending=False).drop_duplicates(subset=["Placa"])
                
                # Regra de Classificação baseada no NOME da placa digital
                def classificar_frota(placa):
                    texto = str(placa).upper()
                    if 'ALUGAD' in texto: return 'Alugados'
                    elif 'MOTO' in texto: return 'Moto'
                    elif 'TRICICLO' in texto: return 'Triciclo'
                    elif 'REBOQUE' in texto: return 'Reboque'
                    elif 'SPRINTER' in texto: return 'Sprinter'
                    elif 'ÔNIBUS' in texto or 'ONIBUS' in texto or 'MICRO' in texto: return 'Ônibus/Micro'
                    elif 'KOMBI' in texto: return 'Kombi'
                    else: return 'Veículos Próprios'
                    
                df_frota_unica['Categoria'] = df_frota_unica['Placa'].apply(classificar_frota)
                
                ordem_cat = {"Veículos Próprios": 1, "Alugados": 2, "Moto": 3, "Triciclo": 4, "Reboque": 5, "Sprinter": 6, "Kombi": 7, "Ônibus/Micro": 8}
                df_frota_unica['Ordem_Cat'] = df_frota_unica['Categoria'].map(lambda x: ordem_cat.get(x, 99))
                
                # Ordenação Inicial
                df_frota_unica = df_frota_unica.sort_values(['Instituição', 'Ordem_Cat', col_cc, 'Placa'])
                
                # ==========================================
                # Construção da Tabela com Linhas Divisórias (Cabeçalhos)
                # ==========================================
                linhas_segmentadas = []
                
                for inst in df_frota_unica['Instituição'].unique():
                    df_i = df_frota_unica[df_frota_unica['Instituição'] == inst]
                    
                    for cat in df_i['Categoria'].unique():
                        # Adiciona a linha de Cabeçalho da Categoria
                        linhas_segmentadas.append({
                            'Placa': f"🔸 {str(cat).upper()}",
                            'Instituição': inst,
                            col_cc: "",
                            'Modelo': "",
                            'Motorista': ""
                        })
                        
                        # Adiciona os veículos referentes àquela categoria
                        df_cat = df_i[df_i['Categoria'] == cat]
                        for _, row in df_cat.iterrows():
                            linhas_segmentadas.append({
                                'Placa': row['Placa'],
                                'Instituição': row['Instituição'],
                                col_cc: row.get(col_cc, ""),
                                'Modelo': row.get('Modelo', ""),
                                'Motorista': row.get('Motorista', "")
                            })
                            
                df_apresentacao = pd.DataFrame(linhas_segmentadas)
                
                # Função de estilo para colorir as linhas de separação
                def highlight_category(row):
                    placa_val = str(row['Placa'])
                    if placa_val.startswith('🔸'):
                        # Linha de cabeçalho: Fundo Azul Escuro com letras brancas e negrito
                        return ['background-color: #1A237E; color: white; font-weight: bold'] * len(row)
                    return [''] * len(row)
                
                df_styled = df_apresentacao.style.apply(highlight_category, axis=1)
                
                # Botão de Download da tabela única e segmentada
                csv_relacao = df_apresentacao.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
                st.download_button(
                    label="📥 Baixar Relação da Frota Segmentada (Excel/CSV)",
                    data=csv_relacao,
                    file_name=f"Relacao_Frota_Segmentada_{inst_sel}_{ano_sel}.csv",
                    mime="text/csv",
                    key="btn_download_relacao"
                )
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Mostra a tabela única na tela
                st.dataframe(df_styled, use_container_width=True, hide_index=True)
                st.info(f"Total de registros na frota (excluindo cabeçalhos): **{len(df_frota_unica)}**")
            else:
                st.warning("Nenhum veículo encontrado para exibir nesta aba.")

        with tab9:
            st.markdown(f"### 📅 Estimativas de IPVA e Dados de Veículos")
            st.markdown("Base de consulta atualizada automaticamente via Google Sheets.")
            
            df_ipva = load_ipva_data()
            
            if "Aviso" in df_ipva.columns:
                st.warning(df_ipva["Aviso"].iloc[0])
            elif not df_ipva.empty:
                
                # Filtros Rápidos na tela do IPVA
                col_filtros1, col_filtros2 = st.columns(2)
                with col_filtros1:
                    if 'Instituição' in df_ipva.columns:
                        inst_ipva = st.selectbox("Filtrar por Instituição:", ["TODAS"] + sorted(df_ipva['Instituição'].dropna().unique()), key='ipva_inst')
                    else:
                        inst_ipva = "TODAS"
                        
                with col_filtros2:
                    if 'Ano base' in df_ipva.columns:
                        ano_ipva = st.selectbox("Filtrar por Ano Base (IPVA):", ["TODOS"] + sorted(df_ipva['Ano base'].dropna().unique(), reverse=True), key='ipva_ano')
                    else:
                        ano_ipva = "TODOS"
                
                # Aplica os filtros
                df_ipva_filtrado = df_ipva.copy()
                if inst_ipva != "TODAS":
                    df_ipva_filtrado = df_ipva_filtrado[df_ipva_filtrado['Instituição'] == inst_ipva]
                if ano_ipva != "TODOS":
                    df_ipva_filtrado = df_ipva_filtrado[df_ipva_filtrado['Ano base'] == ano_ipva]
                
                # Configura a visualização das colunas
                config_cols_ipva = {}
                if 'Ipva estimado' in df_ipva_filtrado.columns:
                    config_cols_ipva['Ipva estimado'] = st.column_config.NumberColumn("Ipva estimado", format="R$ %.2f")
                if 'Ano base' in df_ipva_filtrado.columns:
                    config_cols_ipva['Ano base'] = st.column_config.NumberColumn("Ano base", format="%d")
                if 'Ano do veículo' in df_ipva_filtrado.columns:
                    config_cols_ipva['Ano do veículo'] = st.column_config.NumberColumn("Ano do veículo", format="%d")
                
                # Exibe totais na tela
                total_ipva = df_ipva_filtrado['Ipva estimado'].sum() if 'Ipva estimado' in df_ipva_filtrado.columns else 0
                st.markdown(f"**Total de veículos listados:** {len(df_ipva_filtrado)} | **Valor Total Estimado:** {fmt_br(total_ipva, True)}")
                
                # Botão de download
                col_btn, col_esp = st.columns([1, 2])
                with col_btn:
                    csv_ipva = df_ipva_filtrado.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
                    st.download_button(
                        label="📥 Baixar Tabela Filtrada de IPVA",
                        data=csv_ipva,
                        file_name=f"Base_IPVA_Frota_{inst_ipva}_{ano_ipva}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Mostra a tabela bonita
                st.dataframe(df_ipva_filtrado, use_container_width=True, hide_index=True, column_config=config_cols_ipva)
            else:
                st.warning("Nenhum dado de IPVA encontrado ou erro de carregamento.")

        with tab7:
            st.markdown("### 📑 Detalhamento dos Dados")
            
            df_download = df_base_completa.drop(columns=['Mes_Num'])
            
            csv_data = df_download.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
            st.download_button(
                label="📥 Baixar Relatório Completo (Excel/CSV)",
                data=csv_data,
                file_name=f"Relatorio_Frotas_{inst_sel}_{mes_sel}_{ano_sel}.csv",
                mime="text/csv"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            colunas_moeda = [c for c in ['Custo de manutenção', 'Custo Combustível', 'Custo de seguro', 'Custo de Rastreador'] if c in df_download.columns]
            config_cols = {col: st.column_config.NumberColumn(col, format="R$ %.2f") for col in colunas_moeda}
            
            if 'Quilometragem' in df_download.columns:
                config_cols['Quilometragem'] = st.column_config.NumberColumn('Quilometragem', format="%.0f")
                
            st.dataframe(df_download, use_container_width=True, hide_index=True, column_config=config_cols)

    else:
        st.warning("Verifique o link do arquivo da planilha online ou certifique-se de que os dados foram publicados.")
