from datetime import datetime
from escpos.printer import Usb
from database import DEBUG
from rich.console import Console
from config import get_print_quantity

console = Console()

def imprimir_pedido(pedido, cliente, quantidade_copias=None):
    # Se não foi especificada uma quantidade, usa a das configurações
    if quantidade_copias is None:
        quantidade_copias = get_print_quantity()
    data_atual = datetime.now().strftime('%d/%m/%Y')

    for i in range(quantidade_copias):
        if not DEBUG:
            try:
                p = Usb(0x04b8, 0x0e27)
                printer = p
            except Exception as e:
                console.print("[red]Erro ao imprimir: USB device not found (Device not found or cable not plugged in.)[/red]")
                return
        else:
            class PrinterDebug:
                def __init__(self):
                    self.align = 'left'
                    self.width = 48
                
                def set(self, **kwargs):
                    self.align = kwargs.get('align', self.align)
                
                def text(self, txt):
                    print(txt, end='')
                
                def cut(self):
                    print("\n" + "="*48 + "\n")
                
                def close(self):
                    pass
            
            printer = PrinterDebug()

        printer.width = 48
        printer.set(align='center')
        printer.text("==============================================\n")
        printer.text("Marmitas da Néia\n")
        printer.text("==============================================\n\n")

        printer.text("Detalhes do Pedido\n")
        printer.text("[-------] -------------------------- [-------]\n\n")
        
        printer.set(align='left', font='a', width=1, height=1)
        printer.text(data_atual)
        printer.text(f"\nPedido Nº: {pedido['numero_pedido']}\n")
        printer.text(f"Cliente: {cliente['nm_usuario']}\n")
        printer.text(f"Horário: {pedido['horario_entrega']}\n\n")

        printer.text("----------------------------------------------\n\n")
        printer.set(align='center', invert=True, height=1)
        printer.text("   MARMITAS   \n\n")

        printer.set(align='left', invert=False)
        marmitas_json = eval(pedido['marmitas'])
        for marmita in marmitas_json['marmitas']:
            printer.text(f"Marmita {marmita['tamanho']}\n")
            for adicional in marmita['adicionais']:
                printer.text(f"* {adicional['nome']} (R$ {adicional['preco']})\n")
        printer.text("\n")
        
        if marmitas_json['bebidas']:
            for bebida in marmitas_json['bebidas']:
                printer.text(f"Bebida: {bebida['nome']} x{bebida['quantidade']} (R$ {bebida['preco']})\n")
            printer.text("\n")
            
        printer.text(f"Feijão: {marmitas_json['tipo_feijao']}\n\n")
        
        if pedido.get('obs'):
            printer.text(f"Obs: {pedido['obs']}\n\n")
        printer.text("----------------------------------------------\n\n")

        printer.text(f"R$ {pedido['preco_total']:.2f}\n")
        printer.text(f"Forma de pagamento: {pedido['forma_pagamento']}\n")
        printer.text(f"Status do pagamento: {pedido['status_pagamento']}\n\n")

        # Get address information
        printer.text(f"Entrega: {pedido['endereco']['rua']}, {pedido['endereco']['bairro']}\n")
        if pedido['endereco'].get('referencia'):
            printer.text(f"Referência: {pedido['endereco']['referencia']}\n")
        printer.text("\n")
        
        printer.set(align='center')
        printer.text("[-------] -------------------------- [-------]\n\n")
        printer.text("Obrigado pela sua preferência!\n")
        printer.text("Volte sempre!\n")
        
        printer.cut()
        printer.close()
