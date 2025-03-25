from airflow import DAG
from airflow.providers.google.cloud.operators.dataplex import (
    DataplexCreateLakeOperator,
    DataplexCreateZoneOperator,
    DataplexCreateAssetOperator,
)
from airflow.utils.dates import days_ago
from datetime import timedelta

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    dag_id='dataplex_lake_zone_asset_creation',
    default_args=default_args,
    schedule_interval=None,  # Run manually
    catchup=False,
    tags=['dataplex', 'gcp', 'dq'],
) as dag:

    # Lake Creation
    create_lake = DataplexCreateLakeOperator(
        task_id='create_lake',
        project_id="{{ var.value.gcp_project_id }}",
        location="{{ var.value.gcp_region }}",
        lake_id="{{ var.value.dataplex_lake_id }}",
        body={
            "display_name": "{{ var.value.dataplex_lake_display_name }}",
            "description": "{{ var.value.dataplex_lake_description }}",
            "metastore": {
                "service": "NONE",  # Or your Metastore service
            },
            "labels": {
                "env": "{{ var.value.dataplex_lake_label_env }}",
            },
        },
    )

    # Zone Creation (Raw Zone)
    create_raw_zone = DataplexCreateZoneOperator(
        task_id='create_raw_zone',
        project_id="{{ var.value.gcp_project_id }}",
        location="{{ var.value.gcp_region }}",
        lake_id="{{ var.value.dataplex_lake_id }}",
        zone_id="{{ var.value.dataplex_raw_zone_id }}",
        body={
            "display_name": "{{ var.value.dataplex_raw_zone_display_name }}",
            "description": "{{ var.value.dataplex_raw_zone_description }}",
            "type_": "RAW",
            "resource_spec": {
                "location_type": "SINGLE_REGION",
            },
            "labels": {
                "env": "{{ var.value.dataplex_zone_label_env }}",
            },
        },
    )

    # Zone Creation (Curated Zone)
    create_curated_zone = DataplexCreateZoneOperator(
        task_id='create_curated_zone',
        project_id="{{ var.value.gcp_project_id }}",
        location="{{ var.value.gcp_region }}",
        lake_id="{{ var.value.dataplex_lake_id }}",
        zone_id="{{ var.value.dataplex_curated_zone_id }}",
        body={
            "display_name": "{{ var.value.dataplex_curated_zone_display_name }}",
            "description": "{{ var.value.dataplex_curated_zone_description }}",
            "type_": "CURATED",
            "resource_spec": {
                "location_type": "SINGLE_REGION",
            },
            "labels": {
                "env": "{{ var.value.dataplex_zone_label_env }}",
            },
        },
    )

    # BigQuery Asset Creation
    create_bq_asset = DataplexCreateAssetOperator(
        task_id='create_bq_asset',
        project_id="{{ var.value.gcp_project_id }}",
        location="{{ var.value.gcp_region }}",
        lake_id="{{ var.value.dataplex_lake_id }}",
        zone_id="{{ var.value.dataplex_curated_zone_id }}",
        asset_id="{{ var.value.dataplex_bq_asset_id }}",
        body={
            "display_name": "{{ var.value.dataplex_bq_asset_display_name }}",
            "description": "{{ var.value.dataplex_bq_asset_description }}",
            "resource_spec": {
                "type_": "BIGQUERY_DATASET",
                "name": "{{ var.value.bq_dataset_full_id }}", #project_id.dataset_id
            },
            "discovery_spec": {
                "enabled": True,
            },
            "labels": {
                "env": "{{ var.value.dataplex_asset_label_env }}",
            },
        },
    )

    # Cloud Storage Asset Creation
    create_gcs_asset = DataplexCreateAssetOperator(
        task_id='create_gcs_asset',
        project_id="{{ var.value.gcp_project_id }}",
        location="{{ var.value.gcp_region }}",
        lake_id="{{ var.value.dataplex_lake_id }}",
        zone_id="{{ var.value.dataplex_raw_zone_id }}",
        asset_id="{{ var.value.dataplex_gcs_asset_id }}",
        body={
            "display_name": "{{ var.value.dataplex_gcs_asset_display_name }}",
            "description": "{{ var.value.dataplex_gcs_asset_description }}",
            "resource_spec": {
                "type_": "STORAGE_BUCKET",
                "name": "{{ var.value.gcs_bucket_full_id }}", #gs://bucket_name
            },
            "discovery_spec": {
                "enabled": True,
            },
            "labels": {
                "env": "{{ var.value.dataplex_asset_label_env }}",
            },
        },
    )

    # Define task dependencies
    create_lake >> create_raw_zone
    create_lake >> create_curated_zone
    create_curated_zone >> create_bq_asset
    create_raw_zone >> create_gcs_asset

Airflow Variables Required:
You'll need to set the following Airflow variables (Admin -> Variables in the Airflow UI):
 * gcp_project_id: Your GCP project ID.
 * gcp_region: The GCP region where you want to create Dataplex resources.
 * dataplex_lake_id: The ID for your Dataplex lake.
 * dataplex_lake_display_name: Display name for the lake.
 * dataplex_lake_description: Description for the lake.
 * dataplex_lake_label_env: Label for the lake (e.g., 'dev', 'prod').
 * dataplex_raw_zone_id: ID for the raw zone.
 * dataplex_raw_zone_display_name: Display name for the raw zone.
 * dataplex_raw_zone_description: Description for the raw zone.
 * dataplex_curated_zone_id: ID for the curated zone.
 * dataplex_curated_zone_display_name: Display name for the curated zone.
 * dataplex_curated_zone_description: Description for the curated zone.
 * dataplex_zone_label_env: Label for the zones (e.g., 'dev', 'prod').
 * dataplex_bq_asset_id: ID for the BigQuery asset.
 * dataplex_bq_asset_display_name: Display name for the BigQuery asset.
 * dataplex_bq_asset_description: Description for the BigQuery asset.
 * bq_dataset_full_id: The full BigQuery dataset ID (e.g., your-project.your_dataset).
 * dataplex_gcs_asset_id: ID for the Cloud Storage asset.
 * dataplex_gcs_asset_display_name: Display name for the Cloud Storage asset.
 * dataplex_gcs_asset_description: Description for the Cloud Storage asset.
 * gcs_bucket_full_id: The full Cloud Storage bucket ID (e.g., gs://your-bucket).
 * dataplex_asset_label_env: Label for the assets (e.g., 'dev', 'prod').
Explanation:
 * DAG Definition: The DAG is defined with default arguments and a schedule (set to None for manual runs).
 * Lake Creation: The DataplexCreateLakeOperator creates the Dataplex lake using the provided variables.
 * Zone Creation:
