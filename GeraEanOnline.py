import random
import string
import requests
import streamlit as st

# ----------------- CONSTANTES -----------------
SETORES = {
    "Esporte / Camping": "78910",
    "Beleza & Cuidados": "78920",
    "Utensílios / Armarinho": "78930",
    "Vestuário": "78940"
}

OPENFOOD_URL = "https://world.openfoodfacts.net/api/v2/product/{}.json"
UPCITEMDB_URL = "https://api.upcitemdb.com/prod/trial/lookup?upc={}"

# --------------- FUNÇÕES LÓGICAS --------------
def calc_digito_verificador(ean12: str) -> str:
    total = 0
    for i, ch in enumerate(ean12):
        num = int(ch)
        total += num * (3 if (i % 2) else 1)
    dv = (10 - (total % 10)) % 10
    return str(dv)

def ean_existe_online(ean: str) -> bool:
    # OpenFoodFacts
    try:
        if requests.get(OPENFOOD_URL.format(ean), timeout=3).json().get("status") == 1:
            return True
    except Exception:
        pass
    # UPCitemdb (tem 100 requisições/dia gratuitas)     
    try:
        if requests.get(UPCITEMDB_URL.format(ean), timeout=3).json().get("total", 0) > 0:
            return True
    except Exception:
        pass
    return False

def gerar_eans(setor: str, quantidade: int) -> list[str]:
    prefixo = SETORES[setor]
    gerados = []
    tentativas = 0
    while len(gerados) < quantidade and tentativas < quantidade * 10:
        corpo = prefixo + ''.join(random.choices(string.digits, k=7))  # 12 dígitos
        if corpo in gerados:                    # evita repetição local
            continue
        ean = corpo + calc_digito_verificador(corpo)
        if not ean_existe_online(ean):          # checagem de existência
            gerados.append(ean)
        tentativas += 1
    
    if len(gerados) < quantidade:
        st.warning("Não foi possível gerar todos os EAN pedidos. Tente novamente ou reduza a quantidade.")
    
    return gerados

# ----------------- INTERFACE WEB ------------------
st.set_page_config(page_title="Gerador EAN-13", page_icon="🏷️")

st.title("🏷️ Gerador de EAN-13")
st.write("Gere códigos de barras válidos e não registrados (Prefixo 789).")

# Layout em duas colunas para ficar elegante
col1, col2 = st.columns(2)
with col1:
    setor_var = st.selectbox("Selecione o setor:", list(SETORES.keys()))
with col2:
    qty_var = st.number_input("Quantidade (1-50):", min_value=1, max_value=50, value=5)

# Botão principal
if st.button("Gerar EAN-13", type="primary", use_container_width=True):
    # Mostra um "carregando" enquanto a aplicação faz as consultas na internet
    with st.spinner("Gerando e verificando códigos online (isso pode levar alguns segundos)..."):
        resultados = gerar_eans(setor_var, qty_var)
    
    if resultados:
        st.success(f"{len(resultados)} código(s) gerado(s) com sucesso!")
        
        # Exibe os resultados em um bloco de código com botão de cópia embutido
        codigos_texto = "\n".join(resultados)
        st.code(codigos_texto, language="text")
        
        st.info("💡 Dica: Passe o mouse no canto superior direito da caixa escura acima para ver o botão de 'Copiar'.")