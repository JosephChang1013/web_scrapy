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
    bigquery.SchemaField("comment_num", StandardSqlDataType.TypeKind.INT64.name),
    bigquery.SchemaField('log_datetime', StandardSqlDataType.TypeKind.DATETIME.name),
    bigquery.SchemaField(
        "reactions", StandardSqlDataType.TypeKind.JSON.name,
        "RECORD",
        mode="REPEATED",
        fields=[
            bigquery.SchemaField("comment", StandardSqlDataType.TypeKind.STRING.name),
            bigquery.SchemaField("comment_like", StandardSqlDataType.TypeKind.INT64.name)
        ]

    )
]
# other
BQ_LOG_DATETIME_FIELD = bigquery.SchemaField('log_datetime', StandardSqlDataType.TypeKind.DATETIME.name)
BQ_NEWS_TITLE_FIELD = bigquery.SchemaField("title", StandardSqlDataType.TypeKind.STRING.name)
BQ_NEWS_DATETIME_FIELD = bigquery.SchemaField("date", StandardSqlDataType.TypeKind.DATETIME.name)
BQ_NEWS_LINK_FIELD = bigquery.SchemaField("link", StandardSqlDataType.TypeKind.STRING.name)
BQ_NEWS_CONTENT_FIELD = bigquery.SchemaField('log_datetime', StandardSqlDataType.TypeKind.DATETIME.name)
BQ_NEWS_CATEGORY_FIELD = bigquery.SchemaField("category", StandardSqlDataType.TypeKind.STRING.name)
