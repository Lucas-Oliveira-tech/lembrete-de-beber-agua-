import json
import tkinter as tk
from tkinter import messagebox
import threading
import time

# Função para registrar o usuário no JSON
def registrar_usuario(username, password):
    try:
        with open('usuarios.json', 'r') as file:
            usuarios = json.load(file)
    except FileNotFoundError:
        usuarios = {}

    if username in usuarios:
        messagebox.showerror("Erro", "Usuário já existe!")
    else:
        usuarios[username] = {'senha': password, 'meta': 0, 'progresso': 0}
        with open('usuarios.json', 'w') as file:
            json.dump(usuarios, file)
        messagebox.showinfo("Sucesso", "Usuário registrado com sucesso!")

# Função para realizar o login
def fazer_login(username, password):
    try:
        with open('usuarios.json', 'r') as file:
            usuarios = json.load(file)
    except FileNotFoundError:
        usuarios = {}

    if username in usuarios and usuarios[username]['senha'] == password:
        return True
    else:
        messagebox.showerror("Erro", "Usuário ou senha incorretos.")
        return False

# Função para atualizar a meta de água no JSON
def atualizar_meta(username, meta):
    with open('usuarios.json', 'r') as file:
        usuarios = json.load(file)
    usuarios[username]['meta'] = meta
    usuarios[username]['progresso'] = 0  # Resetando o progresso ao definir uma nova meta
    with open('usuarios.json', 'w') as file:
        json.dump(usuarios, file)

# Função para registrar o consumo de água
def registrar_consumo(username):
    with open('usuarios.json', 'r') as file:
        usuarios = json.load(file)
    
    if usuarios[username]['progresso'] < usuarios[username]['meta']:
        usuarios[username]['progresso'] += 1
        with open('usuarios.json', 'w') as file:
            json.dump(usuarios, file)
        return True
    else:
        messagebox.showinfo("Parabéns!", "Você já atingiu sua meta de água diária!")
        return False

# Função para desfazer o consumo de água
def desfazer_consumo(username):
    with open('usuarios.json', 'r') as file:
        usuarios = json.load(file)
    
    if usuarios[username]['progresso'] > 0:
        usuarios[username]['progresso'] -= 1
        with open('usuarios.json', 'w') as file:
            json.dump(usuarios, file)
        return True
    else:
        messagebox.showinfo("Erro", "Você ainda não registrou nenhum copo de água.")
        return False

# Função para lembrar o usuário de beber água
def lembrete_beber_agua(username, intervalo, parar_evento):
    while not parar_evento.is_set():
        time.sleep(intervalo)
        messagebox.showinfo("Lembrete", "Hora de beber água!")
        parar_evento.wait(intervalo)

