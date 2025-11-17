import os
import sqlite3
import json
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory, url_for, jsonify
import joblib
import pandas as pd
import numpy as np
import logging
from flask_cors import CORS  # para permitir acesso do popup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_ROOT = os.path.dirname(__file__)
MODEL_PATH = os.path.join(APP_ROOT, "modelo_gradient_boosting.pkl")
DB_PATH = os.path.join(APP_ROOT, "consultas.db")
PDF_DIR = os.path.join(APP_ROOT, "consultas")
os.makedirs(PDF_DIR, exist_ok=True)

app = Flask(__name__, template_folder=".")
CORS(app)  # permite requisições cross-origin do popup

# --- Feature names confirmadas
FEATURE_NAMES = [
    "patient_age","patient_sex","SAH","acute myocardium infarct","adrenal hypoplasia","albinism",
    "alzheimer","anemia","aneurysm","ankylosing spondylitis","arrhythmia","arthrosis","asthma",
    "behcet","brain tumor","breast cancer","cardiac insufficiency","cardiopathy","catheterism",
    "cerebral palsy","chron disease","chronic kidney disease","cirrhosis","cone dystrophy","devic",
    "dialysis","down syndrome","dyslipidemia","fibromyalgia","hashimoto disease","hepatic cancer",
    "hepatic transplant","hepatitis c","herpetic encephalitis","hipocolesterolemia",
    "human immunodeficiency virus","hydrocephalus","hypercholesterolemia","hypertriglyceridemia",
    "hypophysis adenoma","intestinal cancer","intracranial hypertension","kidney transplant","leucemia",
    "lung cancer","lymphoma","mccune albright","meningioma","migraine","muscular dystrophy",
    "neurofibromatosis","obesity","osteoporosis","policitemia vera","prolactinoma","prostatic hyperplasia",
    "psoriasis","pulmonary embolism","sarcoidosis","sickle cell anemia","sjogren","tabagism",
    "valvulopathy","vasculitis","vitiligo","AVC","doenca_chagas","trombose_venosa_profunda",
    "cloroquina","hipotireoidismo","hipertireoidismo","esclerose_multipla","artrite"
]

