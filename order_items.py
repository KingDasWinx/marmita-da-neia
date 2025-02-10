from rich.console import Console
from rich.prompt import Prompt
from database import get_products_by_category
import os
import time

console = Console()

def select_marmitas():
    marmitas = []
    adicionar = '1'
    
    while adicionar == '1':
        console.clear()
        produtos = get_products_by_category('M')
        
        console.print("\n[yellow]Tamanhos disponíveis:[/yellow]")
        for i, produto in enumerate(produtos, 1):
            console.print(f"{i} - {produto['nome']} (R$ {produto['preco']:.2f})")
        
        try:
            escolha = int(Prompt.ask("\nEscolha o tamanho (1-P, 2-M, 3-G)"))
            if 1 <= escolha <= len(produtos):
                quantidade = int(Prompt.ask("Quantidade"))
                if quantidade > 0:
                    # Criar uma entrada individual para cada marmita
                    for _ in range(quantidade):
                        marmita = {
                            'produto': produtos[escolha-1],
                            'quantidade': 1,
                            'adicionais': []
                        }
                        marmitas.append(marmita)
                    
                    adicionar = Prompt.ask("\nAdicionar mais marmitas? (1 - Sim, 2 - Não)")
                else:
                    console.print("[red]Quantidade deve ser maior que zero![/red]")
            else:
                console.print("[red]Opção inválida![/red]")
        except ValueError:
            console.print("[red]Por favor, digite um número válido![/red]")
    
    return marmitas

def select_bebidas():
    bebidas = []
    adicionar = Prompt.ask("\nDeseja adicionar bebida? (1 - Sim, 2 - Não)")
    
    while adicionar == '1':
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
                        'produto': produtos[escolha-1],
                        'quantidade': quantidade
                    }
                    bebidas.append(bebida)
                    
                    adicionar = Prompt.ask("\nAdicionar mais bebidas? (1 - Sim, 2 - Não)")
                else:
                    console.print("[red]Quantidade deve ser maior que zero![/red]")
            else:
                console.print("[red]Opção inválida![/red]")
        except ValueError:
            console.print("[red]Por favor, digite um número válido![/red]")
    
    return bebidas

def select_adicionais(marmitas):
    adicionar = Prompt.ask("\nDeseja adicionar adicionais? (1 - Sim, 2 - Não)")
    
    while adicionar == '1':
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
                    if marmita['adicionais']:
                        adicionais_str = " (com: " + ", ".join(a['nome'] for a in marmita['adicionais']) + ")"
                    console.print(f"{i} - Marmita {marmita['produto']['nome']}{adicionais_str}")
                
                try:
                    marmita_escolhida = int(Prompt.ask("\nEm qual marmita adicionar"))
                    if 1 <= marmita_escolhida <= len(marmitas):
                        marmitas[marmita_escolhida-1]['adicionais'].append(adicional)
                        console.print(f"[green]Adicional {adicional['nome']} adicionado à marmita {marmita_escolhida}![/green]")
                    else:
                        console.print("[red]Número de marmita inválido![/red]")
                except ValueError:
                    console.print("[red]Por favor, digite um número válido![/red]")
                
                adicionar = Prompt.ask("\nDeseja adicionar mais adicionais? (1 - Sim, 2 - Não)")
            else:
                console.print("[red]Opção inválida![/red]")
        except ValueError:
            console.print("[red]Por favor, digite um número válido![/red]")
    
    return marmitas

def calcular_subtotais(marmitas, bebidas):
    subtotal_marmitas = sum(m['produto']['preco'] * m['quantidade'] for m in marmitas)
    subtotal_bebidas = sum(b['produto']['preco'] * b['quantidade'] for b in bebidas)
    subtotal_adicionais = sum(
        sum(a['preco'] for a in m['adicionais'])
        for m in marmitas
    )
    
    total = subtotal_marmitas + subtotal_bebidas + subtotal_adicionais
    
    return {
        'marmitas': subtotal_marmitas,
        'bebidas': subtotal_bebidas,
        'adicionais': subtotal_adicionais,
        'total': total
    }

def selecionar_feijao():
    while True:
        tipo_feijao = Prompt.ask("\nEscolha o tipo de feijão (0 - Sem Feijão, 1 - Feijão Carioca, 2 - Feijão Preto)")
        if tipo_feijao in ['0', '1', '2']:
            return {
                '0': 'Sem Feijão',
                '1': 'Feijão Carioca',
                '2': 'Feijão Preto'
            }[tipo_feijao]
        console.print("[red]Opção inválida![/red]")

