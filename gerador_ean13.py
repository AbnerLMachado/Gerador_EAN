# gerador_ean13.py
import random
import string
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import pyperclip  # opcional: pip install pyperclip

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
        messagebox.showwarning("Aviso",
                               "Não foi possível gerar todos os EAN pedidos.\n"
                               "Tente novamente ou reduza a quantidade.")
    return gerados

# ----------------- INTERFACE ------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de EAN-13 (prefixo 789)")
        self.geometry("500x400")
        self.resizable(False, False)

        # Quantidade
        tk.Label(self, text="Quantidade (1-50):").pack(pady=5)
        self.qty_var = tk.IntVar(value=5)
        tk.Spinbox(self, from_=1, to=50, textvariable=self.qty_var, width=5).pack()

        # Setor
        tk.Label(self, text="Selecione o setor:").pack(pady=5)
        self.setor_var = tk.StringVar(value=list(SETORES.keys())[0])
        ttk.Combobox(self, values=list(SETORES.keys()),
                     textvariable=self.setor_var,
                     state="readonly", width=30).pack()

        # Botão gerar
        tk.Button(self, text="Gerar EAN-13", command=self.acao_gerar).pack(pady=10)

        # Campo resultado
        self.txt = tk.Text(self, height=12, width=45)
        self.txt.pack(padx=10, pady=10)

        # Copiar
        tk.Button(self, text="Copiar Todos", command=self.copiar).pack()

    def acao_gerar(self):
        self.txt.delete("1.0", tk.END)
        eans = gerar_eans(self.setor_var.get(), self.qty_var.get())
        self.txt.insert(tk.END, "\n".join(eans))

    def copiar(self):
        conteudo = self.txt.get("1.0", tk.END).strip()
        if conteudo:
            try:
                import pyperclip
                pyperclip.copy(conteudo)
                messagebox.showinfo("Copiado", "Códigos copiados para a área de transferência.")
            except Exception:
                self.clipboard_clear()
                self.clipboard_append(conteudo)
                messagebox.showinfo("Copiado", "Códigos copiados para a área de transferência.")
        else:
            messagebox.showwarning("Vazio", "Não há códigos para copiar.")

if __name__ == "__main__":
    App().mainloop()