# EN->PT para labels PDF
EN_TO_PT = {
    "patient_age": "Idade",
    "patient_sex": "Sexo",
    "SAH": "Hipertensão Arterial Sistêmica (HAS)",
    "acute myocardium infarct": "Infarto Agudo do Miocárdio",
    "adrenal hypoplasia": "Hipoplasia Adrenal",
    "albinism": "Albinismo",
    "alzheimer": "Alzheimer",
    "anemia": "Anemia",
    "aneurysm": "Aneurisma",
    "ankylosing spondylitis": "Espondilite Anquilosante",
    "arrhythmia": "Arritmia",
    "arthrosis": "Artrose",
    "asthma": "Asma",
    "behcet": "Doença de Behçet",
    "brain tumor": "Tumor Cerebral",
    "breast cancer": "Câncer de Mama",
    "cardiac insufficiency": "Insuficiência Cardíaca",
    "cardiopathy": "Cardiopatia",
    "catheterism": "Cateterismo",
    "cerebral palsy": "Paralisia Cerebral",
    "chron disease": "Doença de Crohn",
    "chronic kidney disease": "Doença Renal Crônica",
    "cirrhosis": "Cirrose",
    "cone dystrophy": "Distrofia de Cones",
    "devic": "Síndrome de Devic",
    "dialysis": "Diálise",
    "down syndrome": "Síndrome de Down",
    "dyslipidemia": "Dislipidemia",
    "fibromyalgia": "Fibromialgia",
    "hashimoto disease": "Doença de Hashimoto",
    "hepatic cancer": "Câncer Hepático",
    "hepatic transplant": "Transplante Hepático",
    "hepatitis c": "Hepatite C",
    "herpetic encephalitis": "Encefalite Herpética",
    "hipocolesterolemia": "Hipocolesterolemia",
    "human immunodeficiency virus": "HIV",
    "hydrocephalus": "Hidrocefalia",
    "hypercholesterolemia": "Hipercolesterolemia",
    "hypertriglyceridemia": "Hipertrigliceridemia",
    "hypophysis adenoma": "Adenoma de Hipófise",
    "intestinal cancer": "Câncer Intestinal",
    "intracranial hypertension": "Hipertensão Intracraniana",
    "kidney transplant": "Transplante Renal",
    "leucemia": "Leucemia",
    "lung cancer": "Câncer de Pulmão",
    "lymphoma": "Linfoma",
    "mccune albright": "Síndrome de McCune-Albright",
    "meningioma": "Meningioma",
    "migraine": "Enxaqueca",
    "muscular dystrophy": "Distrofia Muscular",
    "neurofibromatosis": "Neurofibromatose",
    "obesity": "Obesidade",
    "osteoporosis": "Osteoporose",
    "policitemia vera": "Policitemia Vera",
    "prolactinoma": "Prolactinoma",
    "prostatic hyperplasia": "Hiperplasia Prostática",
    "psoriasis": "Psoríase",
    "pulmonary embolism": "Embolia Pulmonar",
    "sarcoidosis": "Sarcoidose",
    "sickle cell anemia": "Anemia Falciforme",
    "sjogren": "Síndrome de Sjögren",
    "tabagism": "Tabagismo",
    "valvulopathy": "Valvulopatia",
    "vasculitis": "Vasculite",
    "vitiligo": "Vitiligo",
    "AVC": "Acidente Vascular Cerebral (AVC)",
    "doenca_chagas": "Doença de Chagas",
    "trombose_venosa_profunda": "Trombose Venosa Profunda",
    "cloroquina": "Uso de Cloroquina",
    "hipotireoidismo": "Hipotireoidismo",
    "hipertireoidismo": "Hipertireoidismo",
    "esclerose_multipla": "Esclerose Múltipla",
    "artrite": "Artrite"
}

# Carrega modelo
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Modelo não encontrado: {MODEL_PATH}")
model = joblib.load(MODEL_PATH)

