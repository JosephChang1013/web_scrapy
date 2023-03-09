import logging
import datetime

from typing import List, Dict, Any
from google.cloud import bigquery
from dependency.base_dependency import GCP_PROJECT_ID, DATASET_TA_SYSTEM, TABLE_AD_ACCOUNT_RAW_TEXTS
from dependency.schema import BQ_LOG_DATETIME_FIELD, SCHEMA_AD_ACCOUNT_RAW_TEXTS, SCHEMA_DCARD_ACCOUNT_RAW_TEXTS, \
    SCHEMA_PTT_ACCOUNT_RAW_TEXTS, SCHEMA_FACEBOOK_ACCOUNT_RAW_TEXTS

BIGQUERY_CLIENT = bigquery.Client()


def big_query_execute(query_list: list[str]) -> list[list]:
    results = []

    # Loop through each query in the input list.
    for query in query_list:

        # Submit the query to the BigQuery API and store the resulting job object.
        query_job = BIGQUERY_CLIENT.query(query)
        result = query_job.result()
        results.append(result)

    # Return a list of lists containing the rows of each query result.
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

    # Define the table ID using variables from the global scope.
    table_id = f'{GCP_PROJECT_ID}.{DATASET_TA_SYSTEM}.{TABLE_AD_ACCOUNT_RAW_TEXTS}_*'

    querys = []
    for d in domain:

        # If the domain is "ptt", generate a query that includes ordering by like count.
        if d == 'ptt':
            query = f'''
            
            SELECT           
             *            
            FROM `{table_id}`
            
            WHERE  _TABLE_SUFFIX = '{d}' AND DATE(log_datetime) BETWEEN  '{start_date}' and '{end_date}'
            
            order by like_count desc ;
                     '''
            querys.append(query)
        else:
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

    # Load the data into the table using the BigQuery client and the job configuration.
    job = BIGQUERY_CLIENT.load_table_from_json(rows, table_id, job_config=job_config)
    job.result()

    # Log a message indicating that the data was loaded successfully.
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
    job.result()
    logging.info(f'loaded {len(rows)} rows and {len(SCHEMA_AD_ACCOUNT_RAW_TEXTS)} columns to {table_id}')


def bq_facebook_metrics(log_datetime: datetime, domain: str, rows: List[Dict[str, Any]]):
    table_id = f'{GCP_PROJECT_ID}.{DATASET_TA_SYSTEM}.{TABLE_AD_ACCOUNT_RAW_TEXTS}_{domain}${log_datetime.strftime("%Y%m%d")}'
    job_config = bigquery.LoadJobConfig(
        autodetect=False,
        create_disposition=bigquery.job.CreateDisposition.CREATE_IF_NEEDED,
        ignore_unknown_values=True,
        schema=SCHEMA_FACEBOOK_ACCOUNT_RAW_TEXTS,
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
    job.result()
    logging.info(f'loaded {len(rows)} rows and {len(SCHEMA_AD_ACCOUNT_RAW_TEXTS)} columns to {table_id}')
