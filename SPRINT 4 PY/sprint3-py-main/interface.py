import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from collections import deque
from logica import classificar_gravidade, salvar_dados, carregar_dados, validar_cpf, buscar_paciente_por_cpf, validar_dados_paciente
from logica import validar_data_formatada

# Carrega os dados dos pacientes e histórico de um arquivo JSON
dados = carregar_dados("dados_pacientes.json")
pacientes = dados["pacientes"]  # Lista de pacientes ativos
historico = dados["historico"]  # Histórico de pacientes que já receberam alta
waiting_queue = deque()  # Fila de espera (não utilizada diretamente no código)

# Classe para a tela inicial do sistema
class TelaInicial:
    def __init__(self, root):
        self.root = root
        self.frame = ttk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        # Título da tela inicial
        titulo = ttk.Label(self.frame, text="Sistema Hospitalar", font=("Arial", 24, "bold"))
        titulo.pack(pady=30)

        # Botões para navegar entre as telas
        botoes = [
            ("Sou Paciente", lambda: self.mudar_tela(TelaPaciente)),
            ("Sou Funcionário", lambda: self.mudar_tela(TelaFuncionario)),
            ("Sair", self.sair)
        ]

        # Criação dos botões
        for texto, comando in botoes:
            btn = ttk.Button(self.frame, text=texto, command=comando, style="TButton")
            btn.pack(pady=20, ipadx=20, ipady=10)

    def mudar_tela(self, tela):
        self.frame.destroy()
        tela(self.root)

    def sair(self):
        salvar_dados("dados_pacientes.json", {"pacientes": pacientes, "historico": historico})
        self.root.quit()

