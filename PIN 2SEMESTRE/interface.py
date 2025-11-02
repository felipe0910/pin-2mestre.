import tkinter as tk
from tkinter import messagebox
import mysql.connector
from ctypes import CDLL, c_float

# -------------------- ESTILOS GLOBAIS --------------------
# Cores
COR_PRIMARIA = "#1E90FF"  # Azul (Mais vibrante para botões)
COR_FUNDO = "#ECECEC"     # Cinza claro (Fundo da janela principal e frames)
COR_TEXTO = "#333333"     # Cinza escuro
COR_DESTAQUE = "#FFFFFF"  # Branco (Fundo dos campos e botões)

# Fontes
FONTE_TITULO = ('Arial', 18, 'bold')
FONTE_LABEL = ('Arial', 10)
FONTE_BOTAO = ('Arial', 11, 'bold')

# Espaçamento
PAD_X_PAD = 25
PAD_Y_PAD = 15
PAD_Y_ELEMENT = 8

# -------------------- CONEXÃO E BIBLIOTERAS --------------------

# Conexão MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",    # sua senha
    database="meu_banco"
)
cursor = conn.cursor()

# Carregar biblioteca C (DLL)
lib = CDLL("./media.dll")
lib.calcular_media.restype = c_float

# -------------------- VARIÁVEIS GLOBAIS (Para referências futuras) --------------------
entry_nome = None
entry_sobrenome = None
entry_data = None
entry_ra = None
entry_email = None
entry_senha = None
entry_login_ra = None
entry_login_senha = None
entry_np1 = None
entry_np2 = None
entry_pin = None

# -------------------- FUNÇÕES AUXILIARES --------------------

def criar_campo(frame, texto, linha, tipo_entry=None):
    """Função auxiliar para criar Label e Entry com estilo aprimorado."""
    tk.Label(frame, text=texto, font=FONTE_LABEL, bg=COR_FUNDO, fg=COR_TEXTO).grid(
        row=linha, column=0, sticky='w', pady=PAD_Y_ELEMENT)
    
    entry = tk.Entry(frame, bg=COR_DESTAQUE, fg=COR_TEXTO, width=30,
                     relief=tk.FLAT, bd=1, highlightthickness=1, highlightcolor=COR_PRIMARIA)
    
    if tipo_entry == 'senha':
        entry.config(show="*")
    
    entry.grid(row=linha, column=1, sticky='ew', pady=PAD_Y_ELEMENT, padx=(10, 0))
    return entry

# -------------------- FUNÇÕES DE BACK-END (Manter a lógica intacta) --------------------

def cadastrar():
    nome = entry_nome.get()
    sobrenome = entry_sobrenome.get()
    data = entry_data.get()
    ra = entry_ra.get()
    email = entry_email.get()
    senha = entry_senha.get()
    
    if not all([nome, sobrenome, data, ra, email, senha]):
        messagebox.showwarning("Aviso", "Preencha todos os campos!")
        return
    
    try:
        # Inserir aluno
        cursor.execute(
            "INSERT INTO alunos (nome, sobrenome, data_nascimento, ra, email) VALUES (%s,%s,%s,%s,%s)",
            (nome, sobrenome, data, ra, email)
        )
        conn.commit()
        
        # Inserir login
        cursor.execute("INSERT INTO login (ra, senha) VALUES (%s, %s)", (ra, senha))
        conn.commit()
        
        messagebox.showinfo("Sucesso", "Cadastro realizado!")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao cadastrar: {err}")

def login():
    ra = entry_login_ra.get()
    senha = entry_login_senha.get()
    
    cursor.execute("SELECT * FROM login WHERE ra=%s AND senha=%s", (ra, senha))
    result = cursor.fetchone()
    
    if result:
        # Pegar id do aluno
        cursor.execute("SELECT id, nome FROM alunos WHERE ra=%s", (ra,))
        aluno = cursor.fetchone()
        abrir_notas(aluno[0], aluno[1])
    else:
        messagebox.showerror("Erro", "RA ou senha incorretos!")

