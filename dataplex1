Key Points
	•	Dataplex uses CloudDQ YAML files for data quality checks, supporting rules, filters, bindings, and more.
	•	Main YAML sections include rules, row filters, rule bindings, dimensions, reference columns, entities, and defaults.
	•	Execution involves creating a Dataplex task with the YAML file, run via CloudDQ, with results in BigQuery.
What Are the YAML Attributes for Dataplex Data Quality Checks?
Introduction to Dataplex and YAML-Based Execution Google Cloud Dataplex is a data management service that unifies and governs distributed data, using CloudDQ for data quality (DQ) checks defined in YAML files. These files allow you to specify rules, filters, and bindings to ensure data quality across BigQuery and Cloud Storage tables. To execute these checks, you create a Dataplex data quality task, upload the YAML file or a zip archive to Cloud Storage, and schedule the task, with results automatically stored in BigQuery.
Supported YAML Attributes Dataplex supports a comprehensive set of YAML attributes through CloudDQ, organized into key sections:
	•	Rules: Define validation logic like NOT_NULL or custom SQL, with attributes like rule_type, dimension, and params.
	•	Row Filters: Filter data subsets using SQL expressions, with filter_id and filter_sql_expr.
	•	Rule Bindings: Link rules and filters to tables, including entity_id, column_id, row_filter_id, and rule_ids.
	•	Rule Dimensions: List allowed categories (e.g., consistency, correctness) for rules.
	•	Reference Columns: Specify columns for failed records queries, aiding troubleshooting.
	•	Entities: Provide metadata for tables, detailing project, dataset, and columns.
	•	Metadata Registry Defaults: Set defaults for entity URIs, especially for Dataplex lakes/zones.
Surprising Detail: Flexible Customization It’s surprising how flexible the YAML setup is, allowing custom SQL rules and incremental validations, making it adaptable for complex data quality needs.

Detailed Survey Note on YAML Attributes and Execution in Dataplex
This section provides an in-depth exploration of the YAML attributes supported by Google Cloud Dataplex for data quality checks, leveraging CloudDQ specifications, and details the execution process. It aims to offer a comprehensive guide for users looking to implement YAML-based data quality checks in Dataplex, ensuring all relevant details from the investigation are included.
Background and Context
Dataplex, part of Google Cloud Platform (GCP), is designed as a data fabric to unify distributed data across data lakes, warehouses, and marts, automating data management and governance. A key feature is its ability to perform data quality (DQ) checks, which are crucial for validating data as part of production pipelines, monitoring dataset quality, and meeting regulatory requirements. These checks are powered by CloudDQ, an open-source data quality engine for BigQuery, with configurations defined in YAML files.
The investigation began by understanding Dataplex through official documentation and web searches, confirming its role in data mesh and governance. It was established that Dataplex uses CloudDQ for DQ tasks, with YAML files as the configuration input, as detailed in the documentation at Use data quality tasks | Dataplex | Google Cloud. Further exploration into CloudDQ’s GitHub repository, particularly the reference guide at CloudDQ reference guide, provided the foundation for identifying supported YAML attributes.
YAML Attributes Supported by Dataplex
Dataplex’s data quality checks rely on CloudDQ’s YAML specification, with the following key sections and attributes identified through the reference guide and sample configurations:
Rules
	•	Description: Defines reusable validation logic for data quality checks, supporting both predefined types (e.g., NOT_NULL, REGEX) and custom SQL expressions (CUSTOM_SQL_EXPR, CUSTOM_SQL_STATEMENT).
	•	Attributes:
	◦	rule_type: Specifies the type of rule (e.g., NOT_NULL, REGEX, CUSTOM_SQL_EXPR).
	◦	dimension: Associates the rule with a category (e.g., correctness, completeness), requiring rule_dimensions to be defined if used.
	◦	params: Includes parameters specific to the rule type, such as pattern for REGEX, custom_sql_expr for CUSTOM_SQL_EXPR, or custom_sql_statement and custom_sql_arguments for CUSTOM_SQL_STATEMENT.
	•	Example: VALUE_ZERO_OR_POSITIVE:
	•	  rule_type: CUSTOM_SQL_EXPR
	•	  dimension: correctness
	•	  params:
	•	    custom_sql_expr: $column >= 0
	•	
	•	Notes: Custom SQL rules must include from data in the statement for CUSTOM_SQL_STATEMENT, and all attributes are case-sensitive.
