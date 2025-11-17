# Carrega modelo
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Modelo não encontrado: {MODEL_PATH}")

# DIAGNÓSTICO - Adicione estas linhas
print("🔍 Iniciando diagnóstico do modelo...")
print(f"📁 Caminho do modelo: {MODEL_PATH}")
print(f"📊 Tamanho do arquivo: {os.path.getsize(MODEL_PATH)} bytes")

try:
    model = joblib.load(MODEL_PATH)
    print("✅ Modelo carregado com sucesso!")
    
    # Verifica se o modelo está treinado
    print(f"📋 Tipo do modelo: {type(model)}")
    print(f"🔧 Atributos do modelo: {dir(model)}")
    
    if hasattr(model, 'n_features_in_'):
        print(f"🎯 Número de features esperadas: {model.n_features_in_}")
    else:
        print("⚠️ Modelo não tem atributo n_features_in_")
        
    if hasattr(model, 'predict'):
        print("✅ Modelo tem método predict")
    else:
        print("❌ Modelo NÃO tem método predict")
        
except Exception as e:
    print(f"❌ Erro ao carregar modelo: {e}")
    # Usa modelo simulado como fallback
    print("🔄 Usando simulador como fallback...")
    model = None