select
    cast(producto_id as integer) as producto_id,
    {{ normalizar_texto('nombre_producto') }} as nombre_producto,
    lower({{ normalizar_texto('categoria') }}) as categoria,
    {{ normalizar_texto('marca') }} as marca,
    cast(costo_unitario as numeric(12, 2)) as costo_unitario,
    cast(precio_lista as numeric(12, 2)) as precio_lista,
    cast(precio_lista as numeric(12, 2)) - cast(costo_unitario as numeric(12, 2)) as margen_lista
from {{ source('raw_sgfood', 'productos') }}