def processar_pagamento():
    console.print("\n[yellow]Forma de pagamento:[/yellow]")
    console.print("1 - PIX")
    console.print("2 - Cartão")
    console.print("3 - Dinheiro")
    console.print("4 - Outro")
    
    while True:
        forma = Prompt.ask("\nEscolha a forma de pagamento")
        
        if forma == '1':  # PIX
            while True:
                pago = Prompt.ask("Pagamento realizado? (1 - Sim, 2 - Não)")
                if pago == '1':
                    return {'forma': 'PIX', 'status': 'Pago'}
                elif pago == '2':
                    return {'forma': 'PIX', 'status': 'Não Pago'}
                console.print("[red]Opção inválida. Digite 1 para Sim ou 2 para Não.[/red]")
        
        elif forma in ['2', '3']:  # Cartão ou Dinheiro
            return {
                'forma': 'Cartão' if forma == '2' else 'Dinheiro',
                'status': 'Pendente'
            }
        
        elif forma == '4':  # Outro
            descricao = Prompt.ask("Digite a descrição da forma de pagamento")
            return {
                'forma': descricao,
                'status': descricao
            }
        
        else:
            console.print("[red]Opção inválida![/red]")

def mostrar_detalhes_pedido(marmitas, bebidas, subtotais, endereco, cliente):
    console.clear()
    console.print("\n[yellow]====== DETALHES DO PEDIDO ======[/yellow]")
    console.print(f"\n[blue]Cliente:[/blue] {cliente['nm_usuario']}")
    console.print(f"[blue]Endereço:[/blue] {endereco['rua']}, {endereco['bairro']}")
    if endereco.get('referencia'):
        console.print(f"[blue]Referência:[/blue] {endereco['referencia']}")
    
    console.print(f"\n[blue]Horário de entrega:[/blue] {subtotais['horario_entrega']}")
    if subtotais.get('observacoes'):
        console.print(f"[blue]Observações:[/blue] {subtotais['observacoes']}")
    
    console.print("\n[green]Marmitas:[/green]")
    for i, marmita in enumerate(marmitas, 1):
        console.print(f"{i}. {marmita['produto']['nome']} - R$ {marmita['produto']['preco']:.2f}")
        if marmita['adicionais']:
            for adicional in marmita['adicionais']:
                console.print(f"   + {adicional['nome']} - R$ {adicional['preco']:.2f}")
    
    if bebidas:
        console.print("\n[green]Bebidas:[/green]")
        for bebida in bebidas:
            console.print(f"{bebida['produto']['nome']} x{bebida['quantidade']} - R$ {bebida['produto']['preco'] * bebida['quantidade']:.2f}")
    
    console.print(f"\n[blue]Tipo de feijão:[/blue] {subtotais['tipo_feijao']}")
    console.print(f"\n[yellow]Subtotal marmitas:[/yellow] R$ {subtotais['marmitas']:.2f}")
    console.print(f"[yellow]Subtotal bebidas:[/yellow] R$ {subtotais['bebidas']:.2f}")
    console.print(f"[yellow]Subtotal adicionais:[/yellow] R$ {subtotais['adicionais']:.2f}")
    console.print(f"[green]Total:[/green] R$ {subtotais['total']:.2f}")
    
    console.print(f"\n[blue]Forma de pagamento:[/blue] {subtotais['forma_pagamento']}")
    console.print(f"[blue]Status do pagamento:[/blue] {subtotais['status_pagamento']}")
    
    console.print("\n[yellow]================================[/yellow]")

def mostrar_resumo_pedido(marmitas, bebidas, endereco, cliente):
    console.clear()
    subtotais = calcular_subtotais(marmitas, bebidas)
    
    # Seleciona tipo de feijão (obrigatório)
    tipo_feijao = selecionar_feijao()
    
    console.print("\n[yellow]Resumo do pedido:[/yellow]")
    console.print(f"Subtotal marmitas: R$ {subtotais['marmitas']:.2f}")
    console.print(f"Subtotal bebidas: R$ {subtotais['bebidas']:.2f}")
    console.print(f"Subtotal adicionais: R$ {subtotais['adicionais']:.2f}")
    console.print(f"[green]Total: R$ {subtotais['total']:.2f}[/green]")
    console.print(f"Tipo de feijão: {tipo_feijao}")
    
    personalizar = Prompt.ask("\nDeseja personalizar o total? (1 - Sim, 2 - Não)")
    if personalizar == '1':
        while True:
            try:
                novo_total = float(Prompt.ask("\nDigite o novo valor total"))
                if novo_total >= 0:
                    subtotais['total'] = novo_total
                    console.print(f"\n[green]Novo total: R$ {novo_total:.2f}[/green]")
                    break
                else:
                    console.print("[red]O valor não pode ser negativo![/red]")
            except ValueError:
                console.print("[red]Por favor, digite um valor válido![/red]")
    
    # Processa pagamento
    pagamento = processar_pagamento()
    
    # Horário de entrega e observações
    horario = Prompt.ask("\nHorário para entrega")
    observacoes = Prompt.ask("Observações (opcional)")
    
    subtotais.update({
        'tipo_feijao': tipo_feijao,
        'forma_pagamento': pagamento['forma'],
        'status_pagamento': pagamento['status'],
        'horario_entrega': horario,
        'observacoes': observacoes if observacoes else None
    })
    
    # Mostra resumo detalhado final
    mostrar_detalhes_pedido(marmitas, bebidas, subtotais, endereco, cliente)    
    return subtotais