class TelaPaciente:
    def __init__(self, root):
        self.root = root
        self.frame = ttk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        titulo = ttk.Label(self.frame, text="Pré-Check-in", font=("Arial", 24, "bold"))
        titulo.pack(pady=30)

        self.campos = {
            "Nome": ttk.Entry(self.frame, font=("Arial", 14)),
            "CPF": ttk.Entry(self.frame, font=("Arial", 14)),
            "Data de Nascimento (DD/MM/AAAA)": ttk.Entry(self.frame, font=("Arial", 14)),
            "Alergias": ttk.Entry(self.frame, font=("Arial", 14))
        }

        for label, entry in self.campos.items():
            ttk.Label(self.frame, text=label, font=("Arial", 14)).pack(pady=5)
            entry.pack(pady=5)

        btn_iniciar_quiz = ttk.Button(self.frame, text="Iniciar Quiz de Sintomas", command=self.iniciar_quiz, style="TButton")
        btn_iniciar_quiz.pack(pady=20, ipadx=20, ipady=10)

        btn_voltar = ttk.Button(self.frame, text="Voltar", command=self.voltar, style="TButton")
        btn_voltar.pack(pady=20, ipadx=20, ipady=10)

    def validar_dados_basicos(self):
        nome = self.campos["Nome"].get()
        cpf = self.campos["CPF"].get()
        nascimento = self.campos["Data de Nascimento (DD/MM/AAAA)"].get()

        if not nome or not cpf or not nascimento:
            raise ValueError("Todos os campos devem ser preenchidos.")
        if not validar_cpf(cpf):
            raise ValueError("CPF inválido.")
        if buscar_paciente_por_cpf(cpf, pacientes):
            raise ValueError("CPF já cadastrado.")
        if not validar_data_formatada(nascimento):
            raise ValueError("Data de nascimento inválida. Use o formato DD/MM/AAAA.")

    def iniciar_quiz(self):
        try:
            self.validar_dados_basicos()
            sintomas = {}


            # Pergunta sobre lesão física
            lesao_fisica = messagebox.askyesno("Lesão Física", "O problema é uma lesão física, como uma fratura?")
            if lesao_fisica:
                # Solicita descrição e local da lesão
                descricao_lesao = simpledialog.askstring("Descrição da Lesão", "O que aconteceu?")
                if not descricao_lesao:
                    raise ValueError("Descrição da lesão não fornecida.")
                local_lesao = simpledialog.askstring("Local da Lesão", "Onde está a lesão? (ex.: braço, perna, cabeça, etc.)")
                if not local_lesao:
                    raise ValueError("Local da lesão não fornecido.")
                sintomas["lesao_fisica"] = {"descricao": descricao_lesao, "local": local_lesao}
            else:
                # Perguntas sobre febre, dor, falta de ar e cansaço
                febre = messagebox.askyesno("Febre", "Você está com febre?")
                if febre:
                    temperatura = simpledialog.askfloat("Temperatura", "Qual é a sua temperatura em °C?")
                    if temperatura is None:
                        raise ValueError("Temperatura não fornecida.")
                    if temperatura < 37.5:
                        sintomas["febre"] = "Baixa"
                    elif 37.5 <= temperatura <= 39:
                        sintomas["febre"] = "Moderada"
                    else:
                        sintomas["febre"] = "Alta"
                else:
                    sintomas["febre"] = "Nenhuma"

                dor = messagebox.askyesno("Dor", "Você está sentindo dor?")
                if dor:
                    intensidade_dor = simpledialog.askstring("Intensidade da Dor", "Qual é a intensidade da dor? (leve, moderada, intensa)")
                    if not intensidade_dor:
                        raise ValueError("Intensidade da dor não fornecida.")
                    sintomas["dor"] = intensidade_dor

                    local_dor = simpledialog.askstring("Localização da Dor", "Onde está a dor? (barriga, cabeça, tórax, ouvido)")
                    if not local_dor or local_dor.lower() not in ["barriga", "cabeça", "tórax", "ouvido"]:
                        raise ValueError("Localização da dor inválida ou não fornecida.")
                    sintomas["local_dor"] = local_dor
                else:
                    sintomas["dor"] = "Nenhuma"
                    sintomas["local_dor"] = "Nenhuma"

                falta_ar = messagebox.askyesno("Falta de Ar", "Você está com falta de ar?")
                sintomas["falta_ar"] = "Sim" if falta_ar else "Não"

                cansaço = messagebox.askyesno("Cansaço", "Você está se sentindo cansado?")
                sintomas["cansaço"] = "Sim" if cansaço else "Não"

            # Pergunta sobre o tempo dos sintomas
            tempo_sintomas = simpledialog.askinteger("Tempo dos Sintomas", "Há quantos dias você está com esses sintomas?")
            if tempo_sintomas is None or tempo_sintomas < 0:
                raise ValueError("Tempo dos sintomas inválido ou não fornecido.")
            sintomas["tempo_sintomas"] = tempo_sintomas

            # Finaliza o check-in com os sintomas coletados
            self.finalizar_checkin(sintomas)
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")

    # Método para finalizar o check-in do paciente
    def finalizar_checkin(self, sintomas):
        try:
            nome = self.campos["Nome"].get()
            cpf = self.campos["CPF"].get()
            birth_date = self.campos["Data de Nascimento (DD/MM/AAAA)"].get()
            alergias = self.campos["Alergias"].get()

            # Criação do objeto paciente
            paciente = {
                "name": nome,
                "cpf": cpf,
                "birth_date": birth_date,
                "alergias": alergias,
                "sintomas": sintomas,
                "diagnosticos": []
            }
            pacientes.append(paciente)

            # Salva os dados atualizados
            salvar_dados("dados_pacientes.json", {"pacientes": pacientes, "historico": historico})
            messagebox.showinfo("Sucesso", "Pré-check-in realizado com sucesso!")
            self.voltar()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")

    # Método para voltar à tela inicial
    def voltar(self):
        self.frame.destroy()
        TelaInicial(self.root)