# Interface principal após login
def interface_principal(username):
    window = tk.Tk()
    window.title("Lembrete de Hidratação")

    # Variáveis de controle para o tema
    tema_atual = {"fundo": "white", "texto": "black", "botao": "lightgray"}

    def alterar_tema():
        """Altera entre tema claro e escuro."""
        if tema_atual["fundo"] == "white":
            tema_atual["fundo"] = "black"
            tema_atual["texto"] = "white"
            tema_atual["botao"] = "gray"
        else:
            tema_atual["fundo"] = "white"
            tema_atual["texto"] = "black"
            tema_atual["botao"] = "lightgray"
        aplicar_tema()

    def aplicar_tema():
        """Aplica o tema a todos os elementos da interface."""
        window.configure(bg=tema_atual["fundo"])
        for widget in window.winfo_children():
            widget.configure(bg=tema_atual["fundo"], fg=tema_atual["texto"])
            if isinstance(widget, tk.Button):
                widget.configure(bg=tema_atual["botao"])

    # Mostrar nome do usuário
    tk.Label(window, text=f"Bem-vindo, {username}").pack()

    # Campo para definir a meta
    tk.Label(window, text="Defina sua meta de copos de água por dia:").pack()
    meta_entry = tk.Entry(window)
    meta_entry.pack()

    def definir_meta():
        meta = int(meta_entry.get())
        if meta > 0:
            atualizar_meta(username, meta)
            messagebox.showinfo("Sucesso", f"Meta de {meta} copos definida!")
            atualizar_progresso(username)
        else:
            messagebox.showerror("Erro", "A meta deve ser maior que zero.")

    tk.Button(window, text="Definir Meta", command=definir_meta).pack()

    # Criando a barra de progresso personalizada usando Canvas
    canvas = tk.Canvas(window, width=300, height=30)
    canvas.pack()

    # Label para mostrar a porcentagem
    porcentagem_label = tk.Label(window, text="0%")
    porcentagem_label.pack()

    # Função para atualizar a barra de progresso
    def atualizar_progresso(username):
        with open('usuarios.json', 'r') as file:
            usuarios = json.load(file)
        progresso = usuarios[username]['progresso']
        meta = usuarios[username]['meta']
        
        # Limpar o canvas e redesenhar a barra de progresso
        canvas.delete("all")
        canvas.create_rectangle(0, 0, 300, 30, outline="black", width=2)
        if meta > 0:
            fill_length = int((progresso / meta) * 300)  # Calcula o preenchimento com base no progresso/meta
            canvas.create_rectangle(0, 0, fill_length, 30, fill="blue")
            # Atualizando a porcentagem
            porcentagem = int((progresso / meta) * 100)
            porcentagem_label.config(text=f"{porcentagem}%")
        else:
            canvas.create_rectangle(0, 0, 0, 30, fill="blue")
            porcentagem_label.config(text="0%")

    # Botão para adicionar consumo de água
    def adicionar_copo():
        if registrar_consumo(username):
            atualizar_progresso(username)

    tk.Button(window, text="Adicionar Copo de Água", command=adicionar_copo).pack()

    # Botão para desfazer o consumo de água
    def remover_copo():
        if desfazer_consumo(username):
            atualizar_progresso(username)

    tk.Button(window, text="Remover Copo de Água", command=remover_copo).pack()

    # Campo para definir intervalo do lembrete em minutos
    tk.Label(window, text="Defina o intervalo para o lembrete de beber água (minutos):").pack()
    lembrete_entry = tk.Entry(window)
    lembrete_entry.pack()

    parar_evento = threading.Event()

    # Função para iniciar lembrete
    def iniciar_lembrete():
        intervalo = int(lembrete_entry.get()) * 60  # Convertendo para segundos
        if intervalo > 0:
            parar_evento.clear()
            threading.Thread(target=lembrete_beber_agua, args=(username, intervalo, parar_evento)).start()
            messagebox.showinfo("Lembrete", f"Lembrete configurado para cada {intervalo // 60} minutos.")
        else:
            messagebox.showerror("Erro", "O intervalo deve ser maior que zero.")

    tk.Button(window, text="Iniciar Lembrete", command=iniciar_lembrete).pack()

    # Função para parar o lembrete
    def parar_lembrete():
        parar_evento.set()
        messagebox.showinfo("Lembrete", "Lembrete de beber água parado.")

    tk.Button(window, text="Parar Lembrete", command=parar_lembrete).pack()

    # Botão para alternar o tema
    tk.Button(window, text="Alternar Tema", command=alterar_tema).pack()

    # Atualiza a barra de progresso inicial com os dados do usuário
    atualizar_progresso(username)
    aplicar_tema()  # Aplicando o tema inicial
    window.mainloop()

# Função da interface de login
def interface_login():
    window = tk.Tk()
    window.title("Login")

    tk.Label(window, text="Usuário").pack()
    username_entry = tk.Entry(window)
    username_entry.pack()

    tk.Label(window, text="Senha").pack()
    password_entry = tk.Entry(window, show="*")
    password_entry.pack()

    def tentar_login():
        username = username_entry.get()
        password = password_entry.get()
        if fazer_login(username, password):
            window.destroy()
            interface_principal(username)

    tk.Button(window, text="Login", command=tentar_login).pack()
    tk.Button(window, text="Registrar", command=lambda: [window.destroy(), interface_registro()]).pack()

    window.mainloop()

# Função da interface de registro
def interface_registro():
    window = tk.Tk()
    window.title("Registrar")

    tk.Label(window, text="Usuário").pack()
    username_entry = tk.Entry(window)
    username_entry.pack()

    tk.Label(window, text="Senha").pack()
    password_entry = tk.Entry(window, show="*")
    password_entry.pack()

    def registrar():
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            registrar_usuario(username, password)
            window.destroy()
        else:
            messagebox.showerror("Erro", "Preencha todos os campos.")

    tk.Button(window, text="Registrar", command=registrar).pack()
    window.mainloop()

# Início do programa
if __name__ == "__main__":
    interface_login()
