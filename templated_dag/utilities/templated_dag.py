import os
import yaml
from jinja2 import Environment, FileSystemLoader
from airflow.models import Variable
from datetime import datetime

class TemplatedDAGUtility:
    def __init__(self):
        # Fetch Airflow global variables
        self.composer_bucket_location = Variable.get("composer_bucket_location")
        self.templated_dag_location = Variable.get("templated_dag_location")
        
        # Define paths
        self.config_folder = os.path.join(self.templated_dag_location, "configs")
        self.template_folder = os.path.join(self.templated_dag_location, "templates")
        self.rendered_folder = os.path.join(self.composer_bucket_location, "rendered_templates")

        # Ensure necessary folders exist
        self.validate_folder_structure()

    def validate_folder_structure(self):
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
