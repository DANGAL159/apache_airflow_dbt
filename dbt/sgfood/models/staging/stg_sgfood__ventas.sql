select
    cast(venta_id as integer) as venta_id,
    cast(fecha_venta as date) as fecha_venta,
    cast(cliente_id as integer) as cliente_id,
    cast(producto_id as integer) as producto_id,
    cast(sucursal_id as integer) as sucursal_id,
    lower({{ normalizar_texto('canal') }}) as canal,
    cast(cantidad as integer) as cantidad,
    cast(precio_unitario as numeric(12, 2)) as precio_unitario,
    cast(descuento_unitario as numeric(12, 2)) as descuento_unitario,
    cast(cantidad as integer) * cast(precio_unitario as numeric(12, 2)) as monto_bruto,
    cast(cantidad as integer) * cast(descuento_unitario as numeric(12, 2)) as descuento_total,
    cast(cantidad as integer) * (cast(precio_unitario as numeric(12, 2)) - cast(descuento_unitario as numeric(12, 2))) as monto_neto
from {{ source('raw_sgfood', 'ventas') }}

