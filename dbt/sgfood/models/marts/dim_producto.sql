select
    producto_id,
    nombre_producto,
    categoria,
    marca,
    costo_unitario,
    precio_lista,
    margen_lista
from {{ ref('stg_sgfood__productos') }}