def salvar_notas(id_aluno):
    try:
        np1_val = float(entry_np1.get())
        np2_val = float(entry_np2.get())
        pin_val = float(entry_pin.get())
    except ValueError: # Melhor capturar ValueError para float()
        messagebox.showerror("Erro", "Notas inválidas! Use apenas números.")
        return
    
    media = lib.calcular_media(c_float(np1_val), c_float(np2_val), c_float(pin_val))
    situacao = "Aprovado" if media >= 7 else "Reprovado"
    
    # Verificar se já existe notas
    cursor.execute("SELECT * FROM notas WHERE id_aluno=%s", (id_aluno,))
    if cursor.fetchone():
        cursor.execute(
            "UPDATE notas SET np1=%s, np2=%s, pin=%s, media=%s, situacao=%s WHERE id_aluno=%s",
            (np1_val, np2_val, pin_val, media, situacao, id_aluno)
        )
    else:
        cursor.execute(
            "INSERT INTO notas (id_aluno, np1, np2, pin, media, situacao) VALUES (%s,%s,%s,%s,%s,%s)",
            (id_aluno, np1_val, np2_val, pin_val, media, situacao)
        )
    conn.commit()
    
    messagebox.showinfo("Resultado", f"Média: {media:.2f}\nSituação: {situacao}")

def abrir_notas(id_aluno, nome_aluno):
    notas_window = tk.Toplevel(root)
    notas_window.title(f"Notas - {nome_aluno}")
    notas_window.config(bg=COR_FUNDO)
    
    # Centralizar janela de notas
    notas_width = 350
    notas_height = 300
    x_notas = (screen_width / 2) - (notas_width / 2)
    y_notas = (screen_height / 2) - (notas_height / 2)
    notas_window.geometry(f'{notas_width}x{notas_height}+{int(x_notas)}+{int(y_notas)}')
    notas_window.transient(root)
    notas_window.grab_set()

    notas_frame = tk.Frame(notas_window, bg=COR_FUNDO, padx=PAD_X_PAD, pady=PAD_Y_PAD)
    notas_frame.pack(fill='both', expand=True) # Manter pack para preencher a toplevel
    
    notas_frame.grid_columnconfigure(0, weight=1) # Coluna do Label
    notas_frame.grid_columnconfigure(1, weight=1) # Coluna do Entry

    tk.Label(notas_frame, text=f"Notas de {nome_aluno}", font=FONTE_TITULO, bg=COR_FUNDO, fg=COR_PRIMARIA).grid(row=0, column=0, columnspan=2, pady=(0, 15))
    
    global entry_np1, entry_np2, entry_pin
    entry_np1 = criar_campo(notas_frame, "NP1", 1)
    entry_np2 = criar_campo(notas_frame, "NP2", 2)
    entry_pin = criar_campo(notas_frame, "PIN (Peso 2)", 3)
    
    tk.Button(notas_frame, text="Salvar Notas", command=lambda: salvar_notas(id_aluno),
              bg='green', fg=COR_DESTAQUE, font=FONTE_BOTAO, relief=tk.FLAT).grid(
                  row=4, column=0, columnspan=2, pady=20, ipadx=15, ipady=7)

# -------------------- INTERFACES TKINTER (LAYOUT) --------------------

root = tk.Tk()
root.title("Sistema de Gestão Escolar")
root.config(bg=COR_FUNDO)

# Centralizar a janela principal na tela
root_width = 500 # Aumentei um pouco para melhor centralização
root_height = 450 # Aumentei um pouco
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width / 2) - (root_width / 2)
y = (screen_height / 2) - (root_height / 2)
root.geometry(f'{root_width}x{root_height}+{int(x)}+{int(y)}')

# Configurar o grid do root para centralizar o frame de cadastro
root.grid_rowconfigure(0, weight=1) # Linha acima do frame
root.grid_rowconfigure(1, weight=0) # Linha do frame
root.grid_rowconfigure(2, weight=1) # Linha abaixo do frame
root.grid_columnconfigure(0, weight=1) # Coluna à esquerda do frame
root.grid_columnconfigure(1, weight=0) # Coluna do frame
root.grid_columnconfigure(2, weight=1) # Coluna à direita do frame


# -------------------- ESTRUTURA CADASTRO --------------------
cadastro_frame = tk.Frame(root, bg=COR_FUNDO, padx=PAD_X_PAD, pady=PAD_Y_PAD)
cadastro_frame.grid(row=1, column=1, sticky='nsew') # Coloca o frame no centro do grid do root

