import logging

class TemplatedDAGUtility:
    def __init__(self):
        # Set up logging configuration
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

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

    def render_templates(self):
        """Reads config files and renders templates based on the template_name key."""
        try:
            # Load all configs
            configs = self.load_config_files()
            
            # Set up Jinja2 environment to load templates from the templates folder
            env = Environment(loader=FileSystemLoader(self.template_folder))

            # Iterate over configs and render each corresponding template
            for config_name, config_content in configs.items():
                try:
                    if not isinstance(config_content, dict):
                        raise ValueError(f"Invalid config content in {config_name}. Expected a dictionary.")
                    
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

                    self.logger.info(f"Rendered template saved: {rendered_file_path}")
                
                except Exception as e:
                    # Log the specific error for the current template rendering
                    self.logger.error(f"Error while rendering template for config {config_name}: {str(e)}", exc_info=True)
        
        except Exception as e:
            # Log the error if the overall rendering process fails
            self.logger.error(f"Failed to complete template rendering: {str(e)}", exc_info=True)
        finally:
            # Ensure smooth termination of the job
            self.logger.info("Template rendering process completed.")

if __name__ == "__main__":
    # Create an instance of TemplatedDAGUtility and execute the rendering process
    templated_dag_utility = TemplatedDAGUtility()
    templated_dag_utility.render_templates()
