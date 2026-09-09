select
    venta_id,
    fecha_venta,
    cliente_id,
    producto_id,
    sucursal_id,
    canal,
    cantidad,
    precio_unitario,
    descuento_unitario,
    costo_unitario,
    monto_bruto,
    descuento_total,
    monto_neto,
    margen_estimado
from {{ ref('int_ventas_enriquecidas') }}

