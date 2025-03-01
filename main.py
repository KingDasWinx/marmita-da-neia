from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import webbrowser
import subprocess
import platform
from order import register_order
from daily_orders import show_daily_orders
from planilha import export_spreadsheet
from config import configure_printing
from clientes import gerenciar_clientes

console = Console()

def open_website():
    """Abre o site das Marmitas da Néia no navegador padrão."""
    website_url = "https://marmitasdaneia.netlify.app/"
    
    try:
        console.print("\n[yellow]Abrindo o site das Marmitas da Néia...[/yellow]")
        webbrowser.open(website_url)
        console.print("\n[green]Site aberto com sucesso![/green]")
    except Exception as e:
        console.print(f"\n[red]Erro ao abrir o site: {str(e)}[/red]")
    
    input("\nPressione Enter para continuar...")

def main_menu():
    title = Text("===== Marmitas da Néia =====", style="bold yellow")
    menu_text = """
1. Registrar Pedido
2. Pedidos do dia
3. Configurar Impressão
4. Exportar planilha
5. Abrir site
6. Gerenciar Clientes
0. Sair
    """
    menu_panel = Panel(menu_text, title=title, border_style="yellow")
    
    while True:
        console.clear()
        console.print(menu_panel)
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            register_order()
        elif opcao == "2":
            show_daily_orders()
        elif opcao == "3":
            configure_printing()
        elif opcao == "4":
            export_spreadsheet()
        elif opcao == "5":
            open_website()
        elif opcao == "6":
            gerenciar_clientes()
        elif opcao == "0":
            break

if __name__ == "__main__":
    main_menu()