# Classe para a tela do funcionário
class TelaFuncionario:
    def __init__(self, root):
        self.root = root
        self.frame = ttk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        # Título da tela do funcionário
        titulo = ttk.Label(self.frame, text="Menu do Funcionário", font=("Arial", 24, "bold"))
        titulo.pack(pady=30)

        # Botões para as funcionalidades do funcionário
        botoes = [
            ("Ver Fila de Espera", lambda: self.mudar_tela(TelaFila)),
            ("Adicionar Diagnóstico", self.adicionar_diagnostico),
            ("Ver Diagnósticos e Alergias", self.ver_diagnosticos_e_alergias),
            ("Ver Preferências da Família", self.ver_preferencias_familia),
            ("Dar Alta", self.dar_alta),
            ("Voltar", self.voltar)
        ]

        # Criação dos botões
        for texto, comando in botoes:
            btn = ttk.Button(self.frame, text=texto, command=comando, style="TButton")
            btn.pack(pady=20, ipadx=20, ipady=10)

    # Método para mudar para outra tela
    def mudar_tela(self, tela):
        self.frame.destroy()
        tela(self.root)

    # Método para adicionar diagnóstico a um paciente
    def adicionar_diagnostico(self):
        try:
            cpf = simpledialog.askstring("Diagnóstico", "Digite o CPF do paciente:")
            if not cpf:
                raise ValueError("CPF não fornecido.")
            if not validar_cpf(cpf):
                raise ValueError("CPF inválido. Verifique e tente novamente.")
            paciente = buscar_paciente_por_cpf(cpf, pacientes)
            if not paciente:
                raise ValueError("Paciente não encontrado.")

            # Solicita informações do diagnóstico
            diagnostico = simpledialog.askstring("Diagnóstico", "Digite o diagnóstico:")
            if not diagnostico:
                raise ValueError("Diagnóstico não fornecido.")
            observacoes = simpledialog.askstring("Observações", "Digite as observações:")
            medicacoes_preferidas = simpledialog.askstring("Medicações", "Digite as medicações preferidas pela família:")

            # Adiciona o diagnóstico ao paciente
            paciente["diagnosticos"].append({
                "diagnostico": diagnostico,
                "observacoes": observacoes,
                "medicacoes_preferidas": medicacoes_preferidas,
                "alergias": paciente.get("alergias", "Nenhuma alergia registrada.")
            })

            # Salva os dados atualizados
            salvar_dados("dados_pacientes.json", {"pacientes": pacientes, "historico": historico})
            messagebox.showinfo("Sucesso", "Diagnóstico adicionado com sucesso!")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")

    # Método para visualizar diagnósticos e alergias de um paciente
    def ver_diagnosticos_e_alergias(self):
        cpf = simpledialog.askstring("Ver Diagnósticos e Alergias", "Digite o CPF do paciente:")
        paciente = buscar_paciente_por_cpf(cpf, pacientes)

        # Se o paciente não estiver na lista de pacientes, busca no histórico
        if not paciente:
            paciente = buscar_paciente_por_cpf(cpf, historico)
            if not paciente:
                messagebox.showerror("Erro", "Paciente não encontrado.")
                return

        # Exibe os diagnósticos e alergias do paciente
        diagnosticos = paciente.get("diagnosticos", [])
        info = f"Alergias: {paciente.get('alergias', 'Nenhuma alergia registrada.')}\n\nDiagnósticos Anteriores:\n"
        if diagnosticos:
            for idx, diag in enumerate(diagnosticos, start=1):
                info += (
                    f"{idx}. Diagnóstico: {diag['diagnostico']}\n"
                    f"   Observações: {diag['observacoes']}\n"
                    f"   Medicações Preferidas: {diag['medicacoes_preferidas']}\n"
                    f"   Alergias: {diag['alergias']}\n\n"
                )
        else:
            info += "Nenhum diagnóstico registrado."

        messagebox.showinfo("Diagnósticos e Alergias", info)

    # Método para visualizar preferências da família
    def ver_preferencias_familia(self):
        cpf = simpledialog.askstring("Ver Preferências da Família", "Digite o CPF do paciente:")
        paciente = buscar_paciente_por_cpf(cpf, pacientes)
        if not paciente:
            messagebox.showerror("Erro", "Paciente não encontrado.")
            return

        # Exibe as preferências de medicações da família
        diagnosticos = paciente.get("diagnosticos", [])
        info = "Preferências da Família:\n"
        if diagnosticos:
            for idx, diag in enumerate(diagnosticos, start=1):
                info += f"{idx}. Medicações Preferidas: {diag['medicacoes_preferidas']}\n"
        else:
            info += "Nenhuma preferência registrada."

        messagebox.showinfo("Preferências da Família", info)

    # Método para dar alta a um paciente
    def dar_alta(self):
        cpf = simpledialog.askstring("Dar Alta", "Digite o CPF do paciente:")
        paciente = buscar_paciente_por_cpf(cpf, pacientes)
        if not paciente:
            messagebox.showerror("Erro", "Paciente não encontrado.")
            return

        # Confirmação para dar alta
        confirmacao = messagebox.askyesno("Confirmação", f"Tem certeza que deseja dar alta para {paciente['name']}?")
        if not confirmacao:
            return

        # Remove o paciente da lista de pacientes e adiciona ao histórico
        pacientes.remove(paciente)
        historico.append(paciente)

        # Salva os dados atualizados
        salvar_dados("dados_pacientes.json", {"pacientes": pacientes, "historico": historico})
        messagebox.showinfo("Sucesso", f"Alta concedida para {paciente['name']}. O diagnóstico foi salvo no histórico.")

    # Método para voltar à tela inicial
    def voltar(self):
        self.frame.destroy()
        TelaInicial(self.root)

