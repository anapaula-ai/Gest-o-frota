import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # Adicionado para o gráfico de rosca
import time  # Adicionado para forçar atualização do cache do Google
import re

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Logística", layout="wide")

# ==========================================
# 2. TELA DE LOGIN E SEGURANÇA
# ==========================================
# A senha agora é puxada de forma segura das configurações (secrets)
try:
    SENHA_ACESSO = st.secrets["senha_acesso"]
except KeyError:
    st.error("⚠️ Erro de configuração: A senha não foi encontrada nos secrets.")
    st.info("Lembre-se de criar o arquivo `.streamlit/secrets.toml` localmente ou configurar nos Secrets do painel Streamlit Cloud.")
    st.stop()

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
        position: relative;
        overflow: hidden;
        background: linear-gradient(180deg, #FFFFFF 0%, #FCFDFF 100%) !important;
        padding: 21px 20px 18px 20px;
        border-radius: 14px;
        border: 1px solid #D7E0EA;
        box-shadow: 0 5px 16px rgba(26, 35, 126, 0.07);
        min-height: 185px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        margin-bottom: 10px;
    }

    .metric-container::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: #1A237E;
    }

    .metric-label {
        color: #60758A !important;
        font-size: 10.5px;
        letter-spacing: .35px;
        font-weight: 800;
        text-transform: uppercase;
        min-height: 34px;
        display: flex;
        align-items: center;
    }

    .metric-value {
        color: #14206F !important;
        font-size: 25px;
        font-weight: 800;
        min-height: 42px;
        display: flex;
        align-items: center;
        letter-spacing: -.25px;
    }

    .metric-subtext {
        color: #455A64 !important;
        font-size: 12.5px;
        font-weight: 500;
        min-height: 31px;
        display: block;
        line-height: 1.45;
        margin-top: 7px;
        padding-top: 8px;
        border-top: 1px solid #EEF2F6;
    }

    .trend-container {
        min-height: 18px;
        display: flex;
        align-items: center;
        margin-top: 4px;
    }

    /* Radar cards atualizados (fonte e margens maiores) */
    .radar-card {
        background: #FFFFFF;
        border: 1px solid #DCE4EC;
        border-left: 4px solid #1A237E;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 3px 10px rgba(26, 35, 126, 0.05);
        color: #263238 !important;
        font-size: 14.5px; 
        line-height: 1.5;
    }
    .radar-card.warning { border-left-color: #F57C00; }
    .radar-card.critical { border-left-color: #D32F2F; }
    .radar-card.ok { border-left-color: #2E7D32; }
    
    /* Título dos gráficos atualizados (mais destaque) */
    .chart-title { height: 50px; display: flex; align-items: center; font-size: 18px; font-weight: 800; color: #1A237E !important; text-align: left; margin-bottom: 8px; }

    /* ==========================================
       ESTILO DAS ABAS (TABS COMO BOTÕES PROPORCIONAIS)
       ========================================== */
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] [data-baseweb="tab-border"] {
        display: none !important;
    }

    div[data-testid="stTabs"] [role="tablist"] {
        display: flex !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
        gap: 12px !important;
        padding-bottom: 15px !important;
    }

    div[data-testid="stTabs"] [role="tab"] {
        flex: 1 1 calc(20% - 12px) !important;
        min-width: 140px !important;
        background-color: #FFFFFF !important; 
        border: 1px solid #CFD8DC !important; 
        border-radius: 8px !important; 
        padding: 10px 8px !important; 
        margin: 0 !important;
        min-height: 48px !important;
        height: auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="stTabs"] [role="tab"] p {
        color: #1A237E !important; 
        font-weight: 700 !important; 
        font-size: 14px !important;
        margin: 0 !important;
        white-space: normal !important;
        text-align: center !important;
        line-height: 1.2 !important;
    }

    div[data-testid="stTabs"] [role="tab"]:hover {
        background-color: #F0F4F8 !important;
        border-color: #90CAF9 !important;
        transform: translateY(-2px);
    }

    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] { 
        background-color: #1A237E !important; 
        border-color: #1A237E !important; 
        box-shadow: 0px 4px 10px rgba(26, 35, 126, 0.2) !important;
    }

    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] p { 
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
    
    /* Tabelas Raio-X atualizadas (Fontes e espaçamentos reajustados para visibilidade) */
    .rx-list{
        background:#FFFFFF;
        border:1px solid #DCE4EC;
        border-radius:12px;
        overflow:hidden;
        box-shadow:0 3px 10px rgba(26,35,126,.04);
    }
    .rx-header{
        display:grid;
        grid-template-columns: minmax(180px, 2.3fr) 0.8fr 1fr 1.3fr 1fr;
        align-items:center;
        gap:10px;
        padding:12px 16px 10px 16px;
        background:#F9FBFD;
        border-bottom:1px solid #E7EDF3;
        color:#607D8B !important;
        font-size: 12px;
        font-weight:800;
        text-transform:uppercase;
        letter-spacing:.35px;
    }
    .rx-row{
        display:grid;
        grid-template-columns: minmax(180px, 2.3fr) 0.8fr 1fr 1.3fr 1fr;
        align-items:center;
        gap:10px;
        padding: 16px 16px;
        border-bottom:1px solid #EEF2F6;
    }
    .rx-row:last-child{border-bottom:none}
    .rx-row:hover{background:#FAFCFF}
    
    .rx-name{color:#17206A !important;font-size:14.5px;font-weight:800; line-height: 1.2;}
    .rx-ativos{color:#2E7D32 !important;font-size:13.5px;font-weight:800;text-align:right;white-space:nowrap}
    .rx-km{color:#1976D2 !important;font-size:13.5px;font-weight:800;text-align:right;white-space:nowrap}
    .rx-money{color:#14206F !important;font-size:14.5px;font-weight:800;text-align:right;white-space:nowrap}
    .rx-badge{justify-self:end;background:#F2F5FA;color:#14206F !important;border:1px solid #E0E6EF;border-radius:999px;padding:6px 12px;font-size:12.5px;font-weight:800;white-space:nowrap}
    .rx-inst{color:#607D8B !important;font-size:10px;font-weight:800;margin-left:6px;background:#F3F6F9;border-radius:999px;padding:3px 6px}

</style>
""", unsafe_allow_html=True)

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

else:
    st.sidebar.markdown("### 🏢 LOGÍSTICA")
    if st.sidebar.button("🔒 Sair / Bloquear App"):
        st.session_state["autenticado"] = False
        st.rerun()
    
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

    @st.cache_data(ttl=60) 
    def load_ipva_data():
        try:
            url_ipva_base = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVMBTwRCrEvDUddWeUaIIpdSiA27cuPhHeArqAa_I3b_E8Fa_43lKg5hhSh2StAQddZQIXFFlM-zn-/pub?gid=398571100&single=true&output=csv"
            url_ipva = f"{url_ipva_base}&t={int(time.time())}"
            
            df_ipva = pd.read_csv(url_ipva, decimal=',', sep=',')
            
            if 'Ipva estimado' in df_ipva.columns:
                df_ipva['Ipva estimado'] = to_float(df_ipva['Ipva estimado'])
                
            return df_ipva
            
        except Exception as e:
            st.error(f"Erro ao carregar dados de IPVA: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=60) 
    def load_top_km_data():
        try:
            url_top_km_base = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVMBTwRCrEvDUddWeUaIIpdSiA27cuPhHeArqAa_I3b_E8Fa_43lKg5hhSh2StAQddZQIXFFlM-zn-/pub?gid=2146713884&single=true&output=csv"
            
            if "COLE_O_LINK" in url_top_km_base:
                return pd.DataFrame() 
            
            url_top_km = f"{url_top_km_base}&t={int(time.time())}"
            df_top = pd.read_csv(url_top_km, decimal=',', sep=',', thousands='.')
            return df_top
            
        except Exception as e:
            st.error(f"Erro ao carregar dados do Top KM: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=60) 
    def load_data():
        try:
            url_base = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVMBTwRCrEvDUddWeUaIIpdSiA27cuPhHeArqAa_I3b_E8Fa_43lKg5hhSh2StAQddZQIXFFlM-zn-/pub?output=csv"
            url_planilha = f"{url_base}&t={int(time.time())}" 
            
            if ".csv" in url_planilha.lower() or "output=csv" in url_planilha.lower():
                df = pd.read_csv(url_planilha, decimal=',', thousands='.')
            else:
                df = pd.read_excel(url_planilha)
            
            if 'Mês Referência' in df.columns:
                datas_cruas = df['Mês Referência'].astype(str)
            else:
                datas_cruas = pd.Series('2026-01-01', index=df.index)

            datas_str = datas_cruas.str.strip().str.split(' ').str[0].str.split('T').str[0]
            
            formatos = ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%Y']
            d1 = pd.Series(pd.NaT, index=datas_str.index)
            
            for fmt in formatos:
                mask = d1.isna()
                if mask.any():
                    d1.loc[mask] = pd.to_datetime(datas_str[mask], format=fmt, errors='coerce')
            
            mask = d1.isna()
            if mask.any():
                d1.loc[mask] = pd.to_datetime(datas_str[mask], errors='coerce', dayfirst=True)
            
            df['Mês Referência'] = d1
            
            meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 
                        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
            df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
            df['Mes_Num'] = df['Mês Referência'].dt.month
            
            df['Ano'] = pd.to_datetime(df['Mês Referência'], errors='coerce').dt.year.fillna(2026).astype(int)
            
            df['Quilometragem'] = to_float(df['Quilometragem'])
            df['Custo de manutenção'] = to_float(df['Custo de manutenção'])
            df['Custo de seguro'] = to_float(df.get('Custo de seguro', 0))
            df['Custo de Rastreador'] = to_float(df.get('Custo de Rastreador', 0))
            
            if 'Custo de combustível' in df.columns:
                df['Custo Combustível'] = to_float(df['Custo de combustível'])
            else:
                df['Custo Combustível'] = to_float(df.iloc[:, 3])
            
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
        
        df_meses_validos = df_ano.dropna(subset=['Mes_Num', 'Mes_Nome']).copy()
        
        if df_meses_validos.empty:
            lista_meses = ["Nenhum Mês"]
        else:
            df_meses_unicos = df_meses_validos[['Mes_Num', 'Mes_Nome']].drop_duplicates().sort_values('Mes_Num')
            lista_meses = df_meses_unicos['Mes_Nome'].tolist()
            
        mes_sel = st.sidebar.selectbox("Mês Competência", options=lista_meses, index=len(lista_meses)-1)

        df_apenas_comb = df_base[df_base["Placa"].str.startswith("COMBUSTÍVEL", na=False)]
        df_apenas_manut = df_base[~df_base["Placa"].str.startswith("COMBUSTÍVEL", na=False)]

        try:
            mes_num_atual = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
        except:
            mes_num_atual = 1

        df_filtrado_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Nome"] == mes_sel]
        df_acumulado_ate_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] <= mes_num_atual]
        df_anterior_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] == mes_num_atual - 1]

        df_comb_mes = df_apenas_comb[df_apenas_comb["Mes_Nome"] == mes_sel]
        df_comb_acum = df_apenas_comb[df_apenas_comb["Mes_Num"] <= mes_num_atual]
        df_comb_anterior = df_apenas_comb[df_apenas_comb["Mes_Num"] == mes_num_atual - 1]

        # ==========================================================
        # CONJUNTO DE ABAS - OTIMIZADO PARA 8 OPÇÕES
        # ==========================================================
        tab_ceo, tab_manut, tab_comb, tab_seg, tab_raiox, tab_km, tab_frota, tab_detalhes = st.tabs([
            "🌐 Visão Executiva",
            "🔧 Manutenção", 
            "⛽ Combustível", 
            "🛡️ Seguro/Rastreadores", 
            "📍 Raio-X da Base", 
            "🛣️ Gestão de Quilometragem", 
            "📋 Frota, IPVA & Doc", 
            "📑 Detalhamento"
        ])

        with tab_ceo:
            # ==========================================================
            # VISÃO EXECUTIVA 2.0 — GESTÃO, ORÇAMENTO E RASTREABILIDADE
            # ==========================================================
            st.markdown(f"### 🌎 Painel Executivo de Logística | {ano_sel}")

            if inst_sel == "AMES":
                nome_unidade = "Base Social"
                titulo_ranking_unidades = "📍 Bases Sociais | Maior Custo Acumulado"
                titulo_raiox_unidades = "🔎 Raio-X das Bases Sociais"
                contexto_inst = "AMES · Apoio à atuação missionária"
            elif inst_sel == "IAV":
                nome_unidade = "Centro de Custo"
                titulo_ranking_unidades = "🏢 Centros de Custo | Maior Custo Acumulado"
                titulo_raiox_unidades = "🔎 Raio-X dos Centros de Custo"
                contexto_inst = "IAV · Estrutura, projetos e serviços"
            else:
                nome_unidade = "Unidade"
                titulo_ranking_unidades = "📊 Unidades | Maior Custo Acumulado"
                titulo_raiox_unidades = "🔎 Raio-X das Unidades"
                contexto_inst = "AMES + IAV · Visão consolidada"

            st.caption(f"{contexto_inst} · Acumulado até {mes_sel}/{ano_sel}")

            # ---------- Regras centrais de classificação ----------
            cadastro_pattern = r"^(VEÍCUL|VEICUL|ALUGAD|MOTO|KOMBI|TRICICLO|REBOQUE|SPRINTER|ÔNIBUS|ONIBUS|MICRO)"

            def limpar_unidade(valor):
                texto = str(valor).strip()
                texto = re.sub(r"\s*\(\d+\)\s*$", "", texto).strip()
                texto = re.sub(r"\s+", " ", texto)
                texto = re.sub(r"\s*-\s*", " - ", texto)
                texto = texto.replace("RDB7G83", "RBD7G83")
                texto = texto.replace("LOGISTICA", "LOGÍSTICA")
                return texto.strip()

            mask_cadastro_exec = df_base_completa["Placa"].astype(str).str.contains(
                cadastro_pattern, case=False, na=False, regex=True
            )
            df_fin_exec = df_base_completa[~mask_cadastro_exec].copy()
            df_fin_exec = df_fin_exec[df_fin_exec["Mes_Num"] <= mes_num_atual].copy()
            df_fin_exec["Unidade_Gestao"] = df_fin_exec[col_cc].apply(limpar_unidade)
            df_fin_exec["Custo_Total"] = (
                df_fin_exec["Custo de manutenção"]
                + df_fin_exec["Custo Combustível"]
                + df_fin_exec["Custo de seguro"]
                + df_fin_exec["Custo de Rastreador"]
            )

            mask_cadastro_frota = df_temp_inst["Placa"].astype(str).str.contains(
                cadastro_pattern, case=False, na=False, regex=True
            )
            df_frota_atual = df_temp_inst[mask_cadastro_frota].copy()
            if not df_frota_atual.empty:
                df_frota_atual["Placa_Fisica"] = df_frota_atual["Placa"].astype(str).str.upper().str.extract(r"([A-Z0-9]{7})\s*$", expand=False)
                df_frota_atual["Placa_Fisica"] = df_frota_atual["Placa_Fisica"].fillna(df_frota_atual["Placa"].astype(str))
                df_frota_atual = df_frota_atual.sort_values("Mes_Num").drop_duplicates(subset=["Placa_Fisica"], keep="last")
                df_frota_atual["Unidade_Gestao"] = df_frota_atual[col_cc].apply(limpar_unidade)
                if cc_sel != "TODOS":
                    unidade_sel_limpa = limpar_unidade(cc_sel)
                    df_frota_atual = df_frota_atual[df_frota_atual["Unidade_Gestao"] == unidade_sel_limpa]

            # ---------- Indicadores executivos ----------
            gasto_manut_acum = df_fin_exec["Custo de manutenção"].sum()
            gasto_comb_acum = df_fin_exec["Custo Combustível"].sum()
            gasto_seguro_acum = df_fin_exec["Custo de seguro"].sum()
            gasto_rastreador_acum = df_fin_exec["Custo de Rastreador"].sum()
            custo_total_global = df_fin_exec["Custo_Total"].sum()
            km_total_global = df_fin_exec["Quilometragem"].sum()
            qtd_frota = df_frota_atual["Placa_Fisica"].nunique() if not df_frota_atual.empty else 0

            orc_manut = sum(ORCAMENTOS_MANUT_2026.get(inst, 0) for inst in inst_ativas)
            orc_comb = sum(ORCAMENTOS_COMB_2026.get(inst, 0) for inst in inst_ativas)
            orc_seg = sum(ORCAMENTOS_SEGURO_2026.get(inst, 0) for inst in inst_ativas)
            orc_rast = sum(ORCAMENTOS_RASTREADOR_2026.get(inst, 0) for inst in inst_ativas)
            orcamento_total_global = orc_manut + orc_comb + orc_seg + orc_rast

            saldo_global = orcamento_total_global - custo_total_global
            perc_global = (custo_total_global / orcamento_total_global * 100) if orcamento_total_global > 0 else 0
            cpk_global = custo_total_global / km_total_global if km_total_global > 0 else 0
            projecao_anual = (custo_total_global / mes_num_atual) * 12 if mes_num_atual > 0 else 0
            diferenca_proj = orcamento_total_global - projecao_anual

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                draw_card(
                    "💰 CUSTO ACUMULADO",
                    fmt_br(custo_total_global, True),
                    f"Até {mes_sel}/{ano_sel}"
                )
            with c2:
                if ano_sel == 2026 and orcamento_total_global > 0:
                    draw_card(
                        "🎯 EXECUÇÃO ORÇAMENTÁRIA",
                        f"{perc_global:.1f}%",
                        f"Orçamento: <b>{fmt_br(orcamento_total_global, True)}</b>",
                        progress=perc_global,
                        progress_text=f"Saldo: {fmt_br(saldo_global, True)}"
                    )
                else:
                    draw_card("🎯 EXECUÇÃO ORÇAMENTÁRIA", "—", "Orçamento não cadastrado para o ano")
            with c3:
                if ano_sel == 2026 and orcamento_total_global > 0:
                    if projecao_anual <= orcamento_total_global:
                        texto_proj = f"🟢 {fmt_br(diferenca_proj, True)} abaixo do orçamento"
                    else:
                        texto_proj = f"🔴 {fmt_br(abs(diferenca_proj), True)} acima do orçamento"
                    draw_card(
                        "📈 PREVISÃO DE GASTO ATÉ DEZ/26",
                        fmt_br(projecao_anual, True),
                        texto_proj
                    )
                else:
                    draw_card("📈 PREVISÃO DE GASTO ATÉ DEZ", fmt_br(projecao_anual, True), "Mantida a média atual de gastos")
            with c4:
                draw_card(
                    "🛣️ KM ACUMULADOS",
                    fmt_br(km_total_global),
                    f"CPK global: <b>{fmt_br(cpk_global, True)}/km</b>",
                    is_lower_better=False
                )
            with c5:
                draw_card(
                    "🚙 ATIVOS CADASTRADOS",
                    fmt_br(qtd_frota),
                    "Ativos no último vínculo conhecido do ano",
                    is_lower_better=False
                )

            st.markdown("<hr style='margin-top: 5px; margin-bottom: 18px'>", unsafe_allow_html=True)

            # ---------- Onde os recursos estão sendo utilizados ----------
            col_recursos, col_radar = st.columns([1.1, 1]) # Ajustado para dar mais largura equilibrada

            with col_recursos:
                st.markdown('<div class="chart-title">💰 Composição dos Custos</div>', unsafe_allow_html=True)
                df_composicao = pd.DataFrame({
                    "Categoria": ["Manutenção", "Combustível", "Seguro", "Rastreador"],
                    "Valor": [gasto_manut_acum, gasto_comb_acum, gasto_seguro_acum, gasto_rastreador_acum]
                })
                df_composicao = df_composicao[df_composicao["Valor"] > 0]

                if not df_composicao.empty:
                    fig_comp = px.bar(
                        df_composicao.sort_values("Valor"),
                        x="Valor", y="Categoria", orientation="h",
                        text="Valor",
                        color="Categoria",
                        color_discrete_map={
                            "Manutenção": "#F57C00",
                            "Combustível": "#0288D1",
                            "Seguro": "#1A237E",
                            "Rastreador": "#81D4FA"
                        }
                    )
                    # Aumentando o texto do gráfico e ajustando os eixos
                    fig_comp.update_traces(texttemplate='<b>R$ %{text:,.0f}</b>', textposition='outside', textfont=dict(size=15, color="#1A237E"), cliponaxis=False)
                    fig_comp.update_layout(
                        height=330, showlegend=False, separators=',.',
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=10, r=120, t=5, b=10),
                        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                        yaxis=dict(title="", tickfont=dict(size=14, color="#333333", weight="bold"))
                    )
                    st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})

            with col_radar:
                st.markdown('<div class="chart-title">🚨 Radar de Atenção</div>', unsafe_allow_html=True)
                alertas = []

                if ano_sel == 2026 and orcamento_total_global > 0:
                    perc_tempo = (mes_num_atual / 12) * 100
                    if projecao_anual > orcamento_total_global:
                        alertas.append(
                            f"⚠️ **Projeção acima do orçamento:** excesso estimado de {fmt_br(abs(diferenca_proj), True)}."
                        )
                    elif perc_global > perc_tempo + 10:
                        alertas.append(
                            f"⚠️ **Ritmo de consumo elevado:** {perc_global:.1f}% do orçamento utilizado com {perc_tempo:.1f}% do ano transcorrido."
                        )

                # Veículo físico com maior manutenção no acumulado.
                mask_placa_fisica = df_fin_exec["Placa"].astype(str).str.fullmatch(r"[A-Z0-9]{7}", case=False, na=False)
                df_placas_exec = df_fin_exec[mask_placa_fisica].copy()
                if not df_placas_exec.empty and df_placas_exec["Custo de manutenção"].sum() > 0:
                    resumo_placa = df_placas_exec.groupby("Placa", as_index=False).agg({
                        "Custo de manutenção": "sum",
                        "Custo_Total": "sum",
                        "Quilometragem": "sum"
                    }).sort_values("Custo de manutenção", ascending=False)
                    placa_crit = resumo_placa.iloc[0]["Placa"]
                    valor_crit = resumo_placa.iloc[0]["Custo de manutenção"]
                    custo_total_crit = resumo_placa.iloc[0]["Custo_Total"]
                    km_crit = resumo_placa.iloc[0]["Quilometragem"]
                    cpk_crit = custo_total_crit / km_crit if km_crit > 0 else 0

                    unidade_crit = ""
                    if not df_frota_atual.empty:
                        vinculo = df_frota_atual[df_frota_atual["Placa_Fisica"].astype(str).str.upper() == str(placa_crit).upper()]
                        if not vinculo.empty:
                            unidade_crit = str(vinculo.iloc[-1]["Unidade_Gestao"])

                    if "ODONTOVAN" in unidade_crit.upper():
                        titulo_crit = unidade_crit
                    else:
                        titulo_crit = placa_crit

                    alertas.append(
                        f"🔧 **{titulo_crit}** · Maior manutenção acumulada: {fmt_br(valor_crit, True)} · "
                        f"Custo/KM: {fmt_br(cpk_crit, True)}"
                    )

                if alertas:
                    for alerta in alertas[:4]:
                        classe = "critical" if ("acima do orçamento" in alerta.lower() or "ritmo de consumo elevado" in alerta.lower()) else "warning"
                        alerta_html = alerta.replace("**", "")
                        st.markdown(
                            f'<div class="radar-card {classe}">{alerta_html}</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        '<div class="radar-card ok">✅ Nenhum alerta financeiro crítico identificado para a seleção atual.</div>',
                        unsafe_allow_html=True
                    )

            st.markdown("<hr>", unsafe_allow_html=True)

            # ---------- Ranking de Bases Sociais / Centros de Custo ----------
            df_unidades = df_fin_exec.groupby(["Instituição", "Unidade_Gestao"], as_index=False).agg({
                "Custo de manutenção": "sum",
                "Custo Combustível": "sum",
                "Custo de seguro": "sum",
                "Custo de Rastreador": "sum",
                "Custo_Total": "sum",
                "Quilometragem": "sum"
            })

            if not df_frota_atual.empty:
                frota_unid = df_frota_atual.groupby(["Instituição", "Unidade_Gestao"])["Placa_Fisica"].nunique().reset_index(name="Ativos")
                df_unidades = pd.merge(df_unidades, frota_unid, on=["Instituição", "Unidade_Gestao"], how="left")
            else:
                df_unidades["Ativos"] = 0

            df_unidades["Ativos"] = df_unidades["Ativos"].fillna(0).astype(int)
            df_unidades["Custo/KM"] = df_unidades.apply(
                lambda r: r["Custo_Total"] / r["Quilometragem"] if r["Quilometragem"] > 0 else 0, axis=1
            )

            col_rank, col_top = st.columns([1, 1.25]) # A tabela agora tem mais espaço para exibir os textos grandes.
            
            with col_rank:
                st.markdown(f'<div class="chart-title">{titulo_ranking_unidades}</div>', unsafe_allow_html=True)
                top_unidades = df_unidades[df_unidades["Custo_Total"] > 0].nlargest(8, "Custo_Total").sort_values("Custo_Total")
                if not top_unidades.empty:
                    fig_unid = px.bar(
                        top_unidades,
                        x="Custo_Total", y="Unidade_Gestao", orientation="h",
                        text="Custo_Total", color="Instituição",
                        color_discrete_map={"AMES": "#0288D1", "IAV": "#F57C00"}
                    )
                    fig_unid.update_traces(texttemplate='<b>R$ %{text:,.0f}</b>', textposition='outside', textfont=dict(size=14, color="#1A237E"), cliponaxis=False)
                    fig_unid.update_layout(
                        height=390, separators=',.',
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=10, r=100, t=5, b=10),
                        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                        yaxis=dict(title="", automargin=True, tickfont=dict(size=13, color="#333333", weight="bold")),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title="")
                    )
                    st.plotly_chart(fig_unid, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("Sem custos para exibir nesta seleção.")

            with col_top:
                st.markdown(f'<div class="chart-title">{titulo_raiox_unidades}</div>', unsafe_allow_html=True)
                tabela_unid = df_unidades[df_unidades["Custo_Total"] > 0].nlargest(8, "Custo_Total")[
                    ["Instituição", "Unidade_Gestao", "Ativos", "Quilometragem", "Custo_Total", "Custo/KM"]
                ].rename(columns={"Unidade_Gestao": nome_unidade})
                
                if not tabela_unid.empty:
                    linhas = []
                    mostrar_inst = inst_sel == "TODAS"
                    for _, r in tabela_unid.iterrows():
                        tag = f'<span class="rx-inst">{r["Instituição"]}</span>' if mostrar_inst else ""
                        linhas.append(
                            f'<div class="rx-row">'
                            f'<div class="rx-name">{r[nome_unidade]}{tag}</div>'
                            f'<div class="rx-ativos">{int(r["Ativos"])} ativos</div>'
                            f'<div class="rx-km">{fmt_br(r["Quilometragem"])} km</div>'
                            f'<div class="rx-money">{fmt_br(r["Custo_Total"], True)}</div>'
                            f'<div class="rx-badge">{fmt_br(r["Custo/KM"], True)}/km</div>'
                            f'</div>'
                        )

                    cabecalho_rx = (
                        '<div class="rx-header">'
                        f'<div>{nome_unidade}</div>'
                        '<div style="text-align:right">Ativos</div>'
                        '<div style="text-align:right">KM</div>'
                        '<div style="text-align:right">Custo Total</div>'
                        '<div style="text-align:right">Custo/KM</div>'
                        '</div>'
                    )

                    st.markdown(
                        '<div class="rx-list">' + cabecalho_rx + "".join(linhas) + '</div>',
                        unsafe_allow_html=True
                    )

            # ---------- Destaque específico: Odontovans ----------
            df_odonto = df_unidades[df_unidades["Unidade_Gestao"].astype(str).str.contains("ODONTOVAN", case=False, na=False)].copy()
            if not df_odonto.empty:
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown('<div class="chart-title">🦷 Odontovans | Visão Financeira e Operacional</div>', unsafe_allow_html=True)
                
                tabela_odonto = df_odonto[[
                    "Instituição", "Unidade_Gestao", "Ativos", "Quilometragem",
                    "Custo de manutenção", "Custo Combustível", "Custo_Total", "Custo/KM"
                ]].sort_values("Custo_Total", ascending=False).rename(columns={
                    "Unidade_Gestao": "Odontovan",
                    "Quilometragem": "KM"
                })
                
                linhas_od = []
                mostrar_inst_od = inst_sel == "TODAS"
                for _, r in tabela_odonto.iterrows():
                    tag = f'<span class="rx-inst">{r["Instituição"]}</span>' if mostrar_inst_od else ""
                    linhas_od.append(
                        f'<div class="rx-row">'
                        f'<div class="rx-name">{r["Odontovan"]}{tag}</div>'
                        f'<div class="rx-ativos">{int(r["Ativos"])} ativos</div>'
                        f'<div class="rx-km">{fmt_br(r["KM"])} km</div>'
                        f'<div class="rx-money">{fmt_br(r["Custo_Total"], True)}</div>'
                        f'<div class="rx-badge">{fmt_br(r["Custo/KM"], True)}/km</div>'
                        f'</div>'
                    )
                
                cabecalho_od = (
                    '<div class="rx-header">'
                    f'<div>Odontovan</div>'
                    '<div style="text-align:right">Ativos</div>'
                    '<div style="text-align:right">KM</div>'
                    '<div style="text-align:right">Custo Total</div>'
                    '<div style="text-align:right">Custo/KM</div>'
                    '</div>'
                )
                
                st.markdown('<div class="rx-list">' + cabecalho_od + "".join(linhas_od) + '</div>', unsafe_allow_html=True)

        with tab_manut:
            # ================= VISÃO MENSAL =================
            st.markdown(f"### 📊 Desempenho Mensal | {mes_sel}/{ano_sel}")
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

            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")

            # ================= VISÃO ACUMULADA =================
            st.markdown(f"### 📈 Desempenho Acumulado | {ano_sel}")
            
            ca1, ca2, ca3 = st.columns(3)
            with ca1:
                if ano_sel == 2026:
                    orc_total_manut = sum(ORCAMENTOS_MANUT_2026.get(inst, 0) for inst in inst_ativas)
                    saldo_manut = orc_total_manut - gasto_manut_acum
                    perc_manut = (gasto_manut_acum / orc_total_manut * 100) if orc_total_manut > 0 else 0
                    sub_manut = f"Orçamento Anual: <b>{fmt_br(orc_total_manut, True)}</b>"
                    prog_text_manut = f"{perc_manut:.1f}% &middot; Saldo {fmt_br(saldo_manut, True)}"
                    draw_card("EXECUÇÃO MANUT. (ACUMULADO)", fmt_br(gasto_manut_acum, True), sub_manut, progress=perc_manut, progress_text=prog_text_manut)
                else:
                    sub_manut = "Orçamento Anual: <b>A definir</b>"
                    draw_card("CUSTO DE MANUT. (ACUMULADO)", fmt_br(gasto_manut_acum, True), sub_manut)
                
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

        with tab_comb:
            st.markdown(f"### ⛽ Gestão de Combustível | {ano_sel}")

            k1, k2 = st.columns(2)
            with k1:
                gasto_m_comb = df_comb_mes["Custo Combustível"].sum()
                gasto_a_comb = df_comb_anterior["Custo Combustível"].sum()
                trend_comb = ((gasto_m_comb - gasto_a_comb) / gasto_a_comb * 100) if gasto_a_comb > 0 else 0
                sub_comb_m = f"Gasto exclusivo em {mes_sel}"
                draw_card("CUSTO COMBUSTÍVEL MENSAL", fmt_br(gasto_m_comb, True), sub_comb_m, trend=trend_comb)
                
            with k2:
                if ano_sel == 2026:
                    orc_total_comb = sum(ORCAMENTOS_COMB_2026.get(inst, 0) for inst in inst_ativas)
                    saldo_comb = orc_total_comb - gasto_comb_acum
                    perc_comb = (gasto_comb_acum / orc_total_comb * 100) if orc_total_comb > 0 else 0
                    sub_comb = f"Orçamento Anual: <b>{fmt_br(orc_total_comb, True)}</b>"
                    prog_text_comb = f"{perc_comb:.1f}% &middot; Saldo {fmt_br(saldo_comb, True)}"
                    draw_card("EXECUÇÃO COMBUSTÍVEL ANUAL", fmt_br(gasto_comb_acum, True), sub_comb, progress=perc_comb, progress_text=prog_text_comb)
                else:
                    sub_comb = "Orçamento Anual: <b>A definir</b>"
                    draw_card("CUSTO COMBUSTÍVEL (ACUMULADO)", fmt_br(gasto_comb_acum, True), sub_comb)
            
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

        with tab_seg:
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

        with tab_raiox:
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
                
                st.markdown(f"#### 🚘 Detalhamento para o Gestor | {base_raiox}")
                
                padrao_exclusao_rx = "COMBUS|SEGUR|FINANC|CONSÓRC|RASTR|LOGIST|MANUT|MENSAL|TAXA|VEÍCUL|VEICUL|ALUGAD|MOTO|KOMBI|TRICICLO|REBOQUE|SPRINTER|ÔNIBUS|ONIBUS|MICRO"
                
                df_veic_acum = df_rx_acum[~df_rx_acum["Placa"].astype(str).str.contains(padrao_exclusao_rx, case=False, na=True)]
                meses_ordem = df_rx_acum.drop_duplicates(subset=["Mes_Num"]).sort_values("Mes_Num")["Mes_Nome"].tolist()
                
                df_placas = pd.DataFrame()
                
                placas_validas = df_veic_acum["Placa"].unique()
                placas_validas = [p for p in placas_validas if str(p).strip() != "" and str(p).upper() != "NAN" and str(p).strip() != "0"]
                
                if len(placas_validas) > 0:
                    df_placas["Placa"] = sorted(placas_validas)
                    
                    df_km_pivot = pd.pivot_table(df_veic_acum, index="Placa", columns="Mes_Nome", values="Quilometragem", aggfunc="sum", fill_value=0).reset_index()
                    df_manut_pivot = pd.pivot_table(df_veic_acum, index="Placa", columns="Mes_Nome", values="Custo de manutenção", aggfunc="sum", fill_value=0).reset_index()
                    
                    for m in meses_ordem:
                        if m in df_km_pivot.columns:
                            col_k = df_km_pivot[["Placa", m]].rename(columns={m: f"KM ({m})"})
                            df_placas = pd.merge(df_placas, col_k, on="Placa", how="left").fillna(0)
                        else:
                            df_placas[f"KM ({m})"] = 0
                            
                        if m in df_manut_pivot.columns:
                            col_m = df_manut_pivot[["Placa", m]].rename(columns={m: f"Custo Manutenção ({m})"})
                            df_placas = pd.merge(df_placas, col_m, on="Placa", how="left").fillna(0)
                        else:
                            df_placas[f"Custo Manutenção ({m})"] = 0
                            
                    # --- NOVIDADE: CRIANDO AS COLUNAS DE TOTAIS ---
                    cols_km = [f"KM ({m})" for m in meses_ordem]
                    cols_custo = [f"Custo Manutenção ({m})" for m in meses_ordem]
                    
                    df_placas["KM Total Acumulado"] = df_placas[cols_km].sum(axis=1)
                    df_placas["Custo Total Acumulado"] = df_placas[cols_custo].sum(axis=1)
                    
                    # Ordena pelos veículos que mais gastaram no total
                    df_placas = df_placas.sort_values("Custo Total Acumulado", ascending=False)
                else:
                    cols_vazias = ["Placa"]
                    for m in meses_ordem:
                        cols_vazias.extend([f"KM ({m})", f"Custo Manutenção ({m})"])
                    cols_vazias.extend(["KM Total Acumulado", "Custo Total Acumulado"])
                    df_placas = pd.DataFrame(columns=cols_vazias)
                
                linha_comb = {"Placa": "⛽ COMBUSTÍVEL DA BASE"}
                tem_combustivel = False
                
                mask_combustivel = df_rx_acum["Placa"].astype(str).str.upper().str.startswith("COMBUSTÍVEL", na=False)
                df_comb_isolado = df_rx_acum[mask_combustivel]
                
                total_comb = 0
                for m in meses_ordem:
                    comb_val = df_comb_isolado[df_comb_isolado["Mes_Nome"] == m]['Custo Combustível'].sum()
                    
                    if comb_val > 0: 
                        tem_combustivel = True
                        
                    linha_comb[f"KM ({m})"] = 0
                    linha_comb[f"Custo Manutenção ({m})"] = comb_val
                    total_comb += comb_val
                
                linha_comb["KM Total Acumulado"] = 0
                linha_comb["Custo Total Acumulado"] = total_comb
                
                if tem_combustivel:
                    df_placas = pd.concat([df_placas, pd.DataFrame([linha_comb])], ignore_index=True)
                
                # --- NOVIDADE: LINHA DE TOTAL GERAL DA BASE ---
                if not df_placas.empty:
                    linha_total = {"Placa": "💰 TOTAL GERAL DA BASE"}
                    for col in df_placas.columns:
                        if col != "Placa":
                            linha_total[col] = df_placas[col].sum()
                    
                    df_placas = pd.concat([df_placas, pd.DataFrame([linha_total])], ignore_index=True)
                
                col_btn_placas, col_espaco = st.columns([1, 2])
                with col_btn_placas:
                    csv_placas = df_placas.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
                    st.download_button(
                        label=f"📥 Baixar Relatório do Gestor",
                        data=csv_placas,
                        file_name=f"Relatorio_Gestor_{base_raiox.replace(' ', '_')}_Ate_{mes_sel}_{ano_sel}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # --- NOVIDADE: ESTILIZAÇÃO DO TOTAL ---
                def highlight_special_rows(row):
                    placa = str(row['Placa'])
                    if "⛽" in placa:
                        return ['background-color: #FFF3E0; font-weight: bold; color: #E65100'] * len(row)
                    elif "💰" in placa:
                        return ['background-color: #1A237E; font-weight: bold; color: white'] * len(row)
                    return [''] * len(row)
                
                df_styled_placas = df_placas.style.apply(highlight_special_rows, axis=1)
                
                config_cols_dinamicas = {"Placa": st.column_config.TextColumn("Placa", width="medium")}
                for m in meses_ordem:
                    config_cols_dinamicas[f"KM ({m})"] = st.column_config.NumberColumn(f"KM ({m})", format="%.0f")
                    config_cols_dinamicas[f"Custo Manutenção ({m})"] = st.column_config.NumberColumn(f"Custo Manutenção ({m})", format="R$ %.2f")
                
                # Configurando o formato visual das novas colunas
                config_cols_dinamicas["KM Total Acumulado"] = st.column_config.NumberColumn("KM Total Acumulado", format="%.0f")
                config_cols_dinamicas["Custo Total Acumulado"] = st.column_config.NumberColumn("Custo Total Acumulado", format="R$ %.2f")
                
                st.dataframe(
                    df_styled_placas, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config=config_cols_dinamicas
                )

        with tab_km:
            # ================= TOP 15 KM =================
            st.markdown(f"### 🚗 Top 15 Veículos | Maior Quilometragem")
            st.markdown("Análise dos veículos mais rodados da frota")
            
            df_top_km = load_top_km_data()
            
            if df_top_km.empty:
                st.warning("⚠️ Os dados do Top KM ainda não puderam ser carregados. Verifique se há informações preenchidas na aba da planilha.")
            else:
                col_placa = 'Placa' if 'Placa' in df_top_km.columns else df_top_km.columns[0]
                
                col_km = None
                for col in df_top_km.columns:
                    if 'KM' in col.upper() or 'QUILOMETRAGEM' in col.upper():
                        col_km = col
                        break
                
                if not col_km and len(df_top_km.columns) > 1:
                    col_km = df_top_km.columns[1]
                
                if col_placa and col_km:
                    df_top_km[col_km] = to_float(df_top_km[col_km])
                    
                    if df_top_km[col_km].max() > 0 and df_top_km[col_km].max() < 3000:
                        df_top_km[col_km] = df_top_km[col_km] * 1000
                    
                    top15 = df_top_km.nlargest(15, col_km).sort_values(col_km, ascending=True)
                    
                    c_grafico, c_tabela = st.columns([2, 1.2])
                    
                    with c_grafico:
                        st.markdown('<div class="chart-title">Ranking dos 15 veículos Mais Rodados</div>', unsafe_allow_html=True)
                        
                        def formatar_k(x):
                            if x >= 1000:
                                return f"{x/1000:.0f}K"
                            return f"{x:,.0f}".replace(',', '.')
                        
                        top15['KM_Formatado'] = top15[col_km].apply(formatar_k)
                        
                        # APLICADO O DEGRADÊ DE VERMELHO ABAIXO
                        fig_top15 = px.bar(
                            top15, 
                            x=col_km, 
                            y=col_placa, 
                            orientation='h', 
                            text='KM_Formatado', 
                            color=col_km,  # Mapeia a cor para o valor da Quilometragem
                            color_continuous_scale='Reds'  # Aplica o degradê do mais claro ao mais escuro
                        )
                        
                        fig_top15.update_traces(
                            texttemplate='<b>%{text}</b>', 
                            textposition='outside', 
                            textfont=ESTILO_TEXTO, 
                            cliponaxis=False
                        )
                        max_km = top15[col_km].max() if not top15.empty else 1
                        
                        fig_top15.update_layout(
                            height=550, 
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)', 
                            margin=dict(r=60, l=10, t=10, b=10), 
                            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_km * 1.20]), 
                            yaxis=dict(automargin=True, tickfont=dict(size=13, color='#333333', family="Arial, sans-serif"), title=""),
                            coloraxis_showscale=False  # Oculta a barrinha lateral do degradê para ficar mais limpo
                        )
                        st.plotly_chart(fig_top15, use_container_width=True, config={'displayModeBar': False})
                    
                    with c_tabela:
                        st.markdown('<div class="chart-title">Tabela de Dados</div>', unsafe_allow_html=True)
                        tabela_top15 = df_top_km.nlargest(15, col_km).sort_values(col_km, ascending=False)
                        st.dataframe(
                            tabela_top15, 
                            use_container_width=True, 
                            hide_index=True,
                            column_config={col_km: st.column_config.NumberColumn("Quilometragem", format="%d")}
                        )
                else:
                    st.error("Não foi possível identificar as colunas de 'Placa' e 'KM' na sua nova planilha Top Km. Verifique os títulos das colunas.")

            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")

            # ================= MAPA DE QUILOMETRAGEM =================
            st.markdown(f"### 🛣️ Mapa de Quilometragem | {ano_sel}")
            st.markdown("Visão em matriz da quilometragem rodada por veículo e por base, com totais consolidados ao longo dos meses.")
            
            padrao_exclusao_km = "COMBUS|SEGUR|FINANC|CONSÓRC|RASTR|LOGIST|MANUT|MENSAL|TAXA|VEÍCUL|VEICUL|ALUGAD|MOTO|KOMBI|TRICICLO|REBOQUE|SPRINTER|ÔNIBUS|ONIBUS|MICRO"
            
            mask_km = (
                (~df_base_completa["Placa"].astype(str).str.contains(padrao_exclusao_km, case=False, na=True)) &
                (df_base_completa["Placa"].astype(str).str.strip() != "") &
                (df_base_completa["Placa"].astype(str).str.upper() != "NAN") &
                (df_base_completa["Placa"].astype(str).str.strip() != "0")
            )
            df_km_matrix = df_base_completa[mask_km]
            
            if not df_km_matrix.empty:
                pt_km = pd.pivot_table(
                    df_km_matrix,
                    values='Quilometragem',
                    index=['Instituição', col_cc, 'Placa'],
                    columns='Mes_Num',
                    aggfunc='sum',
                    fill_value=0
                ).reset_index()
                
                meses_map = {1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN', 
                             7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'}
                
                meses_presentes = sorted([c for c in pt_km.columns if isinstance(c, int)])
                nomes_meses_presentes = [meses_map.get(m, str(m)) for m in meses_presentes]
                
                renames = {m: meses_map.get(m, str(m)) for m in meses_presentes}
                pt_km.rename(columns=renames, inplace=True)
                
                pt_km['TOTAL'] = pt_km[nomes_meses_presentes].sum(axis=1)
                pt_km = pt_km.sort_values(['Instituição', col_cc, 'Placa'])
                
                linhas_subtotal = []
                for inst in pt_km['Instituição'].unique():
                    df_inst = pt_km[pt_km['Instituição'] == inst]
                    for base in df_inst[col_cc].unique():
                        df_b = df_inst[df_inst[col_cc] == base]
                        
                        for _, row in df_b.iterrows():
                            linhas_subtotal.append(row.to_dict())
                        
                        subtotal_dict = {'Instituição': inst, col_cc: base, 'Placa': 'Subtotal'}
                        for mes in nomes_meses_presentes:
                            subtotal_dict[mes] = df_b[mes].sum()
                        subtotal_dict['TOTAL'] = df_b['TOTAL'].sum()
                        linhas_subtotal.append(subtotal_dict)
                    
                    total_inst_dict = {'Instituição': inst, col_cc: '', 'Placa': f'TOTAL {inst}'}
                    for mes in nomes_meses_presentes:
                        total_inst_dict[mes] = df_inst[mes].sum()
                    total_inst_dict['TOTAL'] = df_inst['TOTAL'].sum()
                    linhas_subtotal.append(total_inst_dict)
                
                total_geral_dict = {'Instituição': '', col_cc: '', 'Placa': 'TOTAL GERAL'}
                for mes in nomes_meses_presentes:
                    total_geral_dict[mes] = pt_km[mes].sum()
                total_geral_dict['TOTAL'] = pt_km['TOTAL'].sum()
                linhas_subtotal.append(total_geral_dict)
                
                df_km_subtotals = pd.DataFrame(linhas_subtotal)
                
                def highlight_subtotals(row):
                    placa = str(row['Placa']).upper()
                    if 'SUBTOTAL' in placa:
                        return ['background-color: #E3F2FD; font-weight: bold; color: #1A237E'] * len(row)
                    elif 'TOTAL' in placa:
                        return ['background-color: #1A237E; color: white; font-weight: bold'] * len(row)
                    return [''] * len(row)
                
                def format_br_int(val):
                    try: return f"{int(val):,.0f}".replace(",", ".")
                    except: return "0"
                
                format_dict = {c: format_br_int for c in nomes_meses_presentes + ['TOTAL']}
                df_styled = df_km_subtotals.style.apply(highlight_subtotals, axis=1).format(format_dict)
                
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

        with tab_frota:
            # ================= RELAÇÃO DA FROTA =================
            st.markdown(f"### 📋 Relação da Frota | {ano_sel}")
            st.markdown("Lista atualizada da frota genérica vinculada às bases, segmentada por categoria em uma única planilha.")
            
            pattern_digitais = "VEÍCUL|VEICUL|ALUGAD|MOTO|KOMBI|TRICICLO|REBOQUE|SPRINTER|ÔNIBUS|ONIBUS|MICRO"
            mask_frota_aba = df_base_completa["Placa"].astype(str).str.contains(pattern_digitais, case=False, na=False)
            
            df_frota = df_base_completa[mask_frota_aba].copy()
            
            if not df_frota.empty:
                df_frota_unica = df_frota.sort_values("Mes_Num", ascending=False).drop_duplicates(subset=["Placa"])
                
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
                
                df_frota_unica = df_frota_unica.sort_values(['Instituição', 'Ordem_Cat', col_cc, 'Placa'])
                
                linhas_segmentadas = []
                for inst in df_frota_unica['Instituição'].unique():
                    df_i = df_frota_unica[df_frota_unica['Instituição'] == inst]
                    
                    for cat in df_i['Categoria'].unique():
                        linhas_segmentadas.append({
                            'Placa': f"🔸 {str(cat).upper()}",
                            'Instituição': inst,
                            col_cc: "",
                            'Modelo': "",
                            'Motorista': ""
                        })
                        
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
                
                def highlight_category(row):
                    placa_val = str(row['Placa'])
                    if placa_val.startswith('🔸'):
                        return ['background-color: #1A237E; color: white; font-weight: bold'] * len(row)
                    return [''] * len(row)
                
                df_styled = df_apresentacao.style.apply(highlight_category, axis=1)
                
                csv_relacao = df_apresentacao.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
                st.download_button(
                    label="📥 Baixar Relação da Frota Segmentada (Excel/CSV)",
                    data=csv_relacao,
                    file_name=f"Relacao_Frota_Segmentada_{inst_sel}_{ano_sel}.csv",
                    mime="text/csv",
                    key="btn_download_relacao"
                )
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.dataframe(df_styled, use_container_width=True, hide_index=True)
                st.info(f"Total de registros na frota (excluindo cabeçalhos): **{len(df_frota_unica)}**")
            else:
                st.warning("Nenhum veículo encontrado para exibir nesta aba.")

            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")

            # ================= VEÍCULOS & IPVA =================
            st.markdown(f"### 📅 Estimativas de IPVA e Dados de Veículos")
            st.markdown("Base de consulta atualizada automaticamente via Google Sheets.")
            
            df_ipva = load_ipva_data()
            
            if "Aviso" in df_ipva.columns:
                st.warning(df_ipva["Aviso"].iloc[0])
            elif not df_ipva.empty:
                
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
                
                df_ipva_filtrado = df_ipva.copy()
                if inst_ipva != "TODAS":
                    df_ipva_filtrado = df_ipva_filtrado[df_ipva_filtrado['Instituição'] == inst_ipva]
                if ano_ipva != "TODOS":
                    df_ipva_filtrado = df_ipva_filtrado[df_ipva_filtrado['Ano base'] == ano_ipva]
                
                config_cols_ipva = {}
                if 'Ipva estimado' in df_ipva_filtrado.columns:
                    config_cols_ipva['Ipva estimado'] = st.column_config.NumberColumn("Ipva estimado", format="R$ %.2f")
                if 'Ano base' in df_ipva_filtrado.columns:
                    config_cols_ipva['Ano base'] = st.column_config.NumberColumn("Ano base", format="%d")
                if 'Ano do veículo' in df_ipva_filtrado.columns:
                    config_cols_ipva['Ano do veículo'] = st.column_config.NumberColumn("Ano do veículo", format="%d")
                
                total_ipva = df_ipva_filtrado['Ipva estimado'].sum() if 'Ipva estimado' in df_ipva_filtrado.columns else 0
                st.markdown(f"**Total de veículos listados:** {len(df_ipva_filtrado)} | **Valor Total Estimado:** {fmt_br(total_ipva, True)}")
                
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
                
                st.dataframe(df_ipva_filtrado, use_container_width=True, hide_index=True, column_config=config_cols_ipva)
            else:
                st.warning("Nenhum dado de IPVA encontrado ou erro de carregamento.")

        with tab_detalhes:
            st.markdown("### 📑 Detalhamento dos Dados")
            
            df_download = df_base_completa.drop(columns=['Mes_Num'], errors='ignore')
            
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
