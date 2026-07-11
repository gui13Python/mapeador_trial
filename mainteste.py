"""
Tecla Ghost Fix
----------------
Programa para bloquear/remapear teclas com defeito.

Requisitos (instalar antes de gerar o .exe):
    pip install keyboard pystray pillow

Para gerar o executável (recomendado SEM ofuscação/UPX, isso reduz
falsos positivos de antivírus):
    pyinstaller --onefile --noconsole --icon=icon.ico app.py
"""

import tkinter as tk
from tkinter import messagebox
import keyboard as kd
import json
import os
import sys
import threading

# pystray é usado para o ícone na bandeja do sistema (system tray).
# Isso permite "esconder" a janela sem esconder o programa em si:
# o usuário sempre vê o ícone rodando e pode reabrir ou fechar quando quiser.
import pystray
from PIL import Image, ImageDraw

ARQUIVO_CONFIG = "config.json"
NOME_APP = "Tecla Ghost Fix"

# Pasta de inicialização do Windows (usada só se o usuário MARCAR a opção)
STARTUP_PATH = os.path.join(
    os.getenv("APPDATA", ""),
    "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
)
ATALHO_BAT = os.path.join(STARTUP_PATH, "TeclaGhostFix.bat")


# ------------------ SALVAR / CARREGAR ------------------
def salvar_config(dados):
    with open(ARQUIVO_CONFIG, "w") as f:
        json.dump(dados, f, indent=4)


def carregar_config():
    if os.path.exists(ARQUIVO_CONFIG):
        with open(ARQUIVO_CONFIG, "r") as f:
            return json.load(f)
    return {}


# ------------------ AUTO-START (OPCIONAL E VISÍVEL) ------------------
def autostart_ativo():
    return os.path.exists(ATALHO_BAT)


def ativar_autostart():
    """Cria um atalho .bat na pasta Startup do Windows.
    Só roda se o usuário marcar a caixa na interface — nunca automático."""
    try:
        exe_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
        with open(ATALHO_BAT, "w") as f:
            f.write(f'@echo off\nstart "" "{exe_path}"\n')
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível ativar a inicialização automática:\n{e}")


def desativar_autostart():
    try:
        if os.path.exists(ATALHO_BAT):
            os.remove(ATALHO_BAT)
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível remover a inicialização automática:\n{e}")


# ------------------ ÍCONE DA BANDEJA (SYSTEM TRAY) ------------------
def criar_imagem_icone():
    """Gera um ícone simples em memória (substitua por um icon.ico próprio se quiser)."""
    img = Image.new("RGB", (64, 64), "#38bdf8")
    d = ImageDraw.Draw(img)
    d.rectangle((14, 24, 50, 40), fill="white")
    d.text((22, 26), "TK", fill="#38bdf8")
    return img


class App:
    def __init__(self):
        self.janela = tk.Tk()
        self.janela.title(NOME_APP)
        self.janela.geometry("340x420")
        self.janela.resizable(False, False)

        # Fechar pelo "X" também esconde para a bandeja, em vez de rodar
        # oculto sem o usuário saber. O programa SÓ fica realmente
        # invisível se o usuário escolher "Sair" no menu da bandeja.
        self.janela.protocol("WM_DELETE_WINDOW", self.esconder_janela)

        self.icone_bandeja = None
        self.montar_interface()
        self.carregar_e_aplicar()
        self.iniciar_icone_bandeja()

    # ---------- INTERFACE ----------
    def montar_interface(self):
        tk.Label(
            self.janela,
            text=(
                f"{NOME_APP}\n\n"
                "Digite as teclas para remapear abaixo\n"
                "Ex: F1, Ctrl, Alt, a, b, g\n"
                "Em cada campo, apenas uma tecla"
            ),
            justify="center",
        ).pack(pady=10)

        tk.Label(self.janela, text="Bloquear tecla").pack()
        self.entry_block = tk.Entry(self.janela)
        self.entry_block.pack()

        tk.Label(self.janela, text="Remapear de tecla ruim").pack()
        self.entry_from = tk.Entry(self.janela)
        self.entry_from.pack()

        tk.Label(self.janela, text="Remapear por outra tecla").pack()
        self.entry_to = tk.Entry(self.janela)
        self.entry_to.pack()

        tk.Button(self.janela, text="Aplicar", command=self.aplicar_config).pack(pady=10)

        # Caixa de auto-start: visível, explícita, desmarcável
        self.var_autostart = tk.BooleanVar(value=autostart_ativo())
        tk.Checkbutton(
            self.janela,
            text="Iniciar automaticamente com o Windows",
            variable=self.var_autostart,
            command=self.alternar_autostart,
        ).pack(pady=5)

        tk.Label(
            self.janela,
            text=(
                "Este programa fica ativo em segundo plano para bloquear/\n"
                "remapear teclas. Você pode escondê-lo na bandeja do\n"
                "sistema (ícone perto do relógio) a qualquer momento."
            ),
            fg="#555555",
            justify="center",
            wraplength=300,
        ).pack(pady=10)

        tk.Button(
            self.janela,
            text="Ocultar janela (continua rodando na bandeja)",
            command=self.esconder_janela,
        ).pack(pady=5)

        tk.Button(
            self.janela,
            text="Encerrar programa",
            fg="red",
            command=self.encerrar_programa,
        ).pack(pady=5)

    # ---------- AÇÕES ----------
    def aplicar_config(self):
        dados = {
            "bloquear": self.entry_block.get().strip(),
            "remap_de": self.entry_from.get().strip(),
            "remap_para": self.entry_to.get().strip(),
        }
        try:
            if dados["bloquear"]:
                kd.block_key(dados["bloquear"])
            if dados["remap_de"] and dados["remap_para"]:
                kd.remap_key(dados["remap_de"], dados["remap_para"])
            salvar_config(dados)
            messagebox.showinfo("Sucesso", "Configuração salva e aplicada!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def carregar_e_aplicar(self):
        config = carregar_config()
        if not config:
            return
        self.entry_block.insert(0, config.get("bloquear", ""))
        self.entry_from.insert(0, config.get("remap_de", ""))
        self.entry_to.insert(0, config.get("remap_para", ""))
        try:
            if config.get("bloquear"):
                kd.block_key(config["bloquear"])
            if config.get("remap_de") and config.get("remap_para"):
                kd.remap_key(config["remap_de"], config["remap_para"])
        except Exception as e:
            print(f"Aviso ao reaplicar configuração salva: {e}")

    def alternar_autostart(self):
        if self.var_autostart.get():
            ativar_autostart()
        else:
            desativar_autostart()

    # ---------- BANDEJA DO SISTEMA ----------
    def iniciar_icone_bandeja(self):
        menu = pystray.Menu(
            pystray.MenuItem("Abrir " + NOME_APP, self.mostrar_janela, default=True),
            pystray.MenuItem("Sair", self.encerrar_programa),
        )
        self.icone_bandeja = pystray.Icon(NOME_APP, criar_imagem_icone(), NOME_APP, menu)
        threading.Thread(target=self.icone_bandeja.run, daemon=True).start()

    def esconder_janela(self):
        self.janela.withdraw()

    def mostrar_janela(self, icon=None, item=None):
        self.janela.after(0, self.janela.deiconify)

    def encerrar_programa(self, icon=None, item=None):
        try:
            kd.unhook_all()
        except Exception:
            pass
        if self.icone_bandeja:
            self.icone_bandeja.stop()
        self.janela.after(0, self.janela.destroy)
        os._exit(0)

    def run(self):
        self.janela.mainloop()


if __name__ == "__main__":
    App().run()