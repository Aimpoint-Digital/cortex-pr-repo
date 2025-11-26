# dbt Core Setup Instructions

Add this entry to profiles.yml and replace the placeholders for `account` & `password`

```yml
dbt_demos_jaffle_shop_snowflake:
  target: dev
  outputs:
    dev:
    account: your-snowflake-account
    database: jaffle_shop
    password: YOUR-PASSWORD-HERE
    role: transformer
    schema: dbt_bbrewington
    threads: 4
    type: snowflake
    user: BRENTBREWINGTON
    warehouse: TRANSFORMING
    prod:
    account: your-snowflake-account
    database: jaffle_shop
    password: YOUR-PASSWORD-HERE
    role: transformer
    schema: prod
    threads: 4
    type: snowflake
    user: BRENTBREWINGTON
    warehouse: TRANSFORMING
```

Test your setup:

```bash
dbt debug --profile dbt_demos_jaffle_shop_snowflake --target dev
dbt debug --profile dbt_demos_jaffle_shop_snowflake --target prod
```
