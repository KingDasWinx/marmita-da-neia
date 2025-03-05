from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from database import get_client, register_client, register_address
import time

# Implementações locais para funções que faltam no módulo database
from database import supabase

def get_all_clients():
    """Retorna todos os clientes cadastrados"""
    try:
        response = supabase.table('tb_cliente').select('*').execute()
        return response.data
    except Exception as e:
        print(f"Erro ao buscar todos os clientes: {str(e)}")
        return []

def get_client_addresses(client_id):
    """Retorna os endereços de um cliente específico"""
    try:
        response = supabase.table('tb_endereco').select('*').eq('id_cliente', client_id).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao buscar endereços do cliente: {str(e)}")
        return []

def update_client_name(client_id, new_name):
    """Atualiza o nome de um cliente"""
    try:
        supabase.table('tb_cliente').update({'nm_usuario': new_name}).eq('id_cliente', client_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar nome do cliente: {str(e)}")
        return False

def delete_client(client_id):
    """Remove um cliente e seus endereços do banco de dados"""
    try:
        # Primeiro remove os endereços do cliente
        supabase.table('tb_endereco').delete().eq('id_cliente', client_id).execute()
        # Depois remove o cliente
        supabase.table('tb_cliente').delete().eq('id_cliente', client_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir cliente: {str(e)}")
        return False

def delete_address(address_id):
    """Remove um endereço específico"""
    try:
        supabase.table('tb_endereco').delete().eq('id_endereco', address_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir endereço: {str(e)}")
        return False
        
def update_address(address_id, new_data):
    """Atualiza os dados de um endereço"""
    try:
        supabase.table('tb_endereco').update(new_data).eq('id_endereco', address_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar endereço: {str(e)}")
        return False

console = Console()

def edit_address(address):
    """Permite editar os dados de um endereço existente"""
    address_id = address['id_endereco']
    
    while True:
        console.clear()
        title = "[bold yellow]=== Editar Endereço ===[/bold yellow]"
        console.print(title)
        
        # Painel com as informações atuais do endereço
        current_info = f"""
[cyan]Informações Atuais:[/cyan]

[bold]ID:[/bold] {address['id_endereco']}
[bold]Rua e Número:[/bold] {address['rua']}
[bold]Bairro:[/bold] {address['bairro']}
[bold]Referência:[/bold] {address.get('referencia', '-')}
        """
        info_panel = Panel(current_info, border_style="blue")
        console.print(info_panel)
        
        # Instruções para a edição
        instructions = Panel(
            "[cyan]Edite as informações do endereço.[/cyan]\n" +
            "[white]Deixe em branco para manter o valor atual.[/white]",
            border_style="yellow",
            padding=(1, 2)
        )
        console.print(instructions)
        
        # Formulário de entrada para novos valores
        console.print("\n[bold]Novos dados (deixe vazio para manter atual):[/bold]")
        
        console.print(f"[yellow]Rua e Número (atual: {address['rua']}):[/yellow]")
        rua = Prompt.ask(" ", default="").strip()
        rua = rua if rua else address['rua']
        
        console.print(f"[yellow]Bairro (atual: {address['bairro']}):[/yellow]")
        bairro = Prompt.ask(" ", default="").strip()
        bairro = bairro if bairro else address['bairro']
        
        console.print(f"[yellow]Referência (atual: {address.get('referencia', '-')}):[/yellow]")
        referencia = Prompt.ask(" ", default="").strip()
        referencia = referencia if referencia else address.get('referencia')
        
        # Confirmação dos novos dados
        summary_text = f"""
[cyan]Novos dados do endereço:[/cyan]

[bold]Rua e Número:[/bold] {rua}
[bold]Bairro:[/bold] {bairro}
[bold]Referência:[/bold] {referencia if referencia else '-'}
        """
        summary_panel = Panel(summary_text, title="Confirmação", border_style="green")
        console.print(summary_panel)
        
        if Prompt.ask("\n[yellow]Confirma as alterações? (S/N)[/yellow]", choices=["S", "N"], default="S").upper() == "N":
            if Prompt.ask("\n[yellow]Deseja cancelar a edição? (S/N)[/yellow]", choices=["S", "N"], default="N").upper() == "S":
                console.print("[yellow]Edição cancelada.[/yellow]")
                input("\nPressione Enter para continuar...")
                return
            continue
        
        # Atualizar o endereço
        new_data = {
            'rua': rua,
            'bairro': bairro,
            'referencia': referencia if referencia else None
        }
        
        if update_address(address_id, new_data):
            success_panel = Panel("[green]Endereço atualizado com sucesso![/green]", border_style="green")
            console.print(success_panel)
        else:
            error_panel = Panel("[red]Erro ao atualizar endereço![/red]", border_style="red")
            console.print(error_panel)
            
        input("\nPressione Enter para continuar...")
        return

def get_new_address(client_id):
    """Obtém informações para cadastro de novo endereço"""
    while True:
        console.clear()
        title = "[bold yellow]=== Cadastro de Novo Endereço ===[/bold yellow]"
        console.print(title)
        
        # Painel com as instruções
        instructions = Panel(
            "[cyan]Preencha as informações do novo endereço.[/cyan]\n" +
            "[white]Os campos marcados com [red]*[/red] são obrigatórios.[/white]",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(instructions)
        
        # Formulário de entrada
        console.print("\n[bold]Informações do Endereço:[/bold]")
        console.print("[red]*[/red] [yellow]Rua e Número:[/yellow]")
        rua = Prompt.ask(" ").strip()
        if not rua:
            error_panel = Panel("[red]A rua não pode ficar vazia![/red]", border_style="red")
            console.print(error_panel)
            input("\nPressione Enter para continuar...")
            continue
            
        console.print("[red]*[/red] [yellow]Bairro:[/yellow]")
        bairro = Prompt.ask(" ").strip()
        if not bairro:
            error_panel = Panel("[red]O bairro não pode ficar vazio![/red]", border_style="red")
            console.print(error_panel)
            input("\nPressione Enter para continuar...")
            continue
            
        console.print("[yellow]Referência (opcional):[/yellow]")
        referencia = Prompt.ask(" ").strip()
        
        # Resumo dos dados inseridos
        summary_text = f"""
[cyan]Resumo do Endereço:[/cyan]

[bold]Rua e Número:[/bold] {rua}
[bold]Bairro:[/bold] {bairro}
[bold]Referência:[/bold] {referencia if referencia else '-'}
        """
        summary_panel = Panel(summary_text, title="Confirmação", border_style="green")
        console.print(summary_panel)
        
        if Prompt.ask("\n[yellow]Os dados estão corretos? (S/N)[/yellow]", choices=["S", "N"], default="S").upper() == "N":
            continue
        
        address_data = {
            'id_cliente': client_id,
            'rua': rua,
            'bairro': bairro,
            'referencia': referencia if referencia else None
        }
        
        return address_data

def listar_enderecos(client_id, client_name):
    """Lista todos os endereços de um cliente e permite gerenciá-los"""
    while True:
        console.clear()
        title = f"[bold yellow]=== Endereços de {client_name} ===[/bold yellow]"
        console.print(title)
        
        addresses = get_client_addresses(client_id)
        
        if not addresses:
            empty_panel = Panel("[yellow]Este cliente não possui endereços cadastrados.[/yellow]", border_style="yellow")
            console.print(empty_panel)
            
            add_question = Panel("[cyan]Deseja cadastrar um novo endereço?[/cyan]", border_style="blue")
            console.print(add_question)
            
            if Prompt.ask("\n[yellow]Confirma? (S/N)[/yellow]", choices=["S", "N"], default="S").upper() == "S":
                new_address = get_new_address(client_id)
                address_id = register_address(new_address['id_cliente'], new_address['rua'], 
                                          new_address['bairro'], new_address['referencia'])
                if address_id:
                    console.print("[green]Endereço cadastrado com sucesso![/green]")
                else:
                    console.print("[red]Erro ao cadastrar endereço![/red]")
                input("\nPressione Enter para continuar...")
                continue
            else:
                return
        
        # Tabela de endereços com estilo aprimorado
        table = Table(show_header=True, header_style="bold magenta", box=None, border_style="blue")
        table.add_column("ID", justify="center", style="cyan")
        table.add_column("Rua", style="green")
        table.add_column("Bairro", style="green")
        table.add_column("Referência", style="green")
        
        for addr in addresses:
            table.add_row(
                str(addr['id_endereco']),
                addr['rua'],
                addr['bairro'],
                addr.get('referencia', '')
            )
        
        # Envolvendo a tabela em um painel
        addresses_panel = Panel(table, title="Endereços Cadastrados", border_style="blue", padding=(1, 2))
        console.print(addresses_panel)
        
        # Opções em um painel separado
        options_text = """
[cyan]Opções disponíveis:[/cyan]

[green]1.[/green] Adicionar novo endereço
[green]2.[/green] Editar endereço existente
[green]3.[/green] Excluir endereço
[green]0.[/green] Voltar
        """
        options_panel = Panel(options_text, border_style="yellow")
        console.print(options_panel)
        
        opcao = Prompt.ask("\n[yellow]Escolha uma opção[/yellow]", choices=["1", "2", "3", "0"], default="0")
        
        if opcao == "1":
            new_address = get_new_address(client_id)
            address_id = register_address(new_address['id_cliente'], new_address['rua'], 
                                      new_address['bairro'], new_address['referencia'])
            if address_id:
                console.print("[green]Endereço cadastrado com sucesso![/green]")
            else:
                console.print("[red]Erro ao cadastrar endereço![/red]")
            input("\nPressione Enter para continuar...")
            
        elif opcao == "2":
            id_endereco = Prompt.ask("\nDigite o ID do endereço que deseja editar")
            
            # Verificar se o ID pertence a um endereço deste cliente
            if not any(str(addr['id_endereco']) == id_endereco for addr in addresses):
                console.print("[red]ID de endereço inválido![/red]")
                input("\nPressione Enter para continuar...")
                continue
                
            # Encontrar o endereço selecionado
            selected_address = next(addr for addr in addresses if str(addr['id_endereco']) == id_endereco)
            edit_address(selected_address)
            
        elif opcao == "3":
            id_endereco = Prompt.ask("\nDigite o ID do endereço que deseja excluir")
            
            # Verificar se o ID pertence a um endereço deste cliente
            if not any(str(addr['id_endereco']) == id_endereco for addr in addresses):
                console.print("[red]ID de endereço inválido![/red]")
                input("\nPressione Enter para continuar...")
                continue
                
            if Prompt.ask("Tem certeza que deseja excluir este endereço? (S/N)", default="N").upper() == "S":
                if delete_address(id_endereco):
                    console.print("[green]Endereço excluído com sucesso![/green]")
                else:
                    console.print("[red]Erro ao excluir endereço![/red]")
                input("\nPressione Enter para continuar...")
            
        elif opcao == "0":
            return
        
        else:
            console.print("[red]Opção inválida![/red]")
            input("\nPressione Enter para continuar...")

def editar_cliente(client_id):
    """Permite editar os dados de um cliente"""
    client = get_client(client_id)
    if not client:
        console.print("[red]Cliente não encontrado![/red]")
        input("\nPressione Enter para continuar...")
        return
    
    console.clear()
    
    # Cria um painel com informações do cliente
    info_text = f"""
[cyan]Informações do Cliente:[/cyan]

[bold]ID:[/bold] {client_id}
[bold]Nome:[/bold] {client['nm_usuario']}
    """
    
    # Cria um painel com as opções de edição
    options_text = """
[cyan]Opções disponíveis:[/cyan]

[green]1.[/green] Alterar Nome
[green]2.[/green] Gerenciar Endereços
[green]3.[/green] Excluir Cliente
[green]0.[/green] Voltar
    """
    
    title = f"[bold yellow]=== Editar Cliente ===[/bold yellow]"
    info_panel = Panel(info_text, border_style="blue")
    options_panel = Panel(options_text, border_style="yellow")
    
    console.print(title)
    console.print(info_panel)
    console.print(options_panel)
    
    opcao = Prompt.ask("\n[yellow]Escolha uma opção[/yellow]", choices=["1", "2", "3", "0"], default="0")
    
    if opcao == "1":
        novo_nome = Prompt.ask("Digite o novo nome para o cliente", default=client['nm_usuario'])
        if novo_nome.strip() and novo_nome != client['nm_usuario']:
            if update_client_name(client_id, novo_nome):
                console.print("[green]Nome atualizado com sucesso![/green]")
            else:
                console.print("[red]Erro ao atualizar nome![/red]")
        else:
            console.print("[yellow]Nome não alterado.[/yellow]")
        input("\nPressione Enter para continuar...")
        editar_cliente(client_id)  # Retorna à tela de edição
        
    elif opcao == "2":
        listar_enderecos(client_id, client['nm_usuario'])
        editar_cliente(client_id)  # Retorna à tela de edição
        
    elif opcao == "3":
        confirmacao = Prompt.ask(
            f"[red]ATENÇÃO: Deseja realmente excluir o cliente '{client['nm_usuario']}' e todos os seus endereços?[/red] (S/N)", 
            default="N"
        )
        if confirmacao.upper() == "S":
            confirmacao2 = Prompt.ask(
                "[red]Esta ação não pode ser desfeita. Digite 'CONFIRMAR' para prosseguir[/red]"
            )
            if confirmacao2 == "CONFIRMAR":
                if delete_client(client_id):
                    console.print("[green]Cliente e seus endereços excluídos com sucesso![/green]")
                    input("\nPressione Enter para continuar...")
                    return
                else:
                    console.print("[red]Erro ao excluir cliente![/red]")
                    input("\nPressione Enter para continuar...")
                    editar_cliente(client_id)
            else:
                console.print("[yellow]Operação cancelada.[/yellow]")
                input("\nPressione Enter para continuar...")
                editar_cliente(client_id)
        else:
            editar_cliente(client_id)
            
    elif opcao == "0":
        return

def novo_cliente():
    """Cadastra um novo cliente"""
    console.clear()
    title = "[bold yellow]=== Cadastro de Novo Cliente ===[/bold yellow]"
    console.print(title)
    
    # Painel com as instruções
    instructions = Panel(
        "[cyan]Preencha as informações do novo cliente.[/cyan]\n" +
        "[white]Apenas o nome é obrigatório para cadastrar um cliente.[/white]",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(instructions)
    
    # Formulário de entrada
    console.print("\n[bold]Informações do Cliente:[/bold]")
    console.print("[red]*[/red] [yellow]Nome do Cliente:[/yellow]")
    nome = Prompt.ask(" ").strip()
    if not nome:
        error_panel = Panel("[red]O nome não pode ficar vazio![/red]", border_style="red")
        console.print(error_panel)
        input("\nPressione Enter para continuar...")
        return
    
    # Registrar o cliente
    client = register_client(nome)
    if not client:
        error_panel = Panel("[red]Erro ao cadastrar cliente![/red]", border_style="red")
        console.print(error_panel)
        input("\nPressione Enter para continuar...")
        return
    
    # Extrair apenas o ID do cliente do objeto retornado
    client_id = client['id_cliente']
    
    # Mensagem de sucesso
    success_panel = Panel(
        f"[green]Cliente '{nome}' cadastrado com sucesso![/green]\n" + 
        f"[white]ID do cliente: [bold]{client_id}[/bold][/white]",
        border_style="green"
    )
    console.print(success_panel)
    
    # Perguntar sobre endereço
    address_question = Panel("[cyan]Deseja cadastrar um endereço para este cliente?[/cyan]", border_style="blue")
    console.print(address_question)
    
    if Prompt.ask("\n[yellow]Confirma? (S/N)[/yellow]", choices=["S", "N"], default="S").upper() == "S":
        new_address = get_new_address(client_id)
        address_id = register_address(new_address['id_cliente'], new_address['rua'], 
                                  new_address['bairro'], new_address['referencia'])
        if address_id:
            success_addr = Panel("[green]Endereço cadastrado com sucesso![/green]", border_style="green")
            console.print(success_addr)
        else:
            error_addr = Panel("[red]Erro ao cadastrar endereço![/red]", border_style="red")
            console.print(error_addr)
    
    input("\nPressione Enter para continuar...")

def listar_clientes():
    """Lista todos os clientes cadastrados"""
    while True:
        console.clear()
        title = "[bold yellow]=== Clientes Cadastrados ===[/bold yellow]"
        console.print(title)
        
        clients = get_all_clients()
        
        if not clients:
            empty_panel = Panel("[yellow]Não há clientes cadastrados.[/yellow]", border_style="yellow")
            console.print(empty_panel)
            input("\nPressione Enter para continuar...")
            return
        
        # Tabela de clientes com bordas e estilos aprimorados
        table = Table(show_header=True, header_style="bold magenta", box=None, border_style="blue")
        table.add_column("ID", justify="center", style="cyan")
        table.add_column("Nome", style="green")
        
        for client in clients:
            table.add_row(
                str(client['id_cliente']),
                client['nm_usuario']
            )
        
        # Envolvendo a tabela em um painel para melhor aparência
        clients_panel = Panel(table, border_style="blue", padding=(1, 2))
        console.print(clients_panel)
        
        # Opções em um painel separado
        options_text = """
[cyan]Opções disponíveis:[/cyan]

[green]1.[/green] Selecionar cliente por ID
[green]0.[/green] Voltar
        """
        options_panel = Panel(options_text, border_style="yellow")
        console.print(options_panel)
        
        opcao = Prompt.ask("\n[yellow]Escolha uma opção[/yellow]", choices=["1", "0"], default="0")
        
        if opcao == "1":
            client_id = Prompt.ask("Digite o ID do cliente")
            if not client_id.isdigit():
                console.print("[red]ID inválido![/red]")
                input("\nPressione Enter para continuar...")
                continue
                
            # Verificar se o cliente existe
            if not any(str(client['id_cliente']) == client_id for client in clients):
                console.print("[red]Cliente não encontrado![/red]")
                input("\nPressione Enter para continuar...")
                continue
                
            editar_cliente(client_id)
            
        elif opcao == "0":
            return
        
        else:
            console.print("[red]Opção inválida![/red]")
            input("\nPressione Enter para continuar...")

def gerenciar_clientes():
    """Menu principal de gerenciamento de clientes"""
    while True:
        console.clear()
        title = "[bold yellow]=== Gerenciamento de Clientes ===[/bold yellow]"
        
        # Cria um painel com as opções de gerenciamento de clientes
        options_text = """
[cyan]Opções disponíveis:[/cyan]

[green]1.[/green] Cadastrar novo cliente
[green]2.[/green] Listar todos os clientes
[green]3.[/green] Buscar cliente por ID
[green]0.[/green] Voltar ao menu principal
        """
        panel = Panel(options_text, title=title, border_style="yellow")
        console.print(panel)
        
        opcao = Prompt.ask("\n[yellow]Escolha uma opção[/yellow]", choices=["1", "2", "3", "0"], default="0")
        
        if opcao == "1":
            novo_cliente()
        elif opcao == "2":
            listar_clientes()
        elif opcao == "3":
            # Buscar cliente por ID
            client_id = Prompt.ask("\n[yellow]Digite o ID do cliente[/yellow]")
            if not client_id.isdigit():
                console.print("[red]ID inválido! O ID deve ser um número.[/red]")
                input("\nPressione Enter para continuar...")
                continue
                
            client = get_client(client_id)
            if not client:
                console.print("[red]Cliente não encontrado![/red]")
                input("\nPressione Enter para continuar...")
                continue
                
            editar_cliente(client_id)
        elif opcao == "0":
            break

if __name__ == "__main__":
    gerenciar_clientes()
