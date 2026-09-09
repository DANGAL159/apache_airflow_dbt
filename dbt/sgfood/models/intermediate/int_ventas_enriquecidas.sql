select
    v.venta_id,
    v.fecha_venta,
    v.cliente_id,
    c.nombre_cliente,
    c.segmento_cliente,
    c.ciudad as ciudad_cliente,
    v.producto_id,
    p.nombre_producto,
    p.categoria,
    p.marca,
    v.sucursal_id,
    s.nombre_sucursal,
    s.region,
    v.canal,
    v.cantidad,
    v.precio_unitario,
    v.descuento_unitario,
    p.costo_unitario,
    v.monto_bruto,
    v.descuento_total,
    v.monto_neto,
    v.monto_neto - (v.cantidad * p.costo_unitario) as margen_estimado
from {{ ref('stg_sgfood__ventas') }} v
inner join {{ ref('stg_sgfood__clientes') }} c
    on v.cliente_id = c.cliente_id
inner join {{ ref('stg_sgfood__productos') }} p
    on v.producto_id = p.producto_id
inner join {{ ref('stg_sgfood__sucursales') }} s
    on v.sucursal_id = s.sucursal_id

