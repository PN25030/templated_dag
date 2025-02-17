To run a **null check** on a specific column using **Dataplex Data Quality Scan**, you need to modify the `create` command by specifying **rules for data quality checks**.

### **1. Create a Data Quality Scan with a Null Check**
Run the following command:

```sh
gcloud dataplex data-scans create my-bq-null-check-scan \
  --location=us-central1 \
  --project=YOUR_PROJECT_ID \
  --data-source=projects/YOUR_PROJECT_ID/datasets/YOUR_DATASET/tables/YOUR_TABLE \
  --type=DATA_QUALITY \
  --display-name="Null Check Scan" \
  --description="Dataplex data quality scan for null check on a column" \
  --rules="rule-id=null-check, column=YOUR_COLUMN_NAME, rule-type=NULL_CHECK" \
  --schedule="every 24 hours"
```

### **2. Run the Scan**
To execute the scan immediately:

```sh
gcloud dataplex data-scans run my-bq-null-check-scan --location=us-central1 --project=YOUR_PROJECT_ID
```

### **3. Check the Scan Results**
To check if null values were found:

```sh
gcloud dataplex data-scans describe my-bq-null-check-scan --location=us-central1 --project=YOUR_PROJECT_ID
```

---

### **Explanation of Updates:**
- Changed `--type=DATA_QUALITY` to specify a **data quality scan**.
- Added `--rules` to define a **null check** on `YOUR_COLUMN_NAME`.
- The rule format:  
  - `rule-id`: A unique identifier for the rule.
  - `column`: The column to check.
  - `rule-type`: `NULL_CHECK` ensures that the column has no null values.

This setup will **validate** the column for null values and report failures in Dataplex.

Would you like to add more checks, like **duplicate values or threshold-based validations**? 🚀
