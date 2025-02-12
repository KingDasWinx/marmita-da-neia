from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from order import register_order
from daily_orders import show_daily_orders

console = Console()

def main_menu():
    title = Text("===== Marmitas da Néia =====", style="bold yellow")
    menu_text = """
1. Registrar Pedido
2. Pedidos do dia
3. Configurar Impressão
4. Exportar planilha
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
        elif opcao == "0":
            break

if __name__ == "__main__":
    main_menu()