# DB init
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS consultas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        data_consulta TEXT,
        patient_age REAL,
        patient_sex INTEGER,
        altura REAL,
        peso REAL,
        imc REAL,
        comorbidades_json TEXT,
        probabilidade REAL,
        pdf_path TEXT,
        created_at TEXT
    )
    ''')
    conn.commit()
    conn.close()
init_db()

# PDF generator simples
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_pdf(consulta_info: dict, selected_names_pt: list, prob: float, filename: str):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin
    
    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Relatório de Consulta - Avaliação de Risco de Diabetes")
    y -= 30
    
    # Informações do paciente
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Dados do Paciente:")
    y -= 20
    
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Nome: {consulta_info.get('nome', '-')}")
    c.drawString(width/2, y, f"Data da Consulta: {consulta_info.get('data_consulta', '-')}")
    y -= 15
    
    c.drawString(margin, y, f"Idade: {consulta_info.get('patient_age', '-')} anos")
    c.drawString(width/2, y, f"Sexo: {'Masculino' if consulta_info.get('patient_sex', 1) == 1 else 'Feminino'}")
    y -= 15
    
    # Converter altura para cm para exibição
    altura_m = consulta_info.get('altura', 0)
    altura_cm = altura_m * 100 if altura_m else 0
    c.drawString(margin, y, f"Altura: {altura_cm:.0f} cm ({altura_m:.2f} m)")
    c.drawString(width/2, y, f"Peso: {consulta_info.get('peso', '-')} kg")
    y -= 15
    
    c.drawString(margin, y, f"IMC: {consulta_info.get('imc', '-')}")
    y -= 25
    
    # Resultado da predição
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Resultado da Avaliação:")
    y -= 20
    
    c.setFont("Helvetica", 12)
    c.drawString(margin, y, f"Probabilidade de Diabetes Tipo 2: {prob:.2f}%")
    y -= 25
    
    # Comorbidades
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Comorbidades Identificadas:")
    y -= 20
    
    c.setFont("Helvetica", 10)
    if selected_names_pt:
        for name in selected_names_pt:
            if y < margin + 50:  # Verifica se precisa de nova página
                c.showPage()
                y = height - margin
                c.setFont("Helvetica-Bold", 12)
                c.drawString(margin, y, "Comorbidades Identificadas (continuação):")
                y -= 20
                c.setFont("Helvetica", 10)
            
            # Usa o nome em português do mapeamento
            nome_pt = EN_TO_PT.get(name, name)
            c.drawString(margin + 10, y, f"• {nome_pt}")
            y -= 14
    else:
        c.drawString(margin + 10, y, "Nenhuma comorbidade identificada")
        y -= 14
    
    # Rodapé
    y = margin + 30
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(margin, y, f"Documento gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    
    c.save()

# Constrói X do modelo
def build_X_from_input(payload: dict):
    selected_en, selected_pt = [], []
    age = float(payload.get('idade') or 0)
    sex_val = 2 if str(payload.get('sexo','M')).strip().lower() in ('f','feminino','female') else 1

    raw_comorb = payload.get('comorbidades') or []
    if isinstance(raw_comorb, str):
        try: 
            raw_comorb = json.loads(raw_comorb)
        except: 
            raw_comorb = []

    for it in raw_comorb:
        if it in FEATURE_NAMES:
            selected_en.append(it)
            # Agora usa o mapeamento completo para português
            selected_pt.append(EN_TO_PT.get(it, it))

    row = {'patient_age': age, 'patient_sex': sex_val}
    for feat in FEATURE_NAMES:
        if feat not in row: 
            row[feat] = 1 if feat in selected_en else 0

    altura = float(payload.get('altura') or 0)
    peso = float(payload.get('peso') or 0)
    imc_val = round(peso/(altura*altura), 1) if altura > 0 else None

    df = pd.DataFrame([row], columns=FEATURE_NAMES)
    meta = {
        'nome': payload.get('nome',''), 
        'data_consulta': payload.get('data',''), 
        'altura': altura, 
        'peso': peso, 
        'imc': imc_val
    }
    return df, meta, selected_en, selected_pt
# Routes
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "message": "DataCare Backend API",
        "endpoints": {
            "predict": "POST /predict - Calcular probabilidade de diabetes",
            "download": "GET /consultas/<filename> - Download de PDF"
        }
    })

@app.route("/predict", methods=["POST"])
def predict():
    try:
        payload = request.get_json()
        X, meta, selected_en, selected_pt = build_X_from_input(payload)

        if hasattr(model, "predict_proba"):
            prob = float(model.predict_proba(X)[:,1][0])
        else:
            prob = float(model.predict(X)[0])

        # gerar PDF
        pdf_basename = f"consulta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(PDF_DIR, pdf_basename)
        generate_pdf({**meta, **X.loc[0].to_dict()}, selected_pt, prob*100, pdf_path)

        # salvar DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO consultas (nome,data_consulta,patient_age,patient_sex,altura,peso,imc,
            comorbidades_json,probabilidade,pdf_path,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            meta['nome'], meta['data_consulta'], float(X.loc[0,'patient_age']),
            int(X.loc[0,'patient_sex']), meta['altura'], meta['peso'], meta['imc'],
            json.dumps(selected_en, ensure_ascii=False), prob, pdf_basename,
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()

        pdf_url = url_for('download_pdf', filename=pdf_basename)
        return jsonify({"probabilidade": round(prob*100, 4), "pdf_url": pdf_url})

    except Exception as e:
        logger.exception("Erro na rota /predict: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route("/consultas/<path:filename>")
def download_pdf(filename):
    return send_from_directory(PDF_DIR, filename, as_attachment=False)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
