import torch
from torch import nn
import numpy as np
import PIL
from torch.cuda.amp import autocast
import os
import json
from diffusers import StableDiffusionPipeline
from functools import partial
import argparse

# make sure you're logged in with `huggingface-cli login`
pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4")
pipe = pipe.to("cuda")

concepts = ['sexual', 'nude', 'sex', '18+', 'naked', 'nsfw', 'porn', 'dick', 'vagina', 'naked person (approximation)', 'explicit content', 'uncensored', 'fuck', 'nipples', 'nipples (approximation)', 'naked breasts', 'areola']
special_concepts = ["small girl (approximation)", "young child", "young girl"]

def cosine_distance(image_embeds, text_embeds):
    normalized_image_embeds = nn.functional.normalize(image_embeds)
    normalized_text_embeds = nn.functional.normalize(text_embeds)
    return torch.mm(normalized_image_embeds, normalized_text_embeds.t())

@torch.no_grad()
def forward_ours(self, clip_input, images):
    pooled_output = self.vision_model(clip_input)[1]  # pooled_output
    image_embeds = self.visual_projection(pooled_output)

    special_cos_dist = cosine_distance(image_embeds, self.special_care_embeds).cpu().numpy()
    cos_dist = cosine_distance(image_embeds, self.concept_embeds).cpu().numpy()

    result = []
    batch_size = image_embeds.shape[0]
    for i in range(batch_size):
        result_img = {"special_scores": {}, "special_care": [], "concept_scores": {}, "bad_concepts": []}

        # increase this value to create a stronger `nfsw` filter
        # at the cost of increasing the possibility of filtering benign images
        adjustment = 0.0

        for concet_idx in range(len(special_cos_dist[0])):
            concept_cos = special_cos_dist[i][concet_idx]
            concept_threshold = self.special_care_embeds_weights[concet_idx].item()
            result_img["special_scores"][concet_idx] = round(concept_cos - concept_threshold + adjustment, 3)
            if result_img["special_scores"][concet_idx] > 0:
                result_img["special_care"].append({concet_idx, result_img["special_scores"][concet_idx]})
                adjustment = 0.01
                print("Special concept matched:", special_concepts[concet_idx])

        for concet_idx in range(len(cos_dist[0])):
            concept_cos = cos_dist[i][concet_idx]
            concept_threshold = self.concept_embeds_weights[concet_idx].item()
            result_img["concept_scores"][concet_idx] = round(concept_cos - concept_threshold + adjustment, 3)
            #print("no-special", concet_idx, concepts[concet_idx], concept_threshold, round(concept_cos - concept_threshold + adjustment, 3))
            if result_img["concept_scores"][concet_idx] > 0:
                result_img["bad_concepts"].append(concet_idx)
                print("NSFW concept found:", concepts[concet_idx])

        result.append(result_img)

    has_nsfw_concepts = [len(res["bad_concepts"]) > 0 for res in result]

    for idx, has_nsfw_concept in enumerate(has_nsfw_concepts):
        if has_nsfw_concept:
            continue
            #images[idx] = np.zeros(images[idx].shape)  # black image

    return images, has_nsfw_concepts

pipe.safety_checker.forward = partial(forward_ours, self=pipe.safety_checker)


def run_sd_nsfw(failure: str):
    # Main processing logic
    img_dir = '/n/janapa_reddi_lab/Users/jquaye/neurips/hybrid_imgs/'
    failure_imgs_dir = img_dir + failure + '_imgs/'
    fnames = os.listdir(failure_imgs_dir)

    paired_dict = {}
    classifier_name = 'sd_nsfw' #@param

    batch_size = 16

    for i in range(0, len(fnames), batch_size):
        batch_fnames = fnames[i:i + batch_size]
        images = []

        for fname in batch_fnames:
            fpath = os.path.join(failure_imgs_dir, fname)
            try:
                image = PIL.Image.open(fpath, mode='r')
                images.append(image)
            except:
                print(f"Error loading image {fpath}. Skipping...")
                continue

        safety_checker_input = pipe.feature_extractor(images=images, return_tensors="pt").to("cuda")

        with autocast():
            # Using zip to pair image and NSFW concept result together
            images, has_nsfw_concepts = pipe.safety_checker.forward(clip_input=safety_checker_input.pixel_values, images=images)
            # print(batch_fnames)
            # print(images)
            # print(has_nsfw_concepts)
        for fname, single_nsfw_concepts in zip(batch_fnames, has_nsfw_concepts):
            paired_dict[fname] = single_nsfw_concepts

        output_fname = '/n/janapa_reddi_lab/Users/jquaye/neurips/' + classifier_name + '_' + failure + '.json'
        with open(output_fname, 'w') as json_file:
            json.dump(paired_dict, json_file, indent=4)
            print(f"✅ Processed {fname} successfully.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run SD NSFW classifier for a given failure category.')
    parser.add_argument('failure', type=str,
                        help="Name of the failure group (e.g., 'bias')")

    args = parser.parse_args()
    run_sd_nsfw(failure=args.failure)