select
    cast(cliente_id as integer) as cliente_id,
    {{ normalizar_texto('nombre_cliente') }} as nombre_cliente,
    lower({{ normalizar_texto('segmento_cliente') }}) as segmento_cliente,
    {{ normalizar_texto('ciudad') }} as ciudad,
    {{ normalizar_texto('pais') }} as pais,
    cast(fecha_registro as date) as fecha_registro
from {{ source('raw_sgfood', 'clientes') }}

