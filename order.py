from rich.console import Console
from rich.prompt import Prompt
import os
from database import get_client, get_addresses, register_address, register_client, save_order, get_next_order_number, DEBUG
from order_items import select_marmitas, select_bebidas, select_adicionais, mostrar_resumo_pedido
from config import get_auto_print
import time
import json
import random
import sys


console = Console()

def get_new_address():
    while True:
        console.clear()
        rua = Prompt.ask("[yellow]Digite a rua e número[/yellow]").strip()
        if not rua:
            console.print("[red]A rua não pode ficar vazia![/red]")
            continue
            
        bairro = Prompt.ask("[yellow]Digite o bairro[/yellow]").strip()
        if not bairro:
            console.print("[red]O bairro não pode ficar vazio![/red]")
            continue
            
        referencia = Prompt.ask("[yellow]Digite uma referência (opcional)[/yellow]").strip()
        if not referencia:
            referencia = None
            
        return rua, bairro, referencia

def register_new_client():
    console.clear()
    while True:
        nome = Prompt.ask("[yellow]Digite o nome do cliente[/yellow]").strip()
        if nome:
            break
        console.print("[red]O nome não pode ficar vazio![/red]")
    
    new_client = register_client(nome)
    if new_client:
        console.print("[green]Cliente cadastrado com sucesso![/green]")
        time.sleep(1)
        
        # Registra o primeiro endereço automaticamente
        console.print("\n[yellow]Agora vamos cadastrar um endereço para o cliente.[/yellow]")
        time.sleep(1)
        
        rua, bairro, referencia = get_new_address()
        new_address = register_address(new_client['id_cliente'], rua, bairro, referencia)
        
        if new_address:
            console.print("[green]Endereço cadastrado com sucesso![/green]")
            time.sleep(1)
            return new_client
    else:
        console.print("[red]Erro ao cadastrar cliente![/red]")
        time.sleep(2)
        return None

def show_client_addresses(client_id, client_name):
    while True:
        console.clear()
        console.print(f"\n[green]Cliente: {client_name}[/green]")
        
        # Busca endereços
        addresses = get_addresses(int(client_id))
        
        if addresses:
            console.print("\n[yellow]Endereços disponíveis:[/yellow]")
            for i, addr in enumerate(addresses, 1):
                console.print(f"{i}. {addr['rua']}, {addr['bairro']}")
            
            console.print("\n[blue]Digite 'novo' para adicionar um novo endereço[/blue]")
            address_choice = Prompt.ask("Escolha o número do endereço")
            
            if address_choice.lower() == 'novo':
                rua, bairro, referencia = get_new_address()
                new_address = register_address(int(client_id), rua, bairro, referencia)
                if new_address:
                    console.print("[green]Endereço cadastrado com sucesso![/green]")
                    time.sleep(2)
                    continue  # Volta para mostrar a lista atualizada
                else:
                    console.print("[red]Erro ao cadastrar endereço![/red]")
                    time.sleep(2)
                    continue
            else:
                try:
                    choice_idx = int(address_choice) - 1
                    if 0 <= choice_idx < len(addresses):
                        return addresses[choice_idx]
                    else:
                        console.print("[red]Número de endereço inválido![/red]")
                        time.sleep(2)
                except ValueError:
                    console.print("[red]Por favor, digite um número válido ou 'novo'[/red]")
                    time.sleep(2)
        else:
            console.print("\n[yellow]Nenhum endereço cadastrado. Vamos adicionar um novo.[/yellow]")
            rua, bairro, referencia = get_new_address()
            new_address = register_address(int(client_id), rua, bairro, referencia)
            if new_address:
                console.print("[green]Endereço cadastrado com sucesso![/green]")
                time.sleep(2)
                continue  # Volta para mostrar a lista atualizada
            else:
                console.print("[red]Erro ao cadastrar endereço![/red]")
                time.sleep(2)
                return None

def mostrar_menu_pos_pedido(pedido, cliente):
    # Verifica se a impressão automática está habilitada
    auto_print = get_auto_print()
    if auto_print:
        from printer import imprimir_pedido
        console.print("\n[yellow]Imprimindo pedido automaticamente...[/yellow]")
        imprimir_pedido(pedido, cliente)
        console.print("[green]Pedido impresso com sucesso![/green]")
        time.sleep(1)
        
    while True:
        console.clear()
        console.print("\n[yellow]Opções:[/yellow]")
        console.print("1. Copiar informações do pedido")
        console.print("2. Imprimir pedido")
        console.print("3. Voltar ao menu principal")
        
        opcao = Prompt.ask("\nEscolha uma opção")
        
        if opcao == '1':
            console.print("[yellow]Função não implementada ainda[/yellow]")
            time.sleep(2)
        elif opcao == '2':
            from printer import imprimir_pedido
            imprimir_pedido(pedido, cliente)
            time.sleep(2)
        elif opcao == '3':
            break
        else:
            console.print("[red]Opção inválida![/red]")
            time.sleep(2)

