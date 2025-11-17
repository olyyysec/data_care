import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import sqlite3
import os

# Configuração da página
st.set_page_config(
    page_title="Sistema DataCare",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
st.markdown("""
<style>
    .main {
        background: linear-gradient(180deg, #0b1220, #0f172a);
        color: #e5e7eb;
    }
    .stApp {
        background: linear-gradient(180deg, #0b1220, #0f172a);
    }
    .card {
        background: rgba(17,24,39,0.85);
        padding: 25px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.04);
        margin-bottom: 20px;
    }
    .pill {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        margin: 4px;
        background: rgba(34,211,238,0.12);
        border: 1px solid rgba(34,211,238,0.26);
        font-size: 14px;
    }
    .result-box {
        background: rgba(2,6,23,0.6);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #22d3ee;
        margin-top: 20px;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Categorias de comorbidades
CATEGORIES = {
    "Cardiovasculares": {
        "SAH": "Hipertensão arterial sistêmica (HAS)",
        "acute myocardium infarct": "Infarto agudo do miocárdio",
        "cardiac insufficiency": "Insuficiência cardíaca",
        "cardiopathy": "Cardiopatia",
        "arrhythmia": "Arritmia",
        "pulmonary embolism": "Embolia pulmonar",
        "valvulopathy": "Valvulopatia",
        "aneurysm": "Aneurisma",
        "catheterism": "Cateterismo"
    },
    "Neurológicas": {
        "AVC": "Acidente cerebrovascular (AVC)",
        "brain tumor": "Tumor cerebral",
        "migraine": "Enxaqueca",
        "intracranial hypertension": "Hipertensão intracraniana",
        "meningioma": "Meningioma",
        "hydrocephalus": "Hidrocefalia",
        "devic": "Síndrome de Devic",
        "cerebral palsy": "Paralisia cerebral",
        "esclerose_multipla": "Esclerose múltipla"
    },
    "Respiratórias / Pulmonares": {
        "asthma": "Asma"
    },
    "Endócrinas / Metabólicas": {
        "hipotireoidismo": "Hipotireoidismo",
        "hipertireoidismo": "Hipertireoidismo",
        "hypercholesterolemia": "Hipercolesterolemia",
        "hypertriglyceridemia": "Hipertrigliceridemia",
        "hipocolesterolemia": "Hipocolesterolemia",
        "hypophysis adenoma": "Adenoma da hipófise",
        "obesity": "Obesidade"
    },
    "Renais / Hepáticas": {
        "chronic kidney disease": "Doença renal crônica",
        "kidney transplant": "Transplante renal",
        "dialysis": "Diálise",
        "cirrhosis": "Cirrose",
        "hepatic transplant": "Transplante hepático",
        "hepatic_cancer": "Câncer hepático"
    },
    "Hematológicas / Imunológicas": {
        "anemia": "Anemia",
        "sickle cell anemia": "Anemia falciforme",
        "leucemia": "Leucemia",
        "lymphoma": "Linfoma",
        "sjogren": "Síndrome de Sjögren",
        "sarcoidosis": "Sarcoidose",
        "dyslipidemia": "Dislipidemia"
    },
    "Autoimunes / Inflamatórias": {
        "behcet": "Doença de Behçet",
        "fibromyalgia": "Fibromialgia",
        "psoriasis": "Psoríase",
        "vasculitis": "Vasculite",
        "artrite": "Artrite",
        "arthrosis": "Artrose"
    },
    "Oncológicas": {
        "breast cancer": "Câncer de mama",
        "lung cancer": "Câncer de pulmão",
        "intestinal cancer": "Câncer intestinal"
    },
    "Genéticas / Congênitas": {
        "down syndrome": "Síndrome de Down",
        "albinism": "Albinismo",
        "mccune albright": "Síndrome de McCune-Albright",
        "neurofibromatosis": "Neurofibromatose",
        "policitemia vera": "Policitemia vera"
    },
    "Outras": {
        "osteoporosis": "Osteoporose",
        "prolactinoma": "Prolactinoma",
        "prostatic hyperplasia": "Hiperplasia prostática",
        "vitiligo": "Vitiligo",
        "tabagism": "Tabagismo",
        "human immunodeficiency virus": "Vírus da imunodeficiência humana (HIV)",
        "hepatitis c": "Hepatite C",
        "trombose_venosa_profunda": "Trombose venosa profunda",
        "doenca_chagas": "Doença de Chagas",
        "cloroquina": "Cloroquina"
    }
}

# Função para converter cm para m
def cm_para_metros(cm):
    return cm / 100

# Função para calcular IMC
def calcular_imc(peso, altura_cm):
    if peso and altura_cm and altura_cm > 0:
        altura_m = cm_para_metros(altura_cm)
        return round(peso / (altura_m * altura_m), 1)
    return None

def classificar_imc(imc):
    if not imc:
        return ""
    if imc < 18.5:
        return "Baixo peso"
    elif imc < 25:
        return "Eutrofia"
    elif imc < 30:
        return "Sobrepeso"
    elif imc < 35:
        return "Obesidade I"
    elif imc < 40:
        return "Obesidade II"
    else:
        return "Obesidade III"

# Função para fazer predição - CORRIGIDA
def fazer_predicao(payload):
    try:
        # ⬇️ CORREÇÃO: Usa variável de ambiente do Docker Compose
        BACKEND_URL = os.getenv('BACKEND_URL', 'http://modelo-back:5000')
        
        response = requests.post(
            f"{BACKEND_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_text = response.text
            try:
                error_json = response.json()
                error_text = str(error_json)
            except:
                pass
            return {"error": f"Erro no servidor: {response.status_code} - {error_text}"}
            
    except requests.exceptions.ConnectionError:
        return {"error": f"Não foi possível conectar ao servidor em {BACKEND_URL}. Verifique se o Flask está rodando."}
    except Exception as e:
        return {"error": f"Erro na conexão: {str(e)}"}

# Função para formatar nome do arquivo
def formatar_nome_arquivo(nome, data):
    # Remove caracteres especiais e espaços
    nome_limpo = "".join(c for c in nome if c.isalnum() or c in (' ', '-', '_')).rstrip()
    nome_limpo = nome_limpo.replace(' ', '_')
    
    # Formata data
    data_str = data.strftime("%Y%m%d")
    
    return f"consulta_{nome_limpo}_{data_str}.pdf"

# Página de Login
def login_page():
    st.markdown("""
    <div style='max-width: 400px; margin: 100px auto; padding: 30px; background: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
        <h2 style='text-align: center; color: #333; margin-bottom: 30px;'>Login Médico</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("E-mail", placeholder="seu@email.com")
        senha = st.text_input("Senha", type="password", placeholder="Sua senha")
        
        submit_login = st.form_submit_button("Entrar", use_container_width=True)
        
        if submit_login:
            if email and senha:
                st.session_state.logged_in = True
                st.session_state.current_page = "menu"
                st.rerun()
            else:
                st.error("Por favor, preencha todos os campos")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Cadastrar", use_container_width=True):
            st.session_state.current_page = "cadastro"
            st.rerun()

# Página de Cadastro
def cadastro_page():
    st.markdown("""
    <div style='max-width: 500px; margin: 50px auto; padding: 30px; background: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
        <h2 style='text-align: center; color: #333; margin-bottom: 30px;'>Cadastro de Médico</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("cadastro_form"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo", placeholder="Dr. João Silva")
            crm = st.text_input("CRM", placeholder="12345-SP")
            especialidade = st.text_input("Especialidade", placeholder="Cardiologia")
        with col2:
            telefone = st.text_input("Telefone", placeholder="(11) 99999-9999")
            email = st.text_input("E-mail", placeholder="seu@email.com")
            senha = st.text_input("Senha", type="password", placeholder="Sua senha")
        
        submit_cadastro = st.form_submit_button("Cadastrar", use_container_width=True)
        
        if submit_cadastro:
            if all([nome, crm, especialidade, email, senha]):
                st.success("Cadastro realizado com sucesso!")
                st.session_state.current_page = "login"
                st.rerun()
            else:
                st.error("Por favor, preencha todos os campos obrigatórios")
    
    if st.button("↩️ Voltar para Login"):
        st.session_state.current_page = "login"
        st.rerun()

# Página do Menu
def menu_page():
    st.sidebar.markdown("""
    <div style='padding: 20px; background: #2c3e50; border-radius: 8px; margin-bottom: 20px;'>
        <h2 style='color: white; text-align: center;'>Menu</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🏥 Data Care", use_container_width=True):
        st.session_state.current_page = "datacare"
        st.rerun()
    
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_page = "login"
        st.rerun()
    
    st.markdown("""
    <div class='card'>
        <h1>Bem-vindo, Doutor(a)!</h1>
        <p style='font-size: 16px; color: #94a3b8;'>Escolha uma opção no menu ao lado para continuar.</p>
    </div>
    """, unsafe_allow_html=True)

# Página Principal (DataCare)
def datacare_page():
    st.markdown("""
    <div class='card'>
        <h1>Cadastro de Consulta</h1>
        <p style='color: #94a3b8; margin-bottom: 30px;'>Preencha os dados do paciente e selecione as comorbidades.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar session state
    if 'comorbidades_selecionadas' not in st.session_state:
        st.session_state.comorbidades_selecionadas = []
    if 'nova_comorbidade' not in st.session_state:
        st.session_state.nova_comorbidade = ""
    
    # Seção 1: Dados do Paciente
    with st.form("dados_paciente_form"):
        st.subheader("Dados do Paciente")
        
        # Dados básicos
        col1, col2, col3 = st.columns(3)
        with col1:
            nome = st.text_input("Nome do paciente", placeholder="Ex.: Maria Souza", key="nome_paciente")
        with col2:
            data_consulta = st.date_input("Data da consulta", key="data_consulta")
        with col3:
            idade = st.number_input("Idade (anos)", min_value=0, max_value=130, value=0, key="idade")
        
        # Dados físicos - ALTURA EM CM
        col1, col2 = st.columns(2)
        with col1:
            sexo = st.selectbox("Sexo", ["Masculino", "Feminino"], key="sexo")
            altura_cm = st.number_input("Altura (cm)", min_value=50, max_value=250, value=170, key="altura_cm")
        with col2:
            peso = st.number_input("Peso (kg)", min_value=0.0, max_value=500.0, value=70.0, step=0.1, key="peso")
        
        # Cálculo do IMC
        altura_m = cm_para_metros(altura_cm)
        imc = calcular_imc(peso, altura_cm)
        imc_class = classificar_imc(imc)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("IMC", f"{imc if imc else '—'}")
        with col2:
            st.metric("Classificação", imc_class if imc_class else "—")
        
        # Mostrar altura em metros também para referência
        st.info(f"📏 Altura: {altura_cm} cm = {altura_m:.2f} m")
        
        # Botão para salvar dados básicos
        salvar_dados = st.form_submit_button("💾 Salvar Dados do Paciente", use_container_width=True)
        
        if salvar_dados:
            if not nome:
                st.error("Informe o nome do paciente.")
            elif not data_consulta:
                st.error("Informe a data da consulta.")
            elif idade <= 0:
                st.error("Informe uma idade válida.")
            elif altura_cm <= 0:
                st.error("Informe uma altura válida.")
            elif peso <= 0:
                st.error("Informe um peso válido.")
            else:
                st.session_state.dados_paciente = {
                    "nome": nome,
                    "data_consulta": data_consulta,
                    "idade": idade,
                    "sexo": sexo,
                    "altura_cm": altura_cm,
                    "altura_m": altura_m,
                    "peso": peso,
                    "imc": imc,
                    "imc_class": imc_class,
                    "nome_arquivo": formatar_nome_arquivo(nome, data_consulta)
                }
                st.success("Dados do paciente salvos com sucesso!")
    
    # Seção 2: Comorbidades
    st.markdown("---")
    st.subheader("Comorbidades")
    st.markdown("<p style='color: #94a3b8;'>Ative as que se aplicam ao paciente.</p>", unsafe_allow_html=True)
    
    # Busca
    busca = st.text_input("🔍 Pesquisar comorbidade...", placeholder="Digite para filtrar...", key="busca_comorb")
    
    # Comorbidades por categoria
    comorbidades_temp = st.session_state.comorbidades_selecionadas.copy()
    
    for categoria, comorbidades in CATEGORIES.items():
        comorbidades_filtradas = {
            key: value for key, value in comorbidades.items() 
            if not busca or busca.lower() in value.lower() or busca.lower() in key.lower()
        }
        
        if comorbidades_filtradas:
            with st.expander(f"{categoria} ({len(comorbidades_filtradas)})"):
                items = list(comorbidades_filtradas.items())
                for i in range(0, len(items), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(items):
                            key, value = items[i + j]
                            unique_key = f"comorb_{categoria}_{key}"
                            checked = st.checkbox(value, key=unique_key, value=key in comorbidades_temp)
                            if checked and key not in comorbidades_temp:
                                comorbidades_temp.append(key)
                            elif not checked and key in comorbidades_temp:
                                comorbidades_temp.remove(key)
    
    # Comorbidade personalizada
    st.markdown("---")
    st.subheader("Comorbidade Personalizada")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        nova_comorb = st.text_input(
            "Adicionar comorbidade personalizada", 
            placeholder="Ex.: Doença tireoidiana",
            key="nova_comorb_input",
            value=st.session_state.get('nova_comorbidade', '')
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Adicionar", key="btn_add_comorb", use_container_width=True):
            if nova_comorb and nova_comorb not in comorbidades_temp:
                comorbidades_temp.append(nova_comorb)
                st.session_state.nova_comorbidade = ""
                st.session_state.comorbidades_selecionadas = comorbidades_temp
                st.success(f"Comorbidade '{nova_comorb}' adicionada!")
                st.rerun()
            elif not nova_comorb:
                st.error("Digite uma comorbidade para adicionar.")
    
    # Atualizar comorbidades selecionadas
    st.session_state.comorbidades_selecionadas = comorbidades_temp
    
    # Botão para calcular probabilidade
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 Calcular Probabilidade", use_container_width=True, type="primary"):
            if 'dados_paciente' not in st.session_state:
                st.error("Por favor, salve os dados do paciente primeiro.")
            else:
                dados = st.session_state.dados_paciente
                
                # Prepara payload para a API - CORRIGIDO
                payload = {
                    "nome": dados["nome"],
                    "data": dados["data_consulta"].strftime("%Y-%m-%d"),
                    "idade": float(dados["idade"]),
                    "sexo": "F" if dados["sexo"] == "Feminino" else "M",
                    "altura": float(dados["altura_m"]),  # Enviar em metros para o modelo
                    "peso": float(dados["peso"]),
                    "comorbidades": st.session_state.comorbidades_selecionadas
                }
                
                # Mostra resumo
                st.markdown("---")
                st.subheader("📋 Resumo da Consulta")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Paciente:** {dados['nome']}")
                    st.write(f"**Data:** {dados['data_consulta'].strftime('%d/%m/%Y')}")
                    st.write(f"**Idade:** {dados['idade']} anos")
                    st.write(f"**Sexo:** {dados['sexo']}")
                with col2:
                    st.write(f"**Altura:** {dados['altura_cm']} cm ({dados['altura_m']:.2f} m)")
                    st.write(f"**Peso:** {dados['peso']} kg")
                    st.write(f"**IMC:** {dados['imc']} — {dados['imc_class']}")
                    st.write(f"**Comorbidades:** {len(st.session_state.comorbidades_selecionadas)} selecionadas")
                
                # Mostra comorbidades selecionadas
                if st.session_state.comorbidades_selecionadas:
                    st.write("**Comorbidades selecionadas:**")
                    comorb_html = ""
                    for comorb in st.session_state.comorbidades_selecionadas:
                        label_pt = comorb
                        for cat_comorbidades in CATEGORIES.values():
                            if comorb in cat_comorbidades:
                                label_pt = cat_comorbidades[comorb]
                                break
                        comorb_html += f'<span class="pill">{label_pt}</span> '
                    st.markdown(comorb_html, unsafe_allow_html=True)
                
                # Faz a predição
                with st.spinner("🔄 Calculando probabilidade de diabetes..."):
                    resultado = fazer_predicao(payload)
                
                if "error" in resultado:
                    st.error(f"❌ Erro na predição: {resultado['error']}")
                    
                    # Informações adicionais para debug
                    with st.expander("🔧 Informações para Debug"):
                        st.write("**Payload enviado:**")
                        st.json(payload)
                        st.write("**Resposta do servidor:**")
                        st.write(resultado)
                        
                        # Verificação de conexão
                        BACKEND_URL = os.getenv('BACKEND_URL', 'http://modelo-back:5000')
                        st.write("**Verificação de conexão:**")
                        try:
                            test_response = requests.get("http://localhost:5000/", timeout=5)
                            st.write(f"Status do servidor: {test_response.status_code}")
                        except Exception as e:
                            st.write(f"Servidor não alcançável: {e}")
                            
                else:
                    probabilidade = resultado["probabilidade"]
                    pdf_url = resultado.get("pdf_url", "")
                    
                    st.markdown(f"""
                    <div class='result-box'>
                        <h3 style='color: #22d3ee; margin-top: 0;'>🎯 Resultado da Predição</h3>
                        <p style='font-size: 24px; font-weight: bold; color: #60a5fa;'>
                            Probabilidade de Diabetes Tipo 2: {probabilidade:.2f}%
                        </p>
                        <p style='color: #94a3b8; font-size: 14px;'>
                            Arquivo PDF: {dados['nome_arquivo']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if pdf_url:
                        st.success(f"📄 PDF gerado: [Baixar PDF](http://localhost:5000{pdf_url})")
    
    with col2:
        if st.button("🧹 Limpar Tudo", use_container_width=True):
            for key in ['dados_paciente', 'comorbidades_selecionadas', 'nova_comorbidade']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Botão para voltar ao menu
    if st.button("↩️ Voltar ao Menu", key="voltar_menu"):
        st.session_state.current_page = "menu"
        st.rerun()

# Gerenciamento de estado da sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"

# Navegação entre páginas
if st.session_state.current_page == "cadastro":
    cadastro_page()
elif not st.session_state.logged_in:
    login_page()
else:
    if st.session_state.current_page == "menu":
        menu_page()
    elif st.session_state.current_page == "datacare":
        datacare_page()