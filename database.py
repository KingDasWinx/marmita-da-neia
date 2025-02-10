from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# Debug mode
DEBUG = False

# Carrega as credenciais do arquivo .env
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Inicializa o cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_client(client_id):
    try:
        response = supabase.table('tb_cliente').select('*').eq('id_cliente', client_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar cliente: {str(e)}")
        return None

def get_addresses(client_id):
    try:
        response = supabase.table('tb_endereco').select('*').eq('id_cliente', client_id).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao buscar endereços: {str(e)}")
        return []

def register_address(client_id, rua, bairro, referencia=None):
    try:
        data = {
            'id_cliente': client_id,
            'rua': rua,
            'bairro': bairro,
            'referencia': referencia
        }
        response = supabase.table('tb_endereco').insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Erro ao cadastrar endereço: {str(e)}")
        return None

def register_client(nome):
    try:
        data = {
            'nm_usuario': nome
        }
        response = supabase.table('tb_cliente').insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Erro ao cadastrar cliente: {str(e)}")
        return None

def get_products_by_category(categoria):
    try:
        response = supabase.table('tb_produto_preco').select('*').eq('categoria', categoria).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao buscar produtos: {str(e)}")
        return []

def save_order(client_id, address_id, marmitas, bebidas, tipo_feijao, total, forma_pagamento, status_pagamento, horario_entrega, observacoes=None):
    # Formatar marmitas para JSON
    marmitas_json = []
    for i, m in enumerate(marmitas, 1):
        marmita = {
            "id": i,
            "preco": m['produto']['preco'],
            "tamanho": m['produto']['nome'],
            "adicionais": [{"nome": a['nome'], "preco": a['preco']} for a in m['adicionais']]
        }
        marmitas_json.append(marmita)
    
    # Adicionar bebidas e feijão ao JSON
    pedido_json = {
        "marmitas": marmitas_json,
        "bebidas": [{"nome": b['produto']['nome'], "quantidade": b['quantidade'], "preco": b['produto']['preco']} for b in bebidas],
        "tipo_feijao": tipo_feijao
    }
    
    # Gerar número do pedido (exemplo simples)
    import random
    numero_pedido = f"PED{random.randint(10000, 99999)}"
    
    # Data e hora atual
    from datetime import datetime
    dt_registro = datetime.now().isoformat()
    
    query = """
        INSERT INTO tb_pedido (
            id_cliente, id_endereco, numero_pedido, marmitas, preco_total,
            forma_pagamento, status_pagamento, horario_entrega, obs, dt_registro
        ) VALUES (
            :id_cliente, :id_endereco, :numero_pedido, :marmitas, :preco_total,
            :forma_pagamento, :status_pagamento, :horario_entrega, :obs, :dt_registro
        )
    """
    
    import json
    supabase.table('tb_pedido').insert({
        'id_cliente': client_id,
        'id_endereco': address_id,
        'numero_pedido': numero_pedido,
        'marmitas': json.dumps(pedido_json),
        'preco_total': total,
        'forma_pagamento': forma_pagamento,
        'status_pagamento': status_pagamento,
        'horario_entrega': horario_entrega,
        'obs': observacoes,
        'dt_registro': dt_registro
    }).execute()
