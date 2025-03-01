from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from database import get_daily_orders, get_order_details, delete_order, update_order, update_order_observation
from database import get_addresses, register_address, supabase
from config import get_auto_print
import time

console = Console()

# Função para atualizar o endereço de um pedido
def update_order_address(order_id, address_id):
    try:
        supabase.table('tb_pedido') \
            .update({'id_endereco': address_id}) \
            .eq('id_pedido', order_id) \
            .execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar endereço do pedido: {str(e)}")
        return False

# Função para atualizar as marmitas do pedido
def update_order_marmitas(order_id, marmitas_json, preco_total=None):
    try:
        import json
        update_data = {'marmitas': json.dumps(marmitas_json)}
        
        # Se o preço total foi fornecido, atualiza também
        if preco_total is not None:
            update_data['preco_total'] = preco_total
            
        supabase.table('tb_pedido') \
            .update(update_data) \
            .eq('id_pedido', order_id) \
            .execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar marmitas do pedido: {str(e)}")
        return False

# Função para editar as marmitas de um pedido
def edit_marmitas(order):
    # Importar funções necessárias de order_items.py
    from order_items import get_products_by_category, selecionar_feijao, calcular_subtotais
    import json
    
    # Obter os produtos do banco de dados para consulta de preço
    from database import get_products_by_category
    marmita_products = get_products_by_category('M')
    bebida_products = get_products_by_category('B')
    adicional_products = get_products_by_category('A')
    
    # Criar dicionários de referência rápida para consulta de preços
    marmita_prices = {produto['nome']: produto['preco'] for produto in marmita_products}
    bebida_prices = {produto['nome']: produto['preco'] for produto in bebida_products}
    adicional_prices = {produto['nome']: produto['preco'] for produto in adicional_products}
    
    if isinstance(order['marmitas'], str):
        marmitas_json = json.loads(order['marmitas'])
    else:
        marmitas_json = order['marmitas']
        
    # Lista de marmitas atual
    marmitas = marmitas_json.get('marmitas', [])
    bebidas = marmitas_json.get('bebidas', [])
    tipo_feijao = marmitas_json.get('tipo_feijao', 'Sem Feijão')
    
    # Manter a estrutura das marmitas como está - não modificar
    
    # Manter a estrutura das bebidas como está - não modificar
    
    while True:
        console.clear()
        console.print(f"[yellow]=== Editando Marmitas do Pedido {order['numero_pedido']} ===[/yellow]\n")
        
        # Mostrar marmitas atuais
        console.print("[cyan]Marmitas Atuais:[/cyan]")
        if marmitas:
            for i, marmita in enumerate(marmitas, 1):
                adicionais_str = ""
                if marmita.get('adicionais'):
                    adicionais_str = " (com: " + ", ".join(a.get('nome', '') for a in marmita.get('adicionais', [])) + ")"
                console.print(f"{i}. Marmita {marmita.get('tamanho', 'Desconhecido')}{adicionais_str}")
        else:
            console.print("[red]Nenhuma marmita adicionada![/red]")
        
        # Mostrar bebidas atuais
        console.print("\n[cyan]Bebidas Atuais:[/cyan]")
        if bebidas:
            for i, bebida in enumerate(bebidas, 1):
                console.print(f"{i}. {bebida.get('quantidade', 1)}x {bebida.get('nome', 'Desconhecido')}")
        else:
            console.print("[red]Nenhuma bebida adicionada![/red]")
        
        # Mostrar tipo de feijão
        console.print(f"\n[cyan]Tipo de Feijão:[/cyan] {tipo_feijao}")
        
        # Menu de opções
        menu_text = """
        1. Adicionar Marmita
        2. Remover Marmita
        3. Adicionar Adicional a uma Marmita
        4. Adicionar Bebida
        5. Remover Bebida
        6. Alterar Tipo de Feijão
        0. Salvar e Voltar
        """
        console.print(f"\n{menu_text}")
        
        opcao = Prompt.ask("Escolha uma opção")
        
        if opcao == "0":
            # Calcular novo total
            # Prepara as marmitas para o cálculo de subtotais, garantindo a estrutura correta
            marmitas_para_calculo = []
            for m in marmitas:
                marmita_calc = {}
                # Copia o produto se existir
                if 'produto' in m and isinstance(m['produto'], dict):
                    marmita_calc['produto'] = m['produto']
                # Se não tiver produto mas tiver tamanho, cria um produto base
                elif 'tamanho' in m:
                    marmita_calc['produto'] = {'nome': m['tamanho']}
                    # Tenta adicionar o preço se disponível no objeto principal
                    if 'preco' in m:
                        marmita_calc['produto']['preco'] = m['preco']
                # Define a quantidade padrão como 1 se não especificada
                marmita_calc['quantidade'] = m.get('quantidade', 1)
                # Copia os adicionais se existirem
                if 'adicionais' in m:
                    marmita_calc['adicionais'] = m['adicionais']
                marmitas_para_calculo.append(marmita_calc)
            
            # Prepara as bebidas para o cálculo
            bebidas_para_calculo = []
            for b in bebidas:
                bebida_calc = {}
                # Copia o produto se existir
                if 'produto' in b and isinstance(b['produto'], dict):
                    bebida_calc['produto'] = b['produto']
                # Se não tiver produto mas tiver nome, cria um produto base
                elif 'nome' in b:
                    bebida_calc['produto'] = {'nome': b['nome']}
                    # Tenta adicionar o preço se disponível no objeto principal
                    if 'preco' in b:
                        bebida_calc['produto']['preco'] = b['preco']
                # Define a quantidade
                bebida_calc['quantidade'] = b.get('quantidade', 1)
                bebidas_para_calculo.append(bebida_calc)
            
            subtotais = calcular_subtotais(marmitas_para_calculo, bebidas_para_calculo)
            
            # Atualizar o pedido
            novo_marmitas_json = {
                "marmitas": marmitas,
                "bebidas": bebidas,
                "tipo_feijao": tipo_feijao
            }
            
            # Importar a função update_order do módulo database
            from database import update_order as db_update_order
            
            if update_order_marmitas(order['id_pedido'], novo_marmitas_json, subtotais['total']) and \
               db_update_order(order['id_pedido'], json.dumps(novo_marmitas_json), 
                         order['forma_pagamento'], order['status_pagamento'], 
                         order.get('horario_entrega')):
                console.print("\n[green]Marmitas atualizadas com sucesso![/green]")
                # Atualizar o objeto order
                order['marmitas'] = json.dumps(novo_marmitas_json)
                order['preco_total'] = subtotais['total']
            else:
                console.print("\n[red]Erro ao atualizar marmitas![/red]")
            
            input("\nPressione Enter para continuar...")
            return
        
        elif opcao == "1":
            # Adicionar Marmita
            console.clear()
            produtos = get_products_by_category('M')
            
            console.print("\n[yellow]Tamanhos disponíveis:[/yellow]")
            for i, produto in enumerate(produtos, 1):
                console.print(f"{i} - {produto['nome']} (R$ {produto['preco']:.2f})")
            
            try:
                escolha = int(Prompt.ask("\nEscolha o tamanho (1-P, 2-M, 3-G)"))
                if 1 <= escolha <= len(produtos):
                    # Criar uma nova marmita com a estrutura exata requerida
                    produto_escolhido = produtos[escolha-1]
                    nova_marmita = {
                        'id': len(marmitas) + 1,
                        'preco': produto_escolhido['preco'],
                        'tamanho': produto_escolhido['nome'],
                        'adicionais': []
                    }
                    marmitas.append(nova_marmita)
                    console.print(f"\n[green]Marmita {produtos[escolha-1]['nome']} adicionada com sucesso![/green]")
                else:
                    console.print("\n[red]Opção inválida![/red]")
            except ValueError:
                console.print("\n[red]Por favor, digite um número válido![/red]")
            
            input("\nPressione Enter para continuar...")
        
        elif opcao == "2":
            # Remover Marmita
            if not marmitas:
                console.print("\n[red]Não há marmitas para remover![/red]")
                input("\nPressione Enter para continuar...")
                continue
                
            try:
                escolha = int(Prompt.ask("\nEscolha o número da marmita para remover"))
                if 1 <= escolha <= len(marmitas):
                    removida = marmitas.pop(escolha-1)
                    console.print(f"\n[green]Marmita {removida.get('tamanho', removida.get('produto', {}).get('nome', 'Desconhecido'))} removida com sucesso![/green]")
                else:
                    console.print("\n[red]Número de marmita inválido![/red]")
            except ValueError:
                console.print("\n[red]Por favor, digite um número válido![/red]")
                
            input("\nPressione Enter para continuar...")
        
        elif opcao == "3":
            # Adicionar Adicional a uma Marmita
            if not marmitas:
                console.print("\n[red]Não há marmitas para adicionar adicionais![/red]")
                input("\nPressione Enter para continuar...")
                continue
                
            console.clear()
            produtos = get_products_by_category('A')
            
            console.print("\n[yellow]Adicionais disponíveis:[/yellow]")
            for i, produto in enumerate(produtos, 1):
                console.print(f"{i} - {produto['nome']} (R$ {produto['preco']:.2f})")
            
            try:
                escolha = int(Prompt.ask("\nEscolha o número do adicional"))
                if 1 <= escolha <= len(produtos):
                    adicional = produtos[escolha-1]
                    
                    # Mostrar marmitas disponíveis
                    console.print("\n[yellow]Marmitas disponíveis:[/yellow]")
                    for i, marmita in enumerate(marmitas, 1):
                        adicionais_str = ""
                        if marmita.get('adicionais'):
                            adicionais_str = " (com: " + ", ".join(a.get('nome', '') for a in marmita.get('adicionais', [])) + ")"
                        console.print(f"{i} - Marmita {marmita.get('tamanho', 'Desconhecido')}{adicionais_str}")
                    
                    try:
                        marmita_escolhida = int(Prompt.ask("\nEm qual marmita adicionar"))
                        if 1 <= marmita_escolhida <= len(marmitas):
                            if 'adicionais' not in marmitas[marmita_escolhida-1]:
                                marmitas[marmita_escolhida-1]['adicionais'] = []
                            # Adicionar apenas com a estrutura requerida: nome e preço
                            marmitas[marmita_escolhida-1]['adicionais'].append({
                                'nome': adicional['nome'],
                                'preco': adicional['preco']
                            })
                            console.print(f"\n[green]Adicional {adicional['nome']} adicionado à marmita {marmita_escolhida}![/green]")
                        else:
                            console.print("\n[red]Número de marmita inválido![/red]")
                    except ValueError:
                        console.print("\n[red]Por favor, digite um número válido![/red]")
                else:
                    console.print("\n[red]Opção inválida![/red]")
            except ValueError:
                console.print("\n[red]Por favor, digite um número válido![/red]")
                
            input("\nPressione Enter para continuar...")
        
        elif opcao == "4":
            # Adicionar Bebida
            console.clear()
            produtos = get_products_by_category('B')
            
            console.print("\n[yellow]Bebidas disponíveis:[/yellow]")
            for i, produto in enumerate(produtos, 1):
                console.print(f"{i} - {produto['nome']} (R$ {produto['preco']:.2f})")
            
            try:
                escolha = int(Prompt.ask("\nEscolha o número da bebida"))
                if 1 <= escolha <= len(produtos):
                    quantidade = int(Prompt.ask("Quantidade"))
                    if quantidade > 0:
                        bebida = {
                            'nome': produtos[escolha-1]['nome'],
                            'preco': produtos[escolha-1]['preco'],
                            'quantidade': quantidade
                        }
                        bebidas.append(bebida)
                        console.print(f"\n[green]{quantidade}x {produtos[escolha-1]['nome']} adicionado(s) com sucesso![/green]")
                    else:
                        console.print("\n[red]Quantidade deve ser maior que zero![/red]")
                else:
                    console.print("\n[red]Opção inválida![/red]")
            except ValueError:
                console.print("\n[red]Por favor, digite um número válido![/red]")
                
            input("\nPressione Enter para continuar...")
        
        elif opcao == "5":
            # Remover Bebida
            if not bebidas:
                console.print("\n[red]Não há bebidas para remover![/red]")
                input("\nPressione Enter para continuar...")
                continue
                
            try:
                escolha = int(Prompt.ask("\nEscolha o número da bebida para remover"))
                if 1 <= escolha <= len(bebidas):
                    removida = bebidas.pop(escolha-1)
                    console.print(f"\n[green]{removida.get('quantidade', 1)}x {removida.get('nome', 'Desconhecido')} removido(s) com sucesso![/green]")
                else:
                    console.print("\n[red]Número de bebida inválido![/red]")
            except ValueError:
                console.print("\n[red]Por favor, digite um número válido![/red]")
                
            input("\nPressione Enter para continuar...")
        
        elif opcao == "6":
            # Alterar Tipo de Feijão
            novo_feijao = selecionar_feijao()
            tipo_feijao = novo_feijao
            console.print(f"\n[green]Tipo de feijão alterado para {tipo_feijao}![/green]")
            input("\nPressione Enter para continuar...")

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

