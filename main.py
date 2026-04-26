import os
import sys
import argparse

from modules.general import load_yaml_config, set_env_from_config

# Argument parser setup
parser = argparse.ArgumentParser(
    prog='Path Leakage',
    description='The program tracks the user based on localization and mobility. '
                'This is performed through grouping, tracking and validation through reconstruction',
)
parser.add_argument('-c', '--config', required=True, type=str, help='Path to the YAML configuration file')
parser.add_argument('-t', '--task_name', type=str, help='Task name', required=False)

args = parser.parse_args()
task_name = args.task_name

if not args.config:
    print("Error: YAML configuration file path is required.")
    sys.exit(1)

config = load_yaml_config(f"configs/{args.config}")
# parsed_data = yaml.safe_load(args.config)
os.environ["SCENARIO_NAME"] = str(args.config)[:-4]

# Set environment variables from each section
for section in config:
    set_env_from_config(section, config)

from pipeline import tasks

# print(task_name)
if task_name:
    if task_name in tasks:
        tasks[task_name]()
    else:
        print(f"Error: Task '{task_name}' not found. Available tasks are:")
        for task in tasks.keys():
            print(f" - {task}")
else:
    print("No task specified. Available tasks are:")
    for task in tasks.keys():
        print(f" - {task}")
