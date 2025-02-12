from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# Debug mode
DEBUG = True

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

def get_next_order_number():
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Verifica se é um novo dia
        try:
            with open('last_date.txt', 'r') as f:
                last_date = f.read().strip()
            if last_date != today:
                with open('pd.txt', 'w') as f:
                    f.write('2')  # Já escrevemos 2 pois vamos retornar 1
                with open('last_date.txt', 'w') as f:
                    f.write(today)
                return "1"
        except FileNotFoundError:
            with open('last_date.txt', 'w') as f:
                f.write(today)
            with open('pd.txt', 'w') as f:
                f.write('2')
            return "1"
        
        # Continua com a lógica normal de incremento
        with open('pd.txt', 'r') as f:
            num = int(f.read().strip())
        with open('pd.txt', 'w') as f:
            f.write(str(num + 1))
        return str(num)
    except FileNotFoundError:
        with open('pd.txt', 'w') as f:
            f.write('2')
        return "1"

def get_daily_orders():
    try:
        from datetime import datetime, timedelta
        
        # Pega a data atual em UTC-3
        today = datetime.now() - timedelta(hours=3)
        start_of_day = today.strftime('%Y-%m-%d 00:00:00')
        end_of_day = today.strftime('%Y-%m-%d 23:59:59')
        
        query = supabase.table('tb_pedido') \
            .select('numero_pedido, tb_cliente(nm_usuario), forma_pagamento, status_pagamento') \
            .gte('dt_registro', start_of_day) \
            .lte('dt_registro', end_of_day) \
            .execute()
            
        if not query.data:
            return []
            
        orders = [(
            order['numero_pedido'],
            order['tb_cliente']['nm_usuario'],
            order['forma_pagamento'],
            order['status_pagamento']
        ) for order in query.data]
                
        return sorted(orders, key=lambda x: int(x[0]))  # Ordena por número do pedido
    except Exception as e:
        print(f"Erro ao buscar pedidos do dia: {str(e)}")
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
    
    # Gerar número do pedido
    numero_pedido = get_next_order_number()
    
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

def get_order_details(numero_pedido):
    try:
        query = supabase.table('tb_pedido') \
            .select('''
                *,
                tb_cliente(nm_usuario),
                tb_endereco(rua, bairro, referencia)
            ''') \
            .eq('numero_pedido', numero_pedido) \
            .execute()
            
        if query.data:
            return query.data[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar detalhes do pedido: {str(e)}")
        return None

def delete_order(numero_pedido):
    try:
        supabase.table('tb_pedido') \
            .delete() \
            .eq('numero_pedido', numero_pedido) \
            .execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir pedido: {str(e)}")
        return False

def update_order(numero_pedido, marmitas, forma_pagamento, status_pagamento, horario_entrega=None):
    try:
        supabase.table('tb_pedido') \
            .update({
                'marmitas': marmitas,
                'forma_pagamento': forma_pagamento,
                'status_pagamento': status_pagamento,
                'horario_entrega': horario_entrega
            }) \
            .eq('numero_pedido', numero_pedido) \
            .execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar pedido: {str(e)}")
        return False
