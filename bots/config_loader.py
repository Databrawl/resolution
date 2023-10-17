import yaml
import json
import os

# Config load
with open('config.yml', 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)

## Language settings ##
valid_language_codes = []
lang_directory = "lang"


# Instructions loader
def load_instructions(instruction):
    for file_name in os.listdir("instructions"):
        if file_name.endswith('.txt'):
            file_path = os.path.join("instructions", file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            # Use the file name without extension as the variable name
                variable_name = file_name.split('.')[0]
                instruction[variable_name] = file_content