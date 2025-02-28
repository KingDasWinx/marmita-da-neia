from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from database import get_daily_orders, get_order_details, delete_order, update_order

console = Console()

def format_marmitas(marmitas_json):
    try:
        if isinstance(marmitas_json, str):
            marmitas_json = eval(marmitas_json)
            
        marmitas_list = []
        for i, marmita in enumerate(marmitas_json.get('marmitas', []), 1):
            adicionais = ", ".join(marmita.get('adicionais', [])) or "Sem adicionais"
            marmitas_list.append(f"Marmita {i}:\n  Tamanho: {marmita['tamanho']}\n  Preço: R$ {marmita['preco']:.2f}\n  Adicionais: {adicionais}")
        
        bebidas = marmitas_json.get('bebidas', [])
        if bebidas:
            marmitas_list.append("\nBebidas:\n  " + ", ".join(bebidas))
            
        tipo_feijao = marmitas_json.get('tipo_feijao', '')
        if tipo_feijao:
            marmitas_list.append(f"\nTipo de Feijão: {tipo_feijao}")
            
        return "\n".join(marmitas_list)
    except Exception as e:
        return str(marmitas_json)

def edit_order(order):
    console.clear()
    console.print(f"[yellow]=== Editando Pedido {order['numero_pedido']} ===[/yellow]\n")
    
    # Editar forma de pagamento
    formas_pagamento = ["Dinheiro", "Cartão", "PIX"]
    console.print("\n[cyan]Formas de pagamento disponíveis:[/cyan]")
    for i, forma in enumerate(formas_pagamento, 1):
        console.print(f"{i}. {forma}")
    forma_idx = int(Prompt.ask("\nEscolha a forma de pagamento", default=str(formas_pagamento.index(order['forma_pagamento']) + 1)))
    forma_pagamento = formas_pagamento[forma_idx - 1]
    
    # Editar status do pagamento
    status_opcoes = ["Pendente", "Pago"]
    console.print("\n[cyan]Status de pagamento disponíveis:[/cyan]")
    for i, status in enumerate(status_opcoes, 1):
        console.print(f"{i}. {status}")
    status_idx = int(Prompt.ask("\nEscolha o status do pagamento", default=str(status_opcoes.index(order['status_pagamento']) + 1)))
    status_pagamento = status_opcoes[status_idx - 1]
    
    # Editar horário de entrega
    horario_atual = order.get('horario_entrega', '')
    horario_entrega = Prompt.ask("\nHorário de entrega (HH:MM)", default=horario_atual)
    
    # Confirmar alterações
    console.print("\n[yellow]Resumo das alterações:[/yellow]")
    console.print(f"Forma de Pagamento: {forma_pagamento}")
    console.print(f"Status do Pagamento: {status_pagamento}")
    console.print(f"Horário de Entrega: {horario_entrega}")
    
    if Prompt.ask("\nConfirmar alterações? (S/N)", default="N").upper() == "S":
        if update_order(order['numero_pedido'], order['marmitas'], forma_pagamento, status_pagamento, horario_entrega):
            console.print("\n[green]Pedido atualizado com sucesso![/green]")
        else:
            console.print("\n[red]Erro ao atualizar pedido![/red]")
    else:
        console.print("\n[yellow]Operação cancelada![/yellow]")
    
    input("\nPressione Enter para continuar...")

def update_payment_status(order):
    console.clear()
    console.print(f"[yellow]=== Status do Pagamento - Pedido {order['numero_pedido']} ===[/yellow]\n")
    
    status_opcoes = ["Pendente", "Pago"]
    console.print("\n[cyan]Status de pagamento:[/cyan]")
    for i, status in enumerate(status_opcoes, 1):
        console.print(f"{i}. {status}")
    
    status_idx = int(Prompt.ask("\nEscolha o status do pagamento", default=str(status_opcoes.index(order['status_pagamento']) + 1)))
    status_pagamento = status_opcoes[status_idx - 1]
    
    if status_pagamento != order['status_pagamento']:
        if update_order(order['numero_pedido'], order['marmitas'], order['forma_pagamento'], status_pagamento, order.get('horario_entrega')):
            console.print("\n[green]Status do pagamento atualizado com sucesso![/green]")
        else:
            console.print("\n[red]Erro ao atualizar status do pagamento![/red]")
    else:
        console.print("\n[yellow]Status não foi alterado![/yellow]")
    
    input("\nPressione Enter para continuar...")

