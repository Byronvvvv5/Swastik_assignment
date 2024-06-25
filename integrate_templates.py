import json
import glob

# Load the new JSON files from push
resources = []
datasets_path = 'datasets/*.json'
linkedservice_path = 'linkedServices/*.json'
pipeline_path = 'pipelines/*.json'
integrationRuntime_path = 'integrationRuntimes/*.json'

linkedservice_json_files = glob.glob(linkedservice_path)
for json_file in linkedservice_json_files:
    with open(json_file) as file:
        new_resource = json.load(file)
        new_resource['type'] = 'linkedServices'
        resources.append(new_resource)

datasets_json_files = glob.glob(datasets_path)
for json_file in datasets_json_files:
    with open(json_file) as file:
        new_resource = json.load(file)
        new_resource['type'] = 'datasets'
        resources.append(new_resource)

integrationRuntime_json_files = glob.glob(integrationRuntime_path)
for json_file in integrationRuntime_json_files:
    with open(json_file) as file:
        new_resource = json.load(file)
        new_resource['type'] = 'integrationRuntimes'
        resources.append(new_resource)
print(f"Stepcheck: {resources}")
pipeline_json_files = glob.glob(pipeline_path)
for json_file in pipeline_json_files:
    with open(json_file) as file:
        new_resource = json.load(file)
        new_resource['type'] = 'pipelines'
        resources.append(new_resource)


with open('ARM-Templates/base.datafactory.json', 'r') as arm_template_file:
    arm_template = json.load(arm_template_file)

# Update ARM template with new resources
for resource in resources:
    arm_template['resources'].append({
        "type": f"Microsoft.DataFactory/factories/{resource['type']}",
        "apiVersion": "2018-06-01",
        "name": f"[concat(parameters('factoryName'), '/', {resource['name']})]",
        "properties": resource['properties']
    })

# Save the modified ARM template
with open('ARM-Templates/azuredeploy.datafactory.json', 'w') as modified_arm_template_file:    
    json.dump(arm_template, modified_arm_template_file, indent=4)

with open('ARM-Templates/azuredeploy.datafactory.json', 'r') as modified_arm_template_file:
    check_template = json.load(modified_arm_template_file)
print(f'Integration of new resources completed successfully!\n{resources}\n{check_template}')