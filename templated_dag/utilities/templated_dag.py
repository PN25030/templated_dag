import os
import yaml
from jinja2 import Environment, FileSystemLoader
from airflow.models import Variable
from datetime import datetime
from google.cloud import storage

class TemplatedDAGUtility:
    def __init__(self):
        # Fetch Airflow global variables
        self.composer_bucket_location = Variable.get("composer_bucket_location")
        self.templated_dag_location = Variable.get("templated_dag_location")
        
        # Define paths
        self.config_folder = os.path.join(self.templated_dag_location, "configs")
        self.template_folder = os.path.join(self.templated_dag_location, "templates")
        self.rendered_folder = os.path.join(self.composer_bucket_location, "rendered_templates")
        self.client = storage.Client() 
        # Ensure necessary folders exist
        self.validate_folder_structure()

    def validate_folder_structure_1(self):
        """Validates if the necessary folder structure exists."""
        if not os.path.exists(self.config_folder):
            raise FileNotFoundError(f"Config folder does not exist: {self.config_folder}")
        
        if not os.path.exists(self.template_folder):
            raise FileNotFoundError(f"Template folder does not exist: {self.template_folder}")

    def load_config_files(self):
        """Loads all YAML config files from the config folder."""
        config_files = [f for f in os.listdir(self.config_folder) if f.endswith('.yaml') or f.endswith('.yml')]
        configs = {}
        for config_file in config_files:
            config_path = os.path.join(self.config_folder, config_file)
            with open(config_path, 'r') as file:
                configs[config_file] = yaml.safe_load(file)
        return configs
    
    def validate_folder_structure(self):
        # Define required folders
        required_folders = [
            os.path.join(self.templated_dag_location, 'configs'),
            os.path.join(self.templated_dag_location, 'templates')
        ]
        
        # Check each required folder
        for folder in required_folders:
            if not self.check_folder_exists(folder):
                raise Exception(f"Required folder does not exist: {folder}")

        # Check for .yaml files in configs folder
        configs_folder = os.path.join(self.templated_dag_location, 'configs')
        if not self.check_files_exist(configs_folder, '.yaml'):
            raise Exception(f"No YAML files found in: {configs_folder}")

        # Check for .jinja files in templates folder
        templates_folder = os.path.join(self.templated_dag_location, 'templates')
        if not self.check_files_exist(templates_folder, '.jinja'):
            raise Exception(f"No Jinja files found in: {templates_folder}")

    def check_folder_exists(self, folder_path):
        """Check if the specified folder exists in the GCS bucket."""
        bucket_name, folder_prefix = self.parse_gcs_path(folder_path)
        blobs = self.client.list_blobs(bucket_name, prefix=folder_prefix, delimiter='/')
        return any(blob.name.endswith('/') for blob in blobs.prefixes)

    def check_files_exist(self, folder_path, file_extension):
        """Check if there are any files with the specified extension in the folder."""
        bucket_name, folder_prefix = self.parse_gcs_path(folder_path)
        blobs = self.client.list_blobs(bucket_name, prefix=folder_prefix)
        return any(blob.name.endswith(file_extension) for blob in blobs)

    def parse_gcs_path(self, gcs_path):
        """Parse the GCS path into bucket name and prefix."""
        if not gcs_path.startswith('gs://'):
            raise ValueError(f"Invalid GCS path: {gcs_path}")
        path_parts = gcs_path[5:].split('/', 1)
        bucket_name = path_parts[0]
        folder_prefix = path_parts[1] if len(path_parts) > 1 else ''
        return bucket_name, folder_prefix

    def render_templates(self):
        """Reads config files and renders templates based on the template_name key."""
        # Load all configs
        configs = self.load_config_files()
        
        # Set up Jinja2 environment to load templates from the templates folder
        env = Environment(loader=FileSystemLoader(self.template_folder))

        # Iterate over configs and render each corresponding template
        for config_name, config_content in configs.items():
            template_name = config_content.get("template_name")
            if not template_name:
                raise KeyError(f"'template_name' key not found in {config_name}")
            
            template_file = f"{template_name}.jinja"
            template = env.get_template(template_file)
            
            # Render the template using values from the YAML file
            rendered_output = template.render(config_content)

            # Save the rendered template to the specified location with a timestamp
            timestamp = datetime.now().strftime("%d_%m_%y_%H_%M")
            rendered_file_name = f"{template_name}_{timestamp}.txt"
            rendered_file_path = os.path.join(self.rendered_folder, rendered_file_name)
            
            os.makedirs(self.rendered_folder, exist_ok=True)
            with open(rendered_file_path, 'w') as rendered_file:
                rendered_file.write(rendered_output)

            print(f"Rendered template saved: {rendered_file_path}")

if __name__ == "__main__":
    # Create an instance of TemplatedDAGUtility and execute the rendering process
    templated_dag_utility = TemplatedDAGUtility()
    templated_dag_utility.render_templates()