def show_order_details(numero_pedido):
    order = get_order_details(numero_pedido)
    if not order:
        console.print("\n[red]Pedido não encontrado para o dia de hoje![/red]")
        input("\nPressione Enter para continuar...")
        return
    
    console.clear()
    console.print(f"[yellow]=== Detalhes do Pedido {numero_pedido} ===[/yellow]\n")
    
    # Informações do Cliente
    console.print(f"[cyan]Cliente:[/cyan] {order['tb_cliente']['nm_usuario']}")
    
    # Endereço
    endereco = order['tb_endereco']
    console.print(f"[cyan]Endereço:[/cyan] {endereco['rua']}, {endereco['bairro']}")
    if endereco.get('referencia'):
        console.print(f"[cyan]Referência:[/cyan] {endereco['referencia']}")
    
    # Marmitas
    console.print(f"\n[cyan]Marmitas:[/cyan]")
    console.print(format_marmitas(order['marmitas']))
    
    # Informações de Pagamento
    console.print(f"\n[cyan]Valor Total:[/cyan] R$ {order['preco_total']:.2f}")
    console.print(f"[cyan]Forma de Pagamento:[/cyan] {order['forma_pagamento']}")
    console.print(f"[cyan]Status do Pagamento:[/cyan] {order['status_pagamento']}")
    
    if order.get('horario_entrega'):
        console.print(f"\n[cyan]Horário de Entrega:[/cyan] {order['horario_entrega']}")
    
    # Menu de opções
    menu_text = """
1. Imprimir
2. Status Pagamento
3. Editar
4. Excluir
0. Voltar
    """
    menu_panel = Panel(menu_text, title="Opções", border_style="yellow")
    
    while True:
        console.print("\n")
        console.print(menu_panel)
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            from printer import imprimir_pedido
            imprimir_pedido(order, order['tb_cliente'])
            input("\nPressione Enter para continuar...")
            return
        elif opcao == "2":
            update_payment_status(order)
            return
        elif opcao == "3":
            edit_order(order)
            return
        elif opcao == "4":
            if input("\nTem certeza que deseja excluir este pedido? (S/N): ").upper() == "S":
                if delete_order(numero_pedido):
                    console.print("\n[green]Pedido excluído com sucesso![/green]")
                    input("\nPressione Enter para continuar...")
                    return
                else:
                    console.print("\n[red]Erro ao excluir pedido![/red]")
                    input("\nPressione Enter para continuar...")
        elif opcao == "0":
            return

def show_daily_orders():
    while True:
        orders = get_daily_orders()
        
        console.clear()
        if not orders:
            console.print("\n[yellow]Nenhum pedido registrado hoje![/yellow]")
            input("\nPressione Enter para continuar...")
            return
        
        table = Table(title="Pedidos do Dia")
        table.add_column("Nº Pedido", justify="center", style="cyan")
        table.add_column("Cliente", style="green")
        table.add_column("Forma Pagamento", justify="center")
        table.add_column("Status", justify="center", style="bold")
        
        for order in orders:
            numero_pedido, cliente, forma_pagamento, status = order
            table.add_row(
                numero_pedido,
                cliente,
                forma_pagamento,
                status
            )
        
        console.print(table)
        console.print("\nDigite o número do pedido para ver mais detalhes ou 0 para voltar")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "0":
            return
        
        if any(order[0] == opcao for order in orders):
            show_order_details(opcao)
        else:
            console.print("\n[red]Pedido não encontrado![/red]")
            input("\nPressione Enter para continuar...")
