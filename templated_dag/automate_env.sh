#!/bin/bash

# Define the directory containing your JSON key files
KEY_DIR="./keys"

# Loop over each key.json file in the directory
for KEY_FILE in "$KEY_DIR"/*.json; do
    # Extract the project ID from the key file using jq (make sure jq is installed)
    PROJECT_ID=$(jq -r '.project_id' < "$KEY_FILE")

    # Set Google credentials and project ID environment variables for Terraform
    export GOOGLE_APPLICATION_CREDENTIALS="$KEY_FILE"
    export TF_VAR_project_id="$PROJECT_ID"

    echo "Deploying Terraform for project: $PROJECT_ID"

    # Initialize and apply Terraform
    terraform init
    terraform apply -auto-approve

    if [ $? -ne 0 ]; then
        echo "Terraform deployment failed for project: $PROJECT_ID"
    else
        echo "Terraform deployment succeeded for project: $PROJECT_ID"
    fi

    # Optional: Unset credentials for safety
    unset GOOGLE_APPLICATION_CREDENTIALS
    unset TF_VAR_project_id

done
