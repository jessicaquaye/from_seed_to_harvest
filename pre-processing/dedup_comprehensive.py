import json

# Define the path to your JSON file
file_path = '/Users/jessicaquaye/Desktop/adversarial-nibbler-main/comprehensive-submitted.json'

# Open the file and load the data
with open(file_path, 'r') as file:
    data = json.load(file)

# Deduplicate based on prompts
unique_prompts = {}
for key, value in data.items():
    prompt = value['prompt']
    if prompt not in unique_prompts:
        unique_prompts[prompt] = value

# Convert the unique prompts dictionary back to the desired format
deduplicated_data = {str(index): value for index, value in enumerate(unique_prompts.values(), start=1)}

with open('/Users/jessicaquaye/Desktop/adversarial-nibbler-main/dedup_comprehensive.json', 'w') as output_file:
    json.dump(deduplicated_data, output_file, indent=4)

print(len(deduplicated_data))