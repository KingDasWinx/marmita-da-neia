import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt
from rich.text import Text

console = Console()

# Caminho para o arquivo de configuração
CONFIG_FILE = '.config'

# Configurações padrão
DEFAULT_CONFIG = {
    'imprimir_automaticamente': False,
    'quantidade_impressoes': 1
}

def load_config():
    """Carrega as configurações do arquivo .config"""
    if not os.path.exists(CONFIG_FILE):
        # Se o arquivo não existir, cria com valores padrão
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            return config
    except Exception as e:
        console.print(f"[red]Erro ao carregar configurações: {str(e)}[/red]")
        console.print("[yellow]Usando configurações padrão.[/yellow]")
        return DEFAULT_CONFIG

def save_config(config):
    """Salva as configurações no arquivo .config"""
    try:
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)
        return True
    except Exception as e:
        console.print(f"[red]Erro ao salvar configurações: {str(e)}[/red]")
        return False

def display_current_config():
    """Exibe as configurações atuais"""
    config = load_config()
    
    imprimir_auto = "Sim" if config.get('imprimir_automaticamente', False) else "Não"
    qtd_impressoes = config.get('quantidade_impressoes', 1)
    
    text = Text()
    text.append("\nConfigurações Atuais:\n\n", style="bold")
    text.append(f"Imprimir automaticamente: ", style="yellow")
    text.append(f"{imprimir_auto}\n", style="green" if imprimir_auto == "Sim" else "red")
    
    text.append(f"Quantidade de impressões: ", style="yellow")
    text.append(f"{qtd_impressoes}\n", style="cyan")
    
    console.print(text)
    
def configure_printing():
    """Interface para configurar as opções de impressão"""
    config = load_config()
    
    title = Text("===== Configurações de Impressão =====", style="bold yellow")
    panel = Panel("", title=title, border_style="yellow")
    
    while True:
        console.clear()
        console.print(panel)
        
        display_current_config()
        
        console.print("\n[bold]O que você deseja configurar?[/bold]")
        console.print("1. Imprimir automaticamente")
        console.print("2. Quantidade de impressões")
        console.print("0. Voltar ao menu principal")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            # Configurar impressão automática
            imprimir_auto = config.get('imprimir_automaticamente', False)
            novo_valor = Confirm.ask("\nDeseja imprimir automaticamente ao finalizar um pedido?", 
                                    default=imprimir_auto)
            
            config['imprimir_automaticamente'] = novo_valor
            if save_config(config):
                console.print("[green]Configuração salva com sucesso![/green]")
            
            input("\nPressione Enter para continuar...")
            
        elif opcao == "2":
            # Configurar quantidade de impressões
            qtd_atual = config.get('quantidade_impressoes', 1)
            novo_valor = IntPrompt.ask("\nQuantidade de cópias para impressão", 
                                     default=qtd_atual, 
                                     show_default=True)
            
            if novo_valor < 1:
                console.print("[yellow]A quantidade mínima é 1. Definindo para 1.[/yellow]")
                novo_valor = 1
            
            config['quantidade_impressoes'] = novo_valor
            if save_config(config):
                console.print("[green]Configuração salva com sucesso![/green]")
            
            input("\nPressione Enter para continuar...")
            
        elif opcao == "0":
            break
        
        else:
            console.print("[red]Opção inválida![/red]")
            input("Pressione Enter para continuar...")

# Funções auxiliares para outros módulos
def get_auto_print():
    """Retorna se a impressão automática está ativada"""
    config = load_config()
    return config.get('imprimir_automaticamente', False)

def get_print_quantity():
    """Retorna a quantidade de impressões configurada"""
    config = load_config()
    return config.get('quantidade_impressoes', 1)

if __name__ == "__main__":
    configure_printing()
