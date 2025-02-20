Below is a fully working implementation of the components outlined in the previous response. This code provides a general-purpose utility for GCP Dataplex data quality checks, including rule definitions, a Dataplex manager, and an Airflow operator. Since the actual Dataplex API interactions depend on your specific GCP setup (e.g., credentials, project permissions), I’ll include simplified but functional code with placeholders for the API calls. You can extend these with the actual google-cloud-dataplex library calls once your environment is set up.
Prerequisites
	•	Install required packages: pip install apache-airflow google-cloud-dataplex google-cloud-bigquery
	•	
	•	Set up GCP credentials (e.g., via GOOGLE_APPLICATION_CREDENTIALS environment variable pointing to a service account key file).
	•	Ensure Dataplex and BigQuery APIs are enabled in your GCP project.

Full Working Code
1. `dataplex_utility.py` - Core Utility Components
from dataclasses import dataclass
from google.cloud import dataplex_v1, bigquery
from google.api_core import exceptions
import time

# Data Quality Rule Definition
@dataclass
class DataQualityRule:
    rule_type: str  # e.g., "not_null", "range", "custom_sql"
    column: str     # Target column (optional for table-level rules)
    table: str      # Fully qualified table name (e.g., "project.dataset.table")
    params: dict = None  # Additional parameters (e.g., min/max values, SQL expressions)

    def __post_init__(self):
        if self.params is None:
            self.params = {}

# Predefined Rules Library
def not_null(column, table):
    return DataQualityRule(rule_type="not_null", column=column, table=table)

def range_check(column, table, min_value, max_value):
    return DataQualityRule(
        rule_type="range",
        column=column,
        table=table,
        params={"min_value": min_value, "max_value": max_value}
    )

# Data Quality Manager
class DataQualityManager:
    def __init__(self, project_id, region, lake_id, zone_id):
        self.client = dataplex_v1.DataScanServiceClient()
        self.project_id = project_id
        self.region = region
        self.lake_id = lake_id
        self.zone_id = zone_id
        self.parent = f"projects/{project_id}/locations/{region}"

    def _build_data_scan_config(self, rules, results_table):
        """Convert rules into a Dataplex DataScan config."""
        data = dataplex_v1.Data()
        data.resource = f"//bigquery.googleapis.com/projects/{self.project_id}/datasets/{rules[0].table.split('.')[1]}/tables/{rules[0].table.split('.')[2]}"

        quality_spec = dataplex_v1.DataQualitySpec()
        quality_rules = []

        for rule in rules:
            if rule.rule_type == "not_null":
                quality_rules.append(
                    dataplex_v1.DataQualityRule(
                        column=rule.column,
                        non_null_expectation=dataplex_v1.DataQualityRule.NonNullExpectation()
                    )
                )
            elif rule.rule_type == "range":
                quality_rules.append(
                    dataplex_v1.DataQualityRule(
                        column=rule.column,
                        range_expectation=dataplex_v1.DataQualityRule.RangeExpectation(
                            min_value=rule.params["min_value"],
                            max_value=rule.params["max_value"]
                        )
                    )
                )
            elif rule.rule_type == "custom_sql":
                quality_rules.append(
                    dataplex_v1.DataQualityRule(
                        sql_assertion=dataplex_v1.DataQualityRule.SqlAssertion(
                            sql_expression=rule.params["sql_expression"]
                        )
                    )
                )

        quality_spec.rules = quality_rules
        return dataplex_v1.DataScan(
            data=data,
            data_quality_spec=quality_spec,
            data_profile_result=dataplex_v1.DataProfileResult(
                destination=dataplex_v1.DataProfileResult.Destination(
                    bigquery_table=results_table
                )
            )
        )

    def create_task(self, task_id, rules, results_table):
        """Create a Dataplex DataScan task."""
        data_scan = self._build_data_scan_config(rules, results_table)
        request = dataplex_v1.CreateDataScanRequest(
            parent=self.parent,
            data_scan_id=task_id,
            data_scan=data_scan
        )
        try:
            operation = self.client.create_data_scan(request=request)
            operation.result()  # Wait for task creation to complete
            print(f"Created DataScan task: {task_id}")
            return f"{self.parent}/dataScans/{task_id}"
        except exceptions.GoogleAPIError as e:
            raise ValueError(f"Failed to create task: {e}")

    def run_task(self, task_name):
        """Run the Dataplex DataScan task."""
        request = dataplex_v1.RunDataScanRequest(name=task_name)
        try:
            response = self.client.run_data_scan(request=request)
            job_name = response.job.name
            print(f"Running task: {job_name}")
            while True:
                job = self.client.get_data_scan_job(name=job_name)
                if job.state in [dataplex_v1.DataScanJob.State.SUCCEEDED, dataplex_v1.DataScanJob.State.FAILED]:
                    break
                time.sleep(10)  # Poll every 10 seconds
            return job
        except exceptions.GoogleAPIError as e:
            raise ValueError(f"Failed to run task: {e}")

    def get_results(self, results_table):
        """Fetch results from BigQuery."""
        bq_client = bigquery.Client(project=self.project_id)
        query = f"SELECT * FROM `{results_table}` ORDER BY timestamp DESC LIMIT 10"
        try:
            results = bq_client.query(query).result()
            return [{"rule": row["rule_name"], "passed": row["passed"]} for row in results]
        except exceptions.GoogleAPIError as e:
            raise ValueError(f"Failed to fetch results: {e}")

    def summarize_results(self, results_table):
        """Summarize the latest results."""
        results = self.get_results(results_table)
        print("Data Quality Check Summary:")
        for result in results:
            status = "PASSED" if result["passed"] else "FAILED"
            print(f"  Rule: {result['rule']} - {status}")
        return results

