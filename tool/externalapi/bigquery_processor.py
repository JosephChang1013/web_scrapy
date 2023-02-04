import logging
import datetime

from typing import List, Dict, Any
from google.cloud import bigquery
from dependency.base_dependency import GCP_PROJECT_ID, DATASET_TA_SYSTEM, TABLE_AD_ACCOUNT_RAW_TEXTS
from dependency.schema import BQ_LOG_DATETIME_FIELD, SCHEMA_AD_ACCOUNT_RAW_TEXTS, SCHEMA_DCARD_ACCOUNT_RAW_TEXTS, \
    SCHEMA_PTT_ACCOUNT_RAW_TEXTS

BIGQUERY_CLIENT = bigquery.Client()


def big_query_execute(query_list: list[str]) -> list[list]:
    results = []
    for query in query_list:
        query_job = BIGQUERY_CLIENT.query(query)
        result = query_job.result()
        results.append(result)
    return [[row for row in i] for i in results]


def bq_log_metrics(log_datetime: datetime, domain: str, rows: List[Dict[str, Any]]):
    table_id = f'{GCP_PROJECT_ID}.{DATASET_TA_SYSTEM}.{TABLE_AD_ACCOUNT_RAW_TEXTS}_{domain}${log_datetime.strftime("%Y%m%d")}'
    job_config = bigquery.LoadJobConfig(
        autodetect=False,
        create_disposition=bigquery.job.CreateDisposition.CREATE_IF_NEEDED,
        ignore_unknown_values=True,
        schema=SCHEMA_AD_ACCOUNT_RAW_TEXTS,
        schema_update_options=bigquery.job.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        time_partitioning=bigquery.table.TimePartitioning(
            type_=bigquery.table.TimePartitioningType.DAY,
            field=BQ_LOG_DATETIME_FIELD.name,
            require_partition_filter=True,
        ),
        write_disposition=bigquery.job.WriteDisposition.WRITE_TRUNCATE,
    )
    job = BIGQUERY_CLIENT.load_table_from_json(rows, table_id, job_config=job_config)
    job.result()  # Waits for the job to complete.
    logging.info(f'loaded {len(rows)} rows and {len(SCHEMA_AD_ACCOUNT_RAW_TEXTS)} columns to {table_id}')


def query_script(start_date: datetime, end_date: datetime, domain: list[str]) -> list[str]:
    table_id = f'{GCP_PROJECT_ID}.{DATASET_TA_SYSTEM}.{TABLE_AD_ACCOUNT_RAW_TEXTS}_*'
    querys = []
    for d in domain:
        query = f'''
            SELECT 
                *
            FROM `{table_id}`
            WHERE _TABLE_SUFFIX = '{d}' AND DATE(log_datetime) BETWEEN  '{start_date}' and '{end_date}'; 
        '''
        querys.append(query)
    return querys


def bq_dcard_metrics(log_datetime: datetime, domain: str, rows: List[Dict[str, Any]]):
    table_id = f'{GCP_PROJECT_ID}.{DATASET_TA_SYSTEM}.{TABLE_AD_ACCOUNT_RAW_TEXTS}_{domain}${log_datetime.strftime("%Y%m%d")}'
    job_config = bigquery.LoadJobConfig(
        autodetect=False,
        create_disposition=bigquery.job.CreateDisposition.CREATE_IF_NEEDED,
        ignore_unknown_values=True,
        schema=SCHEMA_DCARD_ACCOUNT_RAW_TEXTS,
        schema_update_options=bigquery.job.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        time_partitioning=bigquery.table.TimePartitioning(
            type_=bigquery.table.TimePartitioningType.DAY,
            field=BQ_LOG_DATETIME_FIELD.name,
            require_partition_filter=True,
        ),
        write_disposition=bigquery.job.WriteDisposition.WRITE_TRUNCATE,
    )
    job = BIGQUERY_CLIENT.load_table_from_json(rows, table_id, job_config=job_config)
    job.result()  # Waits for the job to complete.
    logging.info(f'loaded {len(rows)} rows and {len(SCHEMA_AD_ACCOUNT_RAW_TEXTS)} columns to {table_id}')


def bq_ptt_metrics(log_datetime: datetime, domain: str, rows: List[Dict[str, Any]]):
    table_id = f'{GCP_PROJECT_ID}.{DATASET_TA_SYSTEM}.{TABLE_AD_ACCOUNT_RAW_TEXTS}_{domain}${log_datetime.strftime("%Y%m%d")}'
    job_config = bigquery.LoadJobConfig(
        autodetect=False,
        create_disposition=bigquery.job.CreateDisposition.CREATE_IF_NEEDED,
        ignore_unknown_values=True,
        schema=SCHEMA_PTT_ACCOUNT_RAW_TEXTS,
        schema_update_options=bigquery.job.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        time_partitioning=bigquery.table.TimePartitioning(
            type_=bigquery.table.TimePartitioningType.DAY,
            field=BQ_LOG_DATETIME_FIELD.name,
            require_partition_filter=True,
        ),
        write_disposition=bigquery.job.WriteDisposition.WRITE_TRUNCATE,
    )
    job = BIGQUERY_CLIENT.load_table_from_json(rows, table_id, job_config=job_config)
    job.result()  # Waits for the job to complete.
    logging.info(f'loaded {len(rows)} rows and {len(SCHEMA_AD_ACCOUNT_RAW_TEXTS)} columns to {table_id}')
