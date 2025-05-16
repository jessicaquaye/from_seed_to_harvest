import torch
from diffusers import DiffusionPipeline, StableDiffusionPipeline, AutoPipelineForText2Image
from diffusers.models import AutoencoderKL
import json
import argparse
import os

def generate_imgs(input_fname, model_id, output_dir):
    # Load model
    input_fpath = "/n/janapa_reddi_lab/Users/jquaye/neurips/"
    model = model_id.split("/")[-1]

    if "sd-vae" in model_id:
        # print("SD VAE IN INPUT NAME")
        model_id = "CompVis/stable-diffusion-v1-4"
        vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse")
        pipe = StableDiffusionPipeline.from_pretrained(model_id, vae=vae)

    elif "sdxl-turbo" in model_id:
        pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16")
    
    elif "stable-diffusion-xl-base-1.0" in model_id:
        pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")

    else:
        # Load Stable Diffusion pipeline
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,      # Enables mixed precision (saves VRAM, faster)
            # revision="fp16"                 # Important for fp16 models like SD v1.4
        )

    # Move to GPU
    pipe.to("cuda")

    # Optional: enable deterministic behavior
    pipe.enable_attention_slicing()  # Reduces memory usage (optimize based on your GPU)

    # fname = "image_ready_hate_prompts.json"
    failure = input_fname.split("_")[2]

    with open(input_fpath + input_fname) as f:
        all_prompts = json.load(f)
        f.close()

    for prompt_dict in all_prompts:
        prompt_id = prompt_dict["prompt_id"]
        attack_strategy = prompt_dict["attack_strategy"]
        batch_prompts = prompt_dict["selected_prompts"]
    
        # Use autocast for better performance with fp16
        try: 
            with torch.autocast("cuda"):
                images = pipe(prompt=batch_prompts).images   # This runs the batch together

        except Exception as e:
            print(f"Error generating images: {e}")
            continue 

        # Now images is a list of PIL.Image objects
        for i, img in enumerate(images):
            img.save(f"{output_dir}{failure}_{prompt_id}_{attack_strategy}_{model}_{i}.png")
            print(f"Saved image {i} for prompt ID {prompt_id} with attack strategy {attack_strategy}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate images using Stable Diffusion.')
    parser.add_argument('input_fname', type=str, help='Path to the input JSON file containing prompts.')
    parser.add_argument('model_id', type=str, help='The model ID to be used for image generation.')
    parser.add_argument('output_dir', type=str, help='Directory where generated images will be saved.')

    args = parser.parse_args()

    generate_imgs(args.input_fname, args.model_id, args.output_dir)


