from openai import OpenAI
import base64
import requests
import argparse
import os
import json

def generate_imgs(input_fname, model_id, output_dir):
    # Load model
    input_fpath = "/n/janapa_reddi_lab/Users/jquaye/neurips/"
    model = model_id

    # Setup OpenAIpipeline
    client = OpenAI(api_key= "YOUR API KEY")
  
    # fname = "image_ready_hate_prompts.json"
    failure = input_fname.split("_")[2]

    with open(input_fpath + input_fname) as f:
        all_prompts = json.load(f)
        f.close()

    for prompt_dict in all_prompts:
        prompt_id = prompt_dict["prompt_id"]
        attack_strategy = prompt_dict["attack_strategy"]
        batch_prompts = prompt_dict["selected_prompts"]

        for i, prompt in enumerate(batch_prompts):

            try:
                result = client.images.generate(
                    model="dall-e-2",
                    prompt=prompt,
                    size="256x256"
                )

                image_url = result.data[0].url

                # Save the image to a file
                image_data = requests.get(image_url).content

                with open(f"{output_dir}{failure}_{prompt_id}_{attack_strategy}_{model}_{i}.png", "wb") as f:
                    f.write(image_data)
                    print(f"Saved image {i} for prompt ID {prompt_id} with attack strategy {attack_strategy}")
            
            except Exception as e:
                print(f"Error generating image for prompt ID {prompt_id}: {e} and new prompt {i}: {prompt}")
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate images using Stable Diffusion.')
    parser.add_argument('input_fname', type=str, help='Path to the input JSON file containing prompts.')
    parser.add_argument('model_id', type=str, help='The model ID to be used for image generation.')
    parser.add_argument('output_dir', type=str, help='Directory where generated images will be saved.')

    args = parser.parse_args()

    generate_imgs(args.input_fname, args.model_id, args.output_dir)