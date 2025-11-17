🏥 DataCare - Sistema de Predição de Risco de Diabetes
📋 Sobre o Projeto

O DataCare é um sistema completo para avaliação de risco de Diabetes Tipo 2, desenvolvido para auxiliar profissionais de saúde na identificação precoce de pacientes com maior probabilidade de desenvolver a doença.
🎯 Funcionalidades Principais

    📊 Avaliação de Risco: Calcula probabilidade de Diabetes Tipo 2 usando Machine Learning

    👥 Cadastro de Pacientes: Interface completa para registro de dados clínicos

    🏷️ Comorbidades: Catálogo organizado de 70+ condições médicas

    📄 Relatórios PDF: Geração automática de relatórios em português

    💾 Persistência: Armazenamento em banco de dados SQLite

🏗️ Arquitetura do Sistema
Backend (Flask)

    Framework: Flask + CORS

    Modelo ML: Gradient Boosting Classifier

    Banco de Dados: SQLite

    PDF: ReportLab para geração de relatórios

    Porta: 5000

Frontend (Streamlit)

    Framework: Streamlit

    Interface: Web-based responsiva

    Comunicação: REST API com backend

    Porta: 8501

📁 Estrutura do Projeto
text

datacare/
├── 📋 README.md                 # Este arquivo
├── 🐳 docker-compose.yml        # Orquestração de containers
├── 🔧 Dockerfile               # Imagem Docker única
├── 📦 requirements.txt         # Dependências Python
├── 🚀 app.py                   # Backend Flask
├── 🎨 streamlit_app.py         # Frontend Streamlit
├── 🤖 modelo_gradient_boosting.pkl  # Modelo de ML treinado
├── 💾 consultas.db             # Banco de dados (gerado automaticamente)
└── 📁 consultas/               # Pasta de PDFs (gerada automaticamente)

⚙️ Configuração e Instalação
Pré-requisitos

    Docker

    Docker Compose

🚀 Execução Rápida

    Clone o repositório:

bash

git clone <seu-repositorio>
cd datacare

    Execute com Docker:

bash

docker-compose up --build

    Acesse as aplicações:

        Frontend: http://localhost:8501

        Backend: http://localhost:5000

🔧 Execução Manual (Sem Docker)

    Instale as dependências:

bash

pip install -r requirements.txt

    Execute o backend:

bash

python app.py

    Execute o frontend (em outro terminal):

bash

streamlit run streamlit_app.py

📊 Como Usar o Sistema
1. 🏠 Página Inicial (Streamlit)

    Acesse http://localhost:8501

    Interface intuitiva para cadastro de consultas

2. 📝 Cadastro de Paciente

    Nome completo do paciente

    Data da consulta

    Idade em anos

    Sexo (Masculino/Feminino)

    Altura em metros

    Peso em kg

3. 🏷️ Seleção de Comorbidades

    Busca por nome da condição

    Categorias organizadas:

        Cardiovasculares

        Neurológicas

        Endócrinas/Metabólicas

        Renais/Hepáticas

        Hematológicas/Imunológicas

        Autoimunes/Inflamatórias

        Oncológicas

        Genéticas/Congênitas

        Outras

4. 🎯 Cálculo de Risco

    Clique em "Calcular Probabilidade"

    Sistema processa os dados usando IA

    Retorna probabilidade em porcentagem

5. 📄 Geração de PDF

    Relatório completo em português

    Dados do paciente

    Comorbidades selecionadas

    Resultado da predição

    Download automático

🔌 API Endpoints
Backend Flask (http://localhost:5000)
Método	Endpoint	Descrição
GET	/	Página inicial do backend
POST	/predict	Predição de risco de diabetes
GET	/consultas/<filename>	Download de PDF
Exemplo de Request para Predição
json

POST /predict
{
  "nome": "João Silva",
  "data": "2024-01-15",
  "idade": 45,
  "sexo": "M",
  "altura": 1.75,
  "peso": 80.0,
  "comorbidades": ["obesity", "SAH", "dyslipidemia"]
}

Exemplo de Response
json

{
  "probabilidade": 23.45,
  "pdf_url": "/consultas/consulta_Joao_Silva_2024-01-15.pdf"
}

🐳 Configuração Docker
Serviços Definidos
modelo-back

    Porta: 5000

    Healthcheck: Verifica disponibilidade do backend

    Dependências: Flask, scikit-learn, pandas

streamlit-front

    Porta: 8501

    Dependências: Streamlit, requests

    Depende do: modelo-back

Comandos Úteis
bash

# Build e execução
docker-compose up --build

# Execução em background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Rebuild específico
docker-compose build modelo-back

🎯 Modelo de Machine Learning
Características

    Algoritmo: Gradient Boosting Classifier

    Features: 72 características (idade, sexo + 70 comorbidades)

    Treinamento: Dados sintéticos baseados em regras clínicas

    Saída: Probabilidade entre 0-100%

Variáveis do Modelo

    patient_age: Idade do paciente

    patient_sex: Sexo (1=Masculino, 2=Feminino)

    70 comorbidades binárias (0=Não, 1=Sim)

📊 Exemplo de Uso
Caso Clínico Exemplo

    Paciente: Maria Santos, 52 anos, sexo feminino

    Medidas: 1.62m, 68kg (IMC: 25.9)

    Comorbidades:

        Obesidade

        Hipertensão Arterial

        Dislipidemia

    Resultado: Probabilidade de 34.2% de diabetes

PDF Gerado

O sistema produz um relatório profissional contendo:

    Dados demográficos do paciente

    Medidas antropométricas

    Lista de comorbidades em português

    Probabilidade calculada

    Data e hora da geração

🛠️ Desenvolvimento
Adicionando Nova Comorbidade

    Adicione no array FEATURE_NAMES em app.py

    Adicione tradução em EN_TO_PT

    Adicione na categoria apropriada em CATEGORIES no Streamlit

Modificando o Modelo

    Substitua modelo_gradient_boosting.pkl por novo modelo treinado

    Mantenha a mesma estrutura de features

Customizando o PDF

    Edite a função generate_pdf() em app.py

    Use ReportLab para modificações de layout

🔒 Considerações de Segurança

    CORS configurado para comunicação entre serviços

    Validação de dados de entrada

    Arquivos PDF gerados localmente

    Banco de dados SQLite com schema definido

📈 Próximas Melhorias

    Autenticação de usuários

    Dashboard com estatísticas

    Exportação de dados em CSV

    Histórico de consultas por paciente

    Integração com prontuários eletrônicos

🐛 Solução de Problemas
Erro Comum: Modelo não carregado
bash

# Verifique se o arquivo .pkl existe
ls -la modelo_gradient_boosting.pkl

# Reinstale scikit-learn se necessário
pip install --force-reinstall scikit-learn

Erro de Porta em Uso
bash

# Encerre processos nas portas
sudo lsof -ti:5000 | xargs kill -9
sudo lsof -ti:8501 | xargs kill -9

Problemas com Docker
bash

# Limpe containers antigos
docker-compose down --volumes --remove-orphans

# Rebuild completo
docker-compose build --no-cache

📞 Suporte

Para issues e contribuições:

    Verifique a documentação

    Confirme a estrutura de arquivos

    Teste com docker-compose primeiro

📄 Licença

Este projeto é destinado para fins educacionais e de pesquisa médica.

Desenvolvido para auxiliar profissionais de saúde na prevenção do Diabetes Tipo 2 🩺💙