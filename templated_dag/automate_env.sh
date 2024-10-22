#!/bin/bash

# Define the directory containing your JSON key files
KEY_DIR="./keys"

# Get the current active GCP project ID set by gcloud
CURRENT_PROJECT=$(gcloud config get-value project)

if [ -z "$CURRENT_PROJECT" ]; then
    echo "No project is currently set in gcloud. Please set a project using 'gcloud config set project PROJECT_ID'."
    exit 1
fi

echo "Current active GCP project: $CURRENT_PROJECT"

# Initialize a flag to track if the project is found
PROJECT_FOUND=false

# Loop over each key.json file in the directory
for KEY_FILE in "$KEY_DIR"/*.json; do
    # Extract the project ID from the key file using jq (make sure jq is installed)
    PROJECT_ID=$(jq -r '.project_id' < "$KEY_FILE")

    # Check if the project ID from the key file matches the current active project
    if [ "$PROJECT_ID" == "$CURRENT_PROJECT" ]; then
        PROJECT_FOUND=true
        echo "Matching project ID found: $PROJECT_ID"
        echo "Using service account key: $KEY_FILE"

        # Set Google credentials and project ID environment variables for Terraform
        export GOOGLE_APPLICATION_CREDENTIALS="$KEY_FILE"
        export TF_VAR_project_id="$PROJECT_ID"

        # Run Terraform
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

        break
    fi
done

if [ "$PROJECT_FOUND" = false ]; then
    echo "No matching key.json found for the current project ID: $CURRENT_PROJECT"
    exit 1
fi