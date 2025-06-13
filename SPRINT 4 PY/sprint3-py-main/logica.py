import json
import logging
from datetime import datetime


def validar_data_formatada(data_str):
    """
    Verifica se a data existe e está no formato DD/MM/AAAA.

    Args:
        data_str (str): String da data.

    Returns:
        bool: True se a data for válida no formato DD/MM/AAAA, False caso contrário.
    """
    try:
        datetime.strptime(data_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# Configuração de logs
logging.basicConfig(filename="sistema_hospitalar.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def classificar_gravidade(sintomas, tempo_sintomas):
    """
    Classifica a gravidade com base nos sintomas e no tempo dos sintomas.

    Args:
        sintomas (dict): Dicionário contendo os sintomas do paciente.
        tempo_sintomas (int): Número de dias com os sintomas.

    Returns:
        str: Nível de gravidade ("Grave", "Moderado", "Leve").
    """
    if sintomas.get("febre") in ["Alta", "Moderada"] or sintomas.get("falta_ar") == "Sim":
        return "Grave"
    elif sintomas.get("dor") in ["moderada", "intensa"] or tempo_sintomas > 3:
        return "Moderado"
    else:
        return "Leve"

def salvar_dados(arquivo, dados):
    """
    Salva os dados no arquivo JSON especificado.

    Args:
        arquivo (str): Caminho do arquivo JSON.
        dados (dict): Dados a serem salvos.

    Raises:
        Exception: Caso ocorra um erro ao salvar os dados.
    """
    try:
        with open(arquivo, "w") as f:
            json.dump(dados, f, indent=4)
        logging.info(f"Dados salvos com sucesso no arquivo {arquivo}.")
    except Exception as e:
        logging.error(f"Erro ao salvar dados: {e}")
        raise

def carregar_dados(arquivo):
    """
    Carrega os dados do arquivo JSON especificado.

    Args:
        arquivo (str): Caminho do arquivo JSON.

    Returns:
        dict: Dados carregados do arquivo.
    """
    try:
        with open(arquivo, "r") as f:
            dados = json.load(f)
            for paciente in dados["pacientes"]:
                paciente.setdefault("tempo_sintomas", 0)
                paciente.setdefault("sintomas", {})
                paciente.setdefault("alergias", "Nenhuma alergia registrada.")
                paciente.setdefault("diagnosticos", [])
            logging.info(f"Dados carregados com sucesso do arquivo {arquivo}.")
            return dados
    except FileNotFoundError:
        logging.warning(f"Arquivo {arquivo} não encontrado. Criando um novo arquivo.")
        return {"pacientes": [], "historico": []}
    except json.JSONDecodeError:
        logging.error(f"Erro ao decodificar o arquivo {arquivo}. Criando um novo arquivo.")
        return {"pacientes": [], "historico": []}
    except Exception as e:
        logging.error(f"Erro inesperado ao carregar dados: {e}")
        return {"pacientes": [], "historico": []}

def validar_cpf(cpf):
    """
    Valida o CPF verificando o formato e os dígitos verificadores.

    Args:
        cpf (str): CPF a ser validado.

    Returns:
        bool: True se o CPF for válido, False caso contrário.
    """
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10

    return cpf[-2:] == f"{digito1}{digito2}"

def buscar_paciente_por_cpf(cpf, pacientes):
    """
    Busca um paciente pelo CPF na lista de pacientes.

    Args:
        cpf (str): CPF do paciente.
        pacientes (list): Lista de pacientes.

    Returns:
        dict or None: Paciente encontrado ou None se não encontrado.
    """
    for paciente in pacientes:
        if paciente.get("cpf") == cpf:
            return paciente
    return None

def validar_dados_paciente(nome, cpf, nascimento, pacientes):
    """
    Valida os dados básicos do paciente antes de cadastrar ou iniciar o atendimento.

    Args:
        nome (str): Nome do paciente.
        cpf (str): CPF do paciente.
        nascimento (str): Data de nascimento do paciente.
        pacientes (list): Lista de pacientes já cadastrados.

    Raises:
        ValueError: Caso algum campo seja inválido.
    """
    if not nome or not cpf or not nascimento:
        raise ValueError("Todos os campos obrigatórios devem ser preenchidos.")
    if not validar_cpf(cpf):
        raise ValueError("CPF inválido.")
    if buscar_paciente_por_cpf(cpf, pacientes):
        raise ValueError("Este CPF já está cadastrado.")
