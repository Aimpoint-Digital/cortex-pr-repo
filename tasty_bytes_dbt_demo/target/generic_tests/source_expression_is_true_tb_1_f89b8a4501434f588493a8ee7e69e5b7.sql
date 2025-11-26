{% set dbt_custom_arg_expression %}
{{ column_name }} <= current_timestamp()
{% endset %}

{{ dbt_utils.test_expression_is_true(column_name="ORDER_TS", expression=dbt_custom_arg_expression, model=get_where_subquery(source('tb_101', 'ORDER_HEADER'))) }}