Row Filters
	•	Description: Defines SQL expressions to filter data subsets before applying rules, inserted into the WHERE clause of the validation query.
	•	Attributes:
	◦	filter_id: Unique identifier for the filter.
	◦	filter_sql_expr: SQL expression returning a boolean value, e.g., contact_type = 'email'.
	•	Example: NONE:
	•	  filter_sql_expr: True
	•	INTERNATIONAL_ITEMS:
	•	  filter_sql_expr: REGEXP_CONTAINS(item_id, 'INTNL')
	•	
	•	Notes: Filters are optional but useful for segmenting data, such as for international vs. domestic items.
Rule Bindings
	•	Description: Associates rules and row filters with specific tables and columns, defining the validation routine.
	•	Attributes:
	◦	binding_id: Unique identifier for the binding.
	◦	entity_id or entity_uri: Identifies the table to validate; entity_uri is required for one of these, e.g., bigquery://projects//datasets//tables/.
	◦	column_id: Specifies the column to apply the rule to.
	◦	row_filter_id: Links to a defined filter, if applicable.
	◦	rule_ids: List of rule identifiers to apply.
	◦	reference_columns_id: Optional, links to reference columns for failed records.
	◦	incremental_time_filter_column_id: Optional, specifies a TIMESTAMP or DATETIME column for incremental validations.
	◦	metadata: Optional, additional metadata for the binding.
	•	Example: TRANSACTION_AMOUNT_VALID:
	•	  entity_uri: bigquery://projects/your-project/datasets/your-dataset/tables/sales_orders
	•	  column_id: amount
	•	  row_filter_id: NONE
	•	  rule_ids:
	•	    - VALUE_ZERO_OR_POSITIVE
	•	
	•	Notes: All tables in a binding must be in the same Google Cloud region, and entity_uri can be shortened using metadata_registry_defaults for Dataplex lakes/zones.
Rule Dimensions
	•	Description: Defines the allowed categories for rules, mandatory if dimension is used in rules.
	•	Attributes: List of dimensions, such as:
	◦	consistency
	◦	correctness
	◦	duplication
	◦	completeness
	◦	conformance
	◦	integrity
	•	Example: rule_dimensions:
	•	  - consistency
	•	  - correctness
	•	  - duplication
	•	  - completeness
	•	  - conformance
	•	  - integrity
	•	
	•	Notes: Ensures consistency in rule categorization, with errors if a dimension is not listed.
Reference Columns
	•	Description: Defines sets of columns for joining failed records queries, used in troubleshooting to provide context for failed validations.
	•	Attributes:
	◦	include_reference_columns: List of column names to include, or “*” for all columns (except for CUSTOM_SQL_STATEMENT, where it has no effect).
	•	Example: reference_columns:
	•	  ORDER_DETAILS_REFERENCE_COLUMNS:
	•	    include_reference_columns:
	•	      - id
	•	      - last_modified_timestamp
	•	      - item_id
	•	
	•	Notes: Useful for debugging, ensuring failed records can be traced back with relevant data.
