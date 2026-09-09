select
    fecha_venta,
    categoria,
    canal,
    sum(cantidad) as unidades_vendidas,
    sum(monto_bruto) as venta_bruta,
    sum(descuento_total) as descuento_total,
    sum(monto_neto) as venta_neta,
    sum(margen_estimado) as margen_estimado
from {{ ref('int_ventas_enriquecidas') }}
group by
    fecha_venta,
    categoria,
    canal