def register_order():
    console.clear()
    client_id = Prompt.ask("[yellow]ID do cliente (ou 'novo' para novo cliente)[/yellow]")
    
    if client_id.lower() == 'novo':
        new_client = register_new_client()
        if new_client:
            selected_address = show_client_addresses(new_client['id_cliente'], new_client['nm_usuario'])
            if selected_address:
                # Seleção de itens do pedido
                marmitas = select_marmitas()
                bebidas = select_bebidas()
                marmitas = select_adicionais(marmitas)
                
                # Mostrar resumo e permitir personalização
                subtotais = mostrar_resumo_pedido(marmitas, bebidas, selected_address, new_client)
                
                # Salvar pedido
                numero = get_next_order_number()
                pedido = {
                    'numero_pedido': numero,
                    'marmitas': json.dumps({
                        'marmitas': [{'tamanho': m['produto']['nome'], 'adicionais': m['adicionais']} for m in marmitas],
                        'bebidas': [{'nome': b['produto']['nome'], 'quantidade': b['quantidade'], 'preco': b['produto']['preco']} for b in bebidas],
                        'tipo_feijao': subtotais['tipo_feijao']
                    }),
                    'preco_total': subtotais['total'],
                    'forma_pagamento': subtotais['forma_pagamento'],
                    'status_pagamento': subtotais['status_pagamento'],
                    'horario_entrega': subtotais['horario_entrega'],
                    'obs': subtotais.get('observacoes'),
                    'endereco': selected_address
                }
                
                save_order(
                    new_client['id_cliente'],
                    selected_address['id_endereco'],
                    marmitas,
                    bebidas,
                    subtotais['tipo_feijao'],
                    subtotais['total'],
                    subtotais['forma_pagamento'],
                    subtotais['status_pagamento'],
                    subtotais['horario_entrega'],
                    subtotais.get('observacoes'),
                    numero_pedido=numero
                )
                
                mostrar_menu_pos_pedido(pedido, new_client)
    else:
        try:
            client = get_client(int(client_id))
            if client:
                selected_address = show_client_addresses(int(client_id), client['nm_usuario'])
                if selected_address:
                    # Seleção de itens do pedido
                    marmitas = select_marmitas()
                    bebidas = select_bebidas()
                    marmitas = select_adicionais(marmitas)
                    
                    # Mostrar resumo e permitir personalização
                    subtotais = mostrar_resumo_pedido(marmitas, bebidas, selected_address, client)
                    
                    # Salvar pedido
                    numero = get_next_order_number()
                    pedido = {
                        'numero_pedido': numero,
                        'marmitas': json.dumps({
                            'marmitas': [{'tamanho': m['produto']['nome'], 'adicionais': m['adicionais']} for m in marmitas],
                            'bebidas': [{'nome': b['produto']['nome'], 'quantidade': b['quantidade'], 'preco': b['produto']['preco']} for b in bebidas],
                            'tipo_feijao': subtotais['tipo_feijao']
                        }),
                        'preco_total': subtotais['total'],
                        'forma_pagamento': subtotais['forma_pagamento'],
                        'status_pagamento': subtotais['status_pagamento'],
                        'horario_entrega': subtotais['horario_entrega'],
                        'obs': subtotais.get('observacoes'),
                        'endereco': selected_address
                    }
                    
                    save_order(
                        client['id_cliente'],
                        selected_address['id_endereco'],
                        marmitas,
                        bebidas,
                        subtotais['tipo_feijao'],
                        subtotais['total'],
                        subtotais['forma_pagamento'],
                        subtotais['status_pagamento'],
                        subtotais['horario_entrega'],
                        subtotais.get('observacoes'),
                        numero_pedido=numero
                    )
                    
                    mostrar_menu_pos_pedido(pedido, client)
            else:
                console.print("[red]Cliente não encontrado![/red]")
                time.sleep(2)
        except ValueError:
            console.print("[red]Por favor, digite um número válido ou 'novo'[/red]")
            time.sleep(2)