# Classe para a tela da fila de espera
class TelaFila:
    def __init__(self, root):
        self.root = root
        self.frame = ttk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        # Título da tela da fila de espera
        titulo = ttk.Label(self.frame, text="Fila de Espera", font=("Arial", 24, "bold"))
        titulo.pack(pady=30)

        # Área de texto para exibir a fila de espera
        self.lista_fila = tk.Text(self.frame, height=20, width=80, font=("Arial", 12))
        self.lista_fila.pack(pady=20)
        self.atualizar_fila()

        # Botão para voltar ao menu do funcionário
        btn_voltar = ttk.Button(self.frame, text="Voltar", command=self.voltar, style="TButton")
        btn_voltar.pack(pady=20, ipadx=20, ipady=10)

    # Método para atualizar a lista da fila de espera
    def atualizar_fila(self):
        self.lista_fila.delete(1.0, tk.END)
        if not pacientes:
            self.lista_fila.insert(tk.END, "A fila de espera está vazia.")
        else:
            # Ordena os pacientes por gravidade e tipo de sintomas
            pacientes_ordenados = sorted(
                pacientes,
                key=lambda p: (
                    classificar_gravidade(p.get("sintomas", {}), p.get("sintomas", {}).get("tempo_sintomas", 0)) != "Grave",
                    "lesao_fisica" not in p["sintomas"],
                    p["sintomas"].get("lesao_fisica", {}).get("local") != "cabeça"
                )
            )
            # Exibe os pacientes na fila
            for idx, paciente in enumerate(pacientes_ordenados, start=1):
                sintomas = paciente.get("sintomas", {})
                tempo_sintomas = sintomas.get("tempo_sintomas", 0)
                estado = classificar_gravidade(sintomas, tempo_sintomas)
                sintomas_str = ", ".join([f"{k}: {v}" for k, v in sintomas.items()])
                self.lista_fila.insert(
                    tk.END,
                    f"{idx}. Nome: {paciente.get('name', 'Desconhecido')}, "
                    f"Sintomas: {sintomas_str}, "
                    f"Tempo: {tempo_sintomas} dias, "
                    f"Estado: {estado}\n"
                )

    # Método para voltar ao menu do funcionário
    def voltar(self):
        self.frame.destroy()
        TelaFuncionario(self.root)
