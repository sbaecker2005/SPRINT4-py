import tkinter as tk
from interface import TelaInicial  # Importa a classe TelaInicial do módulo interface.py

# Função principal do programa
def main():
    # Cria a janela principal da aplicação
    root = tk.Tk()
    root.title("Sistema de Triagem de Pacientes")  # Define o título da janela
    root.geometry("1024x768")  # Define o tamanho da janela (largura x altura)
    
    # Inicializa a interface gráfica com a classe TelaInicial
    TelaInicial(root)
    
    # Inicia o loop principal da interface gráfica
    root.mainloop()

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":
    main()  # Chama a função principal
