import unittest
from logica import validar_cpf, classificar_gravidade

# Define uma classe de teste que herda de unittest.TestCase
class TestLogica(unittest.TestCase):
    # Testa a função validar_cpf
    def test_validar_cpf(self):
        # Verifica se a função retorna True para um CPF válido
        self.assertTrue(validar_cpf("12345678909"))  # CPF válido
        # Verifica se a função retorna False para um CPF inválido
        self.assertFalse(validar_cpf("12345678900"))  # CPF inválido
        # Verifica se a função retorna False para um CPF muito curto
        self.assertFalse(validar_cpf("123"))  # CPF muito curto
        # Verifica se a função retorna False para um CPF com caracteres inválidos
        self.assertFalse(validar_cpf("abcdefghijk"))  # CPF com letras

    # Testa a função classificar_gravidade
    def test_classificar_gravidade(self):
        # Verifica se a função classifica corretamente como "Grave"
        sintomas_grave = {"febre": "Alta", "falta_ar": "Sim"}
        self.assertEqual(classificar_gravidade(sintomas_grave, 2), "Grave")

        # Verifica se a função classifica corretamente como "Moderado"
        sintomas_moderado = {"dor": "moderada"}
        self.assertEqual(classificar_gravidade(sintomas_moderado, 4), "Moderado")

        # Verifica se a função classifica corretamente como "Leve"
        sintomas_leve = {"febre": "Nenhuma"}
        self.assertEqual(classificar_gravidade(sintomas_leve, 1), "Leve")

# Executa os testes quando o arquivo é executado diretamente
if __name__ == "__main__":
    unittest.main()