# Função para obter dados de novo endereço
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

def edit_order(order):
    console.clear()
    console.print(f"[yellow]=== Editando Pedido {order['numero_pedido']} ===[/yellow]\n")
    
    # Definir endereco_atual no início da função para evitar UnboundLocalError
    endereco_atual = order['tb_endereco']
    
    # Menu de opções de edição
    menu_text = """
1. Forma de Pagamento
2. Status do Pagamento
3. Horário de Entrega
4. Observação
5. Endereço de Entrega
6. Editar Marmitas
0. Voltar
    """
    menu_panel = Panel(menu_text, title="O que deseja editar?", border_style="yellow")
    
    while True:
        console.print("\n")
        console.print(menu_panel)
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            # Editar forma de pagamento
            formas_pagamento = ["Dinheiro", "Cartão", "PIX"]
            console.clear()
            console.print("\n[cyan]Forma de pagamento atual:[/cyan] " + order['forma_pagamento'])
            console.print("\n[cyan]Formas de pagamento disponíveis:[/cyan]")
            for i, forma in enumerate(formas_pagamento, 1):
                console.print(f"{i}. {forma}")
            forma_idx = int(Prompt.ask("\nEscolha a forma de pagamento", default=str(formas_pagamento.index(order['forma_pagamento']) + 1)))
            forma_pagamento = formas_pagamento[forma_idx - 1]
            
            if forma_pagamento != order['forma_pagamento']:
                if update_order(order['id_pedido'], order['marmitas'], forma_pagamento, order['status_pagamento'], order.get('horario_entrega')):
                    console.print("\n[green]Forma de pagamento atualizada com sucesso![/green]")
                    order['forma_pagamento'] = forma_pagamento
                else:
                    console.print("\n[red]Erro ao atualizar forma de pagamento![/red]")
            else:
                console.print("\n[yellow]Forma de pagamento não foi alterada![/yellow]")
            
            input("\nPressione Enter para continuar...")
            console.clear()
            
        elif opcao == "2":
            # Editar status do pagamento
            status_opcoes = ["Pendente", "Pago"]
            console.clear()
            console.print("\n[cyan]Status de pagamento atual:[/cyan] " + order['status_pagamento'])
            console.print("\n[cyan]Status de pagamento disponíveis:[/cyan]")
            for i, status in enumerate(status_opcoes, 1):
                console.print(f"{i}. {status}")
            status_idx = int(Prompt.ask("\nEscolha o status do pagamento", default=str(status_opcoes.index(order['status_pagamento']) + 1)))
            status_pagamento = status_opcoes[status_idx - 1]
            
            if status_pagamento != order['status_pagamento']:
                if update_order(order['id_pedido'], order['marmitas'], order['forma_pagamento'], status_pagamento, order.get('horario_entrega')):
                    console.print("\n[green]Status do pagamento atualizado com sucesso![/green]")
                    order['status_pagamento'] = status_pagamento
                else:
                    console.print("\n[red]Erro ao atualizar status do pagamento![/red]")
            else:
                console.print("\n[yellow]Status do pagamento não foi alterado![/yellow]")
            
            input("\nPressione Enter para continuar...")
            console.clear()
            
        elif opcao == "3":
            # Editar horário de entrega
            console.clear()
            horario_atual = order.get('horario_entrega', '')
            console.print("\n[cyan]Horário de entrega atual:[/cyan] " + horario_atual)
            horario_entrega = Prompt.ask("\nNovo horário de entrega (HH:MM) ou Enter para manter", default=horario_atual)
            
            if horario_entrega != horario_atual:
                if update_order(order['id_pedido'], order['marmitas'], order['forma_pagamento'], order['status_pagamento'], horario_entrega):
                    console.print("\n[green]Horário de entrega atualizado com sucesso![/green]")
                    order['horario_entrega'] = horario_entrega
                else:
                    console.print("\n[red]Erro ao atualizar horário de entrega![/red]")
            else:
                console.print("\n[yellow]Horário de entrega não foi alterado![/yellow]")
            
            input("\nPressione Enter para continuar...")
            console.clear()
            
        elif opcao == "4":
            # Editar observação
            console.clear()
            obs_atual = order.get('obs', 'Nenhuma observação')
            if obs_atual is None:
                obs_atual = 'Nenhuma observação'
            console.print(f"\n[cyan]Observação atual:[/cyan] {obs_atual}")
            nova_obs = Prompt.ask("\nNova observação ou Enter para manter", default=obs_atual)
            
            if nova_obs != obs_atual:
                if update_order_observation(order['id_pedido'], nova_obs):
                    console.print("\n[green]Observação atualizada com sucesso![/green]")
                    order['obs'] = nova_obs
                else:
                    console.print("\n[red]Erro ao atualizar observação![/red]")
            else:
                console.print("\n[yellow]Observação não foi alterada![/yellow]")
            
            input("\nPressione Enter para continuar...")
            console.clear()
            
        elif opcao == "5":
            # Escolher endereço de entrega dentre os cadastrados
            console.clear()
            endereco_atual = order['tb_endereco']
            console.print("\n[cyan]Endereço atual:[/cyan]")
            console.print(f"Rua: {endereco_atual['rua']}")
            console.print(f"Bairro: {endereco_atual['bairro']}")
            console.print(f"Referência: {endereco_atual.get('referencia', 'Nenhuma')}")
            
            # Função local para obter novos dados de endereço
            def get_new_address():
                while True:
                    console.clear()
                    console.print("\n[yellow]Digite os dados do novo endereço:[/yellow]")
                    
                    rua = Prompt.ask("[yellow]Digite a rua[/yellow]").strip()
                    if not rua:
                        console.print("\n[red]A rua é obrigatória![/red]")
                        input("\nPressione Enter para continuar...")
                        continue
                        
                    bairro = Prompt.ask("[yellow]Digite o bairro[/yellow]").strip()
                    if not bairro:
                        console.print("\n[red]O bairro é obrigatório![/red]")
                        input("\nPressione Enter para continuar...")
                        continue
                        
                    referencia = Prompt.ask("[yellow]Digite uma referência (opcional)[/yellow]").strip()
                    if not referencia:
                        referencia = None
                        
                    return rua, bairro, referencia
            
            # Loop para seleção de endereço
            while True:
                console.clear()
                console.print(f"\n[cyan]Endereço atual:[/cyan]")
                console.print(f"Rua: {endereco_atual['rua']}")
                console.print(f"Bairro: {endereco_atual['bairro']}")
                if endereco_atual.get('referencia'):
                    console.print(f"Referência: {endereco_atual['referencia']}")
                
                # Busca endereços
                addresses = get_addresses(order['id_cliente'])
                
                if addresses:
                    console.print("\n[yellow]Endereços disponíveis:[/yellow]")
                    for i, address in enumerate(addresses, 1):
                        console.print(f"{i} - Rua: {address['rua']}, Bairro: {address['bairro']}")
                    console.print(f"{len(addresses) + 1} - Adicionar novo endereço")
                    console.print("0 - Voltar")
                    
                    opcao_end = Prompt.ask("\nEscolha um endereço", default="0")
                    
                    if opcao_end == "0":
                        break
                    elif opcao_end.isdigit() and 1 <= int(opcao_end) <= len(addresses):
                        # Atualiza o endereço do pedido
                        address_id = addresses[int(opcao_end) - 1]['id_endereco']
                        if update_order_address(order['id_pedido'], address_id):
                            console.print("\n[green]Endereço atualizado com sucesso![/green]")
                            # Atualizar o objeto order com o novo endereço
                            order['tb_endereco'] = addresses[int(opcao_end) - 1]
                            order['id_endereco'] = address_id
                        else:
                            console.print("\n[red]Erro ao atualizar endereço![/red]")
                        input("\nPressione Enter para continuar...")
                        break
                    elif opcao_end.isdigit() and int(opcao_end) == len(addresses) + 1:
                        # Adicionar novo endereço
                        rua, bairro, referencia = get_new_address()
                        novo_endereco = add_address(order['id_cliente'], rua, bairro, referencia)
                        if novo_endereco and novo_endereco.get('id_endereco'):
                            if update_order_address(order['id_pedido'], novo_endereco['id_endereco']):
                                console.print("\n[green]Novo endereço adicionado e associado ao pedido com sucesso![/green]")
                                # Atualizar o objeto order com o novo endereço
                                order['tb_endereco'] = novo_endereco
                                order['id_endereco'] = novo_endereco['id_endereco']
                            else:
                                console.print("\n[red]Erro ao atualizar endereço do pedido![/red]")
                        else:
                            console.print("\n[red]Erro ao adicionar novo endereço![/red]")
                        input("\nPressione Enter para continuar...")
                        break
                    else:
                        console.print("\n[red]Opção inválida![/red]")
                        input("\nPressione Enter para continuar...")
                else:
                    console.print("\n[red]Nenhum endereço cadastrado para este cliente![/red]")
                    console.print("1 - Adicionar novo endereço")
                    console.print("0 - Voltar")
                    
                    opcao_end = Prompt.ask("\nEscolha uma opção", default="0")
                    
                    if opcao_end == "0":
                        break
                    elif opcao_end == "1":
                        # Adicionar novo endereço
                        rua, bairro, referencia = get_new_address()
                        novo_endereco = add_address(order['id_cliente'], rua, bairro, referencia)
                        if novo_endereco and novo_endereco.get('id_endereco'):
                            if update_order_address(order['id_pedido'], novo_endereco['id_endereco']):
                                console.print("\n[green]Novo endereço adicionado e associado ao pedido com sucesso![/green]")
                                # Atualizar o objeto order com o novo endereço
                                order['tb_endereco'] = novo_endereco
                                order['id_endereco'] = novo_endereco['id_endereco']
                            else:
                                console.print("\n[red]Erro ao atualizar endereço do pedido![/red]")
                        else:
                            console.print("\n[red]Erro ao adicionar novo endereço![/red]")
                        input("\nPressione Enter para continuar...")
                        break
                    else:
                        console.print("\n[red]Opção inválida![/red]")
                        input("\nPressione Enter para continuar...")
            
        elif opcao == "6":
            # Editar marmitas
            console.clear()
            edit_marmitas(order)
            
            console.clear()
            
        elif opcao == "0":
            return
        else:
            console.print("\n[red]Opção inválida![/red]")
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
        if update_order(order['id_pedido'], order['marmitas'], order['forma_pagamento'], status_pagamento, order.get('horario_entrega')):
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
    
    # # Verificar se a impressão automática está habilitada
    # auto_print = get_auto_print()
    # if auto_print:
    #     from printer import imprimir_pedido
    #     imprimir_pedido(order, order['tb_cliente'])
    #     console.print("\n[green]Pedido impresso automaticamente![/green]")
    
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
                if delete_order(order['id_pedido']):
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