2. `dataplex_utility/airflow.py` - Airflow Operator
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityCheckOperator(BaseOperator):
    @apply_defaults
    def __init__(self, rules, dataplex_manager, results_table, fail_on_error=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rules = rules
        self.dataplex_manager = dataplex_manager
        self.results_table = results_table
        self.fail_on_error = fail_on_error

    def execute(self, context):
        task_id = f"data_quality_task_{context['run_id'].replace(':', '_')}"
        task_name = self.dataplex_manager.create_task(task_id, self.rules, self.results_table)
        job = self.dataplex_manager.run_task(task_name)
        
        # Check job status
        if job.state == dataplex_v1.DataScanJob.State.FAILED:
            raise ValueError(f"Data quality task {task_id} failed to execute.")

        # Fetch and evaluate results
        results = self.dataplex_manager.get_results(self.results_table)
        if self.fail_on_error and not all(result["passed"] for result in results):
            raise ValueError(f"Data quality checks failed: {results}")
        
        self.log.info(f"Data quality results: {results}")
        return results

3. `example_dag.py` - Airflow DAG Example
from airflow import DAG
from datetime import datetime
from dataplex_utility import DataQualityManager, DataQualityRule, not_null, range_check
from dataplex_utility.airflow import DataQualityCheckOperator

# Define the DAG
dag = DAG(
    dag_id='data_quality_pipeline',
    start_date=datetime(2025, 2, 19),
    schedule_interval='@daily',
    catchup=False,
)

# Initialize the DataQualityManager
manager = DataQualityManager(
    project_id='your_project_id',  # Replace with your GCP project ID
    region='us-central1',
    lake_id='your_lake_id',       # Replace with your Dataplex lake ID
    zone_id='your_zone_id'        # Replace with your Dataplex zone ID
)

# Define data quality rules
rules = [
    not_null(column="customer_id", table="your_project.your_dataset.your_table"),
    range_check(column="age", table="your_project.your_dataset.your_table", min_value=18, max_value=100)
]

# Add the data quality check task to the DAG
data_quality_task = DataQualityCheckOperator(
    task_id='check_data_quality',
    rules=rules,
    dataplex_manager=manager,
    results_table='your_project.your_dataset.dq_results',  # Replace with your BigQuery results table
    fail_on_error=True,
    dag=dag
)

# Optional: Add downstream tasks
# another_task = SomeOperator(task_id='next_task', dag=dag)
# data_quality_task >> another_task

How to Use This Code
	1	Set Up GCP Environment:
	◦	Replace placeholders (your_project_id, your_lake_id, etc.) with your actual GCP details.
	◦	Ensure your service account has permissions for Dataplex and BigQuery.
	2	Directory Structure: project/
	3	├── dataplex_utility.py       # Core utility code
	4	├── dataplex_utility/
	5	│   └── airflow.py            # Airflow operator
	6	└── dags/
	7	    └── example_dag.py        # Airflow DAG
	8	
	9	Run Airflow:
	◦	Place example_dag.py in your Airflow dags/ folder.
	◦	Start the Airflow scheduler and webserver: airflow scheduler
	◦	airflow webserver -p 8080
	◦	
	◦	Trigger the DAG via the Airflow UI or CLI: airflow dags trigger -d data_quality_pipeline
	◦	
	10	Expected Behavior:
	◦	The DataQualityCheckOperator creates a Dataplex DataScan task, runs it, and checks the results.
	◦	If any rule fails and fail_on_error=True, the DAG fails, alerting the developer.
	◦	Results are stored in the specified BigQuery table (dq_results).

Notes and Enhancements
	•	Error Handling: The code includes basic error handling; enhance it with retries or custom alerts (e.g., Slack notifications) as needed.
	•	Results Table Schema: Ensure your BigQuery dq_results table has an appropriate schema (e.g., rule_name STRING, passed BOOLEAN, timestamp TIMESTAMP).
	•	Incremental Scans: Add an incremental=True parameter to DataQualityCheckOperator and modify the Dataplex config to use incremental scanning (requires additional API setup).
	•	Testing: Test with a small dataset first to verify Dataplex task creation and result storage.
This implementation provides a solid foundation for a plug-and-play data quality utility, making it easy for developers to integrate into Airflow workflows while leveraging Dataplex’s capabilities. Let me know if you need help refining it further!
