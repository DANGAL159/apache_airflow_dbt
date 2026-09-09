select
    cliente_id,
    nombre_cliente,
    segmento_cliente,
    ciudad,
    pais,
    fecha_registro
from {{ ref('stg_sgfood__clientes') }}

