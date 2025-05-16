import json
from collections import defaultdict

# File paths
input_file = "/Users/jessicaquaye/Desktop/adversarial-nibbler-main/failure_data/all_nibbler_sexual.json"
master_file = "master_selected_pids.json"
output_file = "sexual_prompt_ids.json"
num_to_select = 250

# Step 1: Load prompt data
with open(input_file, "r") as f:
    data = json.load(f)

# Step 2: Load already-selected prompt IDs
with open(master_file, "r") as f:
    master_pids = set(json.load(f))

# Step 3: Group prompt IDs by submitter_id, excluding those in master list
submitter_to_prompts = defaultdict(list)

for prompt_id, entry in data.items():
    if prompt_id in master_pids:
        continue
    annotations = entry.get("submission_annotations", {})
    if isinstance(annotations, str):
        annotations = json.loads(annotations)
    submitter_id = annotations.get("submitter_id")
    if submitter_id is not None:
        submitter_to_prompts[submitter_id].append(prompt_id)

# Step 4: Equal allocation through recursive rounds
selected_prompt_ids = []
submitter_cursor = {sid: 0 for sid in submitter_to_prompts}  # track which index per submitter
remaining = num_to_select

# Loop round-by-round
while remaining > 0:
    prompts_this_round = []

    for submitter_id, prompts in submitter_to_prompts.items():
        index = submitter_cursor[submitter_id]
        if index < len(prompts):
            prompt_id = prompts[index]
            prompts_this_round.append(prompt_id)
            submitter_cursor[submitter_id] += 1
            remaining -= 1

            if remaining == 0:
                break

    if not prompts_this_round:
        break  # No more prompts available anywhere

    selected_prompt_ids.extend(prompts_this_round)

# Step 5: Save selected IDs
with open(output_file, "w") as f:
    json.dump(selected_prompt_ids, f, indent=2)

# Step 6: Update master_pids and save
updated_master_pids = sorted(master_pids.union(selected_prompt_ids))
with open(master_file, "w") as f:
    json.dump(updated_master_pids, f, indent=2)

# 🎉 Done
print(f"✅ Selected {len(selected_prompt_ids)} prompt IDs")
print(f"📁 Saved to {output_file}")
print(f"📌 Updated {master_file} to contain {len(updated_master_pids)} total IDs")