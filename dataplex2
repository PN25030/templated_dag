You can use the `gcloud dataplex data-scans` command to create and execute a Dataplex data scan for your BigQuery table.

### **1. Create a Data Scan**
Run the following command to create a Dataplex data scan for a BigQuery table:

```sh
gcloud dataplex data-scans create my-bq-scan \
  --location=us-central1 \
  --project=YOUR_PROJECT_ID \
  --data-source=projects/YOUR_PROJECT_ID/datasets/YOUR_DATASET/tables/YOUR_TABLE \
  --type=DATA_PROFILE \
  --display-name="My BigQuery Scan" \
  --description="Dataplex data scan for BigQuery table" \
  --schedule="every 24 hours"  # Adjust as needed
```

#### **Explanation of flags:**
- `--location`: The region where Dataplex is set up.
- `--project`: Your GCP project ID.
- `--data-source`: The full resource path of your BigQuery table.
- `--type`: The type of scan (`DATA_PROFILE` or `DATA_QUALITY`).
- `--schedule`: Optional, defines how frequently the scan runs.

---

### **2. Execute (Run) the Scan**
After creating the scan, you can trigger it manually using:

```sh
gcloud dataplex data-scans run my-bq-scan --location=us-central1 --project=YOUR_PROJECT_ID
```

This will immediately execute the scan instead of waiting for a scheduled run.

---

### **Check Scan Results**
You can check the status of the scan execution using:

```sh
gcloud dataplex data-scans list --location=us-central1 --project=YOUR_PROJECT_ID
```

For details of a specific scan:

```sh
gcloud dataplex data-scans describe my-bq-scan --location=us-central1 --project=YOUR_PROJECT_ID
```

---

Let me know if you need additional configurations or adjustments! 🚀
