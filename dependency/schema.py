from google.cloud import bigquery
from google.cloud.bigquery_v2 import StandardSqlDataType

# dataset
SCHEMA_AD_ACCOUNT_RAW_TEXTS = [
    bigquery.SchemaField("date", StandardSqlDataType.TypeKind.DATETIME.name),
    bigquery.SchemaField("title", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("link", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("category", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("content", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField('log_datetime', StandardSqlDataType.TypeKind.DATETIME.name)
]

SCHEMA_DCARD_ACCOUNT_RAW_TEXTS = [
    bigquery.SchemaField("date", StandardSqlDataType.TypeKind.DATETIME.name),
    bigquery.SchemaField("title", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("link", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("category", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("content", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("like_count", StandardSqlDataType.TypeKind.INT64.name),
    bigquery.SchemaField('log_datetime', StandardSqlDataType.TypeKind.DATETIME.name),

]

SCHEMA_PTT_ACCOUNT_RAW_TEXTS = [
    bigquery.SchemaField("date", StandardSqlDataType.TypeKind.DATETIME.name),
    bigquery.SchemaField("title", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("link", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("category", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("content", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("like_count", StandardSqlDataType.TypeKind.INT64.name),
    bigquery.SchemaField("comment_count", StandardSqlDataType.TypeKind.INT64.name),
    bigquery.SchemaField('log_dateme', StandardSqlDataType.TypeKind.DATETIME.name),
]

SCHEMA_FACEBOOK_ACCOUNT_RAW_TEXTS = [
    bigquery.SchemaField("post_date", StandardSqlDataType.TypeKind.DATETIME.name),
    bigquery.SchemaField("post_name", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("comment_count", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("content", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("like_count", StandardSqlDataType.TypeKind.STRING.name),
    bigquery.SchemaField("comment_reaction", StandardSqlDataType.TypeKind.JSON.name, ),
    # fields=[
    #     bigquery.SchemaField("comment_name", StandardSqlDataType.TypeKind.STRING.name),
    #     bigquery.SchemaField("comment_date", StandardSqlDataType.TypeKind.STRING.name),
    #     bigquery.SchemaField("comment_text", StandardSqlDataType.TypeKind.STRING.name),
    #
    # ]),
    bigquery.SchemaField('log_datetime', StandardSqlDataType.TypeKind.DATETIME.name),

]

# other
BQ_LOG_DATETIME_FIELD = bigquery.SchemaField('log_datetime', StandardSqlDataType.TypeKind.DATETIME.name)
