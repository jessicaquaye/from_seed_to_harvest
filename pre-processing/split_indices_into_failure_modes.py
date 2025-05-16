import json

# Load the first JSON file
with open('/Users/jessicaquaye/Desktop/adversarial-nibbler-main/dedup-comprehensive.json', 'r') as f1:
    json_data = json.load(f1)


def process_json(data):
    sexual_idxs, violent_idxs, bias_idxs, hate_idxs = set(), set(), set(), set()
    sexual_dict, violent_dict, bias_dict, hate_dict = dict(), dict(), dict(), dict()

    for key, item in data.items():
        annotations = json.loads(item["submission_annotations"])

        failure_types = annotations.get("image_failure_type", [])

        if "image_failure_sexual" in failure_types:
            sexual_idxs.add(key)
            sexual_dict[key] = item

        if "image_failure_violent" in failure_types:
            violent_idxs.add(key)
            violent_dict[key] = item

        if "image_failure_bias" in failure_types:
            bias_idxs.add(key)
            bias_dict[key] = item

        if "image_failure_hate" in failure_types:
            hate_idxs.add(key)
            hate_dict[key] = item

    return sexual_idxs, violent_idxs, bias_idxs, hate_idxs, sexual_dict, violent_dict, bias_dict, hate_dict

print("Len of deduplicated prompts: ", len(json_data))

# Process the JSON and get the filtered results
sexual_idxs, violent_idxs, bias_idxs, hate_idxs, sexual_dict, violent_dict, bias_dict, hate_dict = process_json(json_data)

#Write only idxs
with open('all_nibbler_sexual_idxs.json', 'w') as file:
    json.dump(list(sexual_idxs), file)

with open('all_nibbler_violent_idxs.json', 'w') as file:
    json.dump(list(violent_idxs), file)

with open('all_nibbler_bias_idxs.json', 'w') as file:
    json.dump(list(bias_idxs), file)

with open('all_nibbler_hate_idxs.json', 'w') as file:
    json.dump(list(hate_idxs), file)

#Write full dicts
with open('all_nibbler_sexual.json', 'w') as file:
    json.dump(sexual_dict, file)

with open('all_nibbler_violent.json', 'w') as file:
    json.dump(violent_dict, file)

with open('all_nibbler_bias.json', 'w') as file:
    json.dump(bias_dict, file)

with open('all_nibbler_hate.json', 'w') as file:
    json.dump(hate_dict, file)

print("Sexual prompts count:" ,len(sexual_idxs))
print("Violent prompts count:" ,len(violent_idxs))
print("Bias prompts count:" ,len(bias_idxs))
print("Hate prompts count:" ,len(hate_idxs))
