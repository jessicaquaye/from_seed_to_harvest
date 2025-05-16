import json
from collections import defaultdict

# Config
dir = '/Users/jessicaquaye/Desktop/adversarial-nibbler-main/'
fname = "all_nibbler_hate"
input_file = dir + "failure_data/" + fname + ".json"
output_file = dir + fname + "_selected_pids.json"
num_to_select = 250

# Step 1: Load JSON data
with open(input_file, "r") as f:
    data = json.load(f)

# Step 2: Group prompt IDs by submitter_id
submitter_to_prompt_ids = defaultdict(list)
for prompt_id, entry in data.items():
    annotations = entry.get("submission_annotations", {})
    if isinstance(annotations, str):
        annotations = json.loads(annotations)

    submitter_id = annotations.get("submitter_id")
    if submitter_id is not None:
        submitter_to_prompt_ids[submitter_id].append(prompt_id)

# Step 3: Perform recursive equal-round selection
selected_prompt_ids = []
submitter_cursors = {sid: 0 for sid in submitter_to_prompt_ids}  # Track progress per submitter

while len(selected_prompt_ids) < num_to_select:
    added_this_round = 0
    for submitter_id, prompt_list in submitter_to_prompt_ids.items():
        cursor = submitter_cursors[submitter_id]
        if cursor < len(prompt_list):
            selected_prompt_ids.append(prompt_list[cursor])
            submitter_cursors[submitter_id] += 1
            added_this_round += 1

            if len(selected_prompt_ids) == num_to_select:
                break
    if added_this_round == 0:
        break  # No more prompts to add from any submitter

# Step 4: Save selected prompt IDs to output file
with open(output_file, "w") as outf:
    json.dump(selected_prompt_ids, outf, indent=2)

print(f"✅ Saved {len(selected_prompt_ids)} prompt IDs to {output_file}")