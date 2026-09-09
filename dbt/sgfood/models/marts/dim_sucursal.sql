select
    sucursal_id,
    nombre_sucursal,
    region,
    ciudad
from {{ ref('stg_sgfood__sucursales') }}