Entities
	•	Description: Captures static metadata for tables, referenced by entity_id in rule bindings.
	•	Attributes:
	◦	entity_id: Unique identifier for the entity.
	◦	entity_type: Type of entity, e.g., bigquery_table.
	◦	source_database, project_name, dataset_name, table_name: Details for BigQuery tables.
	◦	columns: List of columns with name, data_type, and description.
	•	Example: entities:
	•	  sales_orders:
	•	    entity_type: bigquery_table
	•	    project_name: your-project
	•	    dataset_name: your-dataset
	•	    table_name: sales_orders
	•	    columns:
	•	      - name: order_id
	•	        data_type: STRING
	•	        description: Unique order identifier
	•	      - name: amount
	•	        data_type: FLOAT
	•	        description: Order amount
	•	
	•	Notes: Found in sample configurations like configs/entities/test-data.yml, editable for project and dataset IDs.
Metadata Registry Defaults
	•	Description: Optional section to shorten entity_uri for schemes like Dataplex, defining default values for projects, locations, lakes, and zones.
	•	Attributes:
	◦	projects, locations, lakes, zones: Default values for Dataplex notation.
	•	Example: metadata_registry_defaults:
	•	  dataplex:
	•	    projects: your-project
	•	    locations: your-region
	•	    lakes: your-lake
	•	    zones: your-zone
	•	
	•	Notes: Overrides can be specified in entity_uri, enhancing readability for Dataplex users.
Execution Process in Dataplex
The execution of YAML-based data quality checks in Dataplex involves the following steps, as outlined in the documentation at Use data quality tasks | Dataplex | Google Cloud:
	1	Prepare YAML Files: Create YAML files or a zip archive containing multiple files, adhering to the CloudDQ specification. These can be stored locally or in Cloud Storage.
	2	Create Data Quality Task: In the Dataplex console, navigate to Analytics > Dataplex, under Manage lakes, click Process, then +CREATE TASK, and select Check Data Quality. Specify:
	◦	The input as a Cloud Storage URI pointing to the YAML file or zip archive.
	◦	Execution settings, such as the service account and project for BigQuery jobs.
	◦	Scheduling options, like running immediately or on a schedule.
	3	Execution: Dataplex uses CloudDQ as the driver program, converting YAML checks to SQL and pushing them down to BigQuery for zero-copy execution. It requires enabling the Dataproc API and Private Google Access for the network.
	4	Results: Results are stored in a BigQuery table, accessible for reporting and monitoring, with options for incremental validations using incremental_time_filter_column_id.
The process is serverless, requiring no infrastructure setup, and supports scheduling through Dataplex’s serverless scheduler or external tools like Cloud Composer, as noted in Data quality tasks overview | Dataplex | Google Cloud.
Sample Configurations and Further Resources
To aid in understanding, sample configurations are provided in the CloudDQ repository, such as:
	•	docs/examples/referential_integrity.yaml for referential integrity rules, found at referential integrity sample.
	•	docs/examples/row_by_row.yaml for row-by-row comparisons, at row by row sample.
These samples illustrate the practical application of the attributes, with CLI commands in the user manual at CloudDQ user manual showing how to execute them, e.g., using clouddq run --config configs/entities/test-data.yml.
Surprising Flexibility and Customization
A notable finding is the flexibility of the YAML setup, allowing custom SQL rules and incremental validations, which is particularly surprising given the serverless nature of Dataplex. This adaptability ensures it can handle complex data quality requirements, such as business logic validations and aggregate conditions, as seen in samples like docs/examples/business_logic.yaml at business logic sample.
Conclusion
The YAML attributes supported by GCP Dataplex for data quality checks are comprehensively defined by CloudDQ, covering rules, filters, bindings, dimensions, reference columns, entities, and defaults. The execution process integrates seamlessly with Dataplex tasks, leveraging CloudDQ for serverless, zero-copy execution, with results in BigQuery. Users are encouraged to refer to the provided documentation and sample configurations for hands-on implementation, ensuring robust data quality management.
Key Citations
	•	Use data quality tasks Dataplex Google Cloud
	•	Data quality tasks overview Dataplex Google Cloud
	•	CloudDQ reference guide
	•	CloudDQ user manual
	•	referential integrity sample
	•	row by row sample
	•	business logic sample
