# criar_modelo_valido.py
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
import joblib

# Feature names do seu código
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

def criar_dados_treinamento(n_amostras=1000):
    """Cria dados sintéticos para treinar o modelo"""
    np.random.seed(42)
    
    # Dados básicos
    data = {
        'patient_age': np.random.normal(50, 15, n_amostras),
        'patient_sex': np.random.choice([1, 2], n_amostras),
    }
    
    # Adiciona features binárias (comorbidades)
    for feature in FEATURE_NAMES[2:]:  # Pula age e sex
        # Probabilidades realistas para comorbidades
        if feature in ['obesity', 'SAH', 'dyslipidemia']:
            data[feature] = np.random.choice([0, 1], n_amostras, p=[0.7, 0.3])
        else:
            data[feature] = np.random.choice([0, 1], n_amostras, p=[0.9, 0.1])
    
    df = pd.DataFrame(data)
    
    # Cria target (diabetes) baseado em regras clínicas
    # Idade > 45, obesidade, HAS e dislipidemia são fatores de risco
    risk_factors = (
        (df['patient_age'] > 45) * 0.3 +
        (df['obesity'] == 1) * 0.4 +
        (df['SAH'] == 1) * 0.2 +
        (df['dyslipidemia'] == 1) * 0.1 +
        np.random.normal(0, 0.1, n_amostras)
    )
    
    # Converte para probabilidade e cria target binário
    diabetes_prob = 1 / (1 + np.exp(-risk_factors))
    df['diabetes'] = (diabetes_prob > 0.5).astype(int)
    
    return df

print("🎯 Criando dados de treinamento...")
df = criar_dados_treinamento(2000)

print(f"📊 Shape dos dados: {df.shape}")
print(f"🎯 Distribuição do target: {df['diabetes'].value_counts()}")

# Separa features e target
X = df[FEATURE_NAMES]
y = df['diabetes']

print("🤖 Treinando modelo Gradient Boosting...")
model = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.1,
    random_state=42
)

# Treina o modelo
model.fit(X, y)

print(f"✅ Modelo treinado com sucesso!")
print(f"📈 Acurácia no treinamento: {model.score(X, y):.3f}")
print(f"🔧 Número de features: {model.n_features_in_}")

# Salva o modelo
print("💾 Salvando modelo...")
joblib.dump(model, 'modelo_gradient_boosting.pkl')

# Verifica se salvou corretamente
print("🔍 Verificando modelo salvo...")
model_loaded = joblib.load('modelo_gradient_boosting.pkl')
print(f"✅ Modelo carregado: {type(model_loaded)}")
print(f"🎯 Teste de predição: {model_loaded.predict(X[:1])}")

print("🎉 Modelo criado e validado com sucesso!")