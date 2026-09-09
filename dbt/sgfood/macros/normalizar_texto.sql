{% macro normalizar_texto(columna) -%}
    nullif(trim(cast({{ columna }} as text)), '')
{%- endmacro %}