# Configurar colunas internas do cadastro_frame para centralização
cadastro_frame.grid_columnconfigure(0, weight=1) # Coluna para Labels
cadastro_frame.grid_columnconfigure(1, weight=1) # Coluna para Entries

tk.Label(cadastro_frame, text="Novo Cadastro", font=FONTE_TITULO, bg=COR_FUNDO, fg=COR_PRIMARIA).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='nsew')

# Atribuindo as Entry Widgets às variáveis globais (Usando sticky 'ew' para expansão)
entry_nome = criar_campo(cadastro_frame, "Nome", 1)
entry_sobrenome = criar_campo(cadastro_frame, "Sobrenome", 2)
entry_data = criar_campo(cadastro_frame, "Data Nascimento (AAAA-MM-DD)", 3)
entry_ra = criar_campo(cadastro_frame, "RA", 4)
entry_email = criar_campo(cadastro_frame, "Email", 5)
entry_senha = criar_campo(cadastro_frame, "Senha", 6, 'senha')

tk.Button(cadastro_frame, text="Cadastrar", command=cadastrar,
          bg=COR_PRIMARIA, fg=COR_DESTAQUE, font=FONTE_BOTAO, relief=tk.FLAT).grid(
              row=7, column=0, columnspan=2, pady=20, ipadx=15, ipady=7, sticky='ew') # Botão também sticky 'ew'


# -------------------- ESTRUTURA LOGIN --------------------
login_window = tk.Toplevel(root)
login_window.title("Acesso ao Sistema")
login_window.config(bg=COR_FUNDO)
login_window.transient(root)
login_window.grab_set()

# Centralizar Janela de Login
login_width = 350
login_height = 250
x_login = (screen_width / 2) - (login_width / 2)
y_login = (screen_height / 2) - (login_height / 2)
login_window.geometry(f'{login_width}x{login_height}+{int(x_login)}+{int(y_login)}')

login_frame = tk.Frame(login_window, bg=COR_FUNDO, padx=PAD_X_PAD, pady=PAD_Y_PAD)
login_frame.pack(fill='both', expand=True) # Usamos pack aqui para preencher a toplevel

# Configurar colunas para centralização no Login Frame
login_frame.grid_columnconfigure(0, weight=1) # Coluna para Labels
login_frame.grid_columnconfigure(1, weight=1) # Coluna para Entries

tk.Label(login_frame, text="Login", font=FONTE_TITULO, bg=COR_FUNDO, fg=COR_PRIMARIA).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='nsew')

tk.Label(login_frame, text="RA", font=FONTE_LABEL, bg=COR_FUNDO, fg=COR_TEXTO).grid(row=1, column=0, sticky='w', pady=PAD_Y_ELEMENT)
entry_login_ra = tk.Entry(login_frame, bg=COR_DESTAQUE, fg=COR_TEXTO, width=20, relief=tk.FLAT, bd=1, highlightthickness=1, highlightcolor=COR_PRIMARIA)
entry_login_ra.grid(row=1, column=1, sticky='ew', pady=PAD_Y_ELEMENT, padx=(10, 0))

tk.Label(login_frame, text="Senha", font=FONTE_LABEL, bg=COR_FUNDO, fg=COR_TEXTO).grid(row=2, column=0, sticky='w', pady=PAD_Y_ELEMENT)
entry_login_senha = tk.Entry(login_frame, show="*", bg=COR_DESTAQUE, fg=COR_TEXTO, width=20, relief=tk.FLAT, bd=1, highlightthickness=1, highlightcolor=COR_PRIMARIA)
entry_login_senha.grid(row=2, column=1, sticky='ew', pady=PAD_Y_ELEMENT, padx=(10, 0))

tk.Button(login_frame, text="Login", command=login,
          bg=COR_PRIMARIA, fg=COR_DESTAQUE, font=FONTE_BOTAO, relief=tk.FLAT).grid(
              row=3, column=0, columnspan=2, pady=20, ipadx=15, ipady=7, sticky='ew') # Botão também sticky 'ew'


root.mainloop()