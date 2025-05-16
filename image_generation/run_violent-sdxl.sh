#!/bin/bash

#SBATCH -p gpu_requeue       
#SBATCH -o violent_sd-xl_%j.out     # Standard output and error log
#SBATCH -e violent_sd-xl_%j.err      # Separate error file
#SBATCH -c 4                 # Number of CPU cores
#SBATCH --mem 8G                         # Total memory
#SBATCH -t 10:00:00                   # Time limit hrs:min:sec
#SBATCH --gres=gpu:1

# Load any required modules (adjust based on your environment)
module load python/3.10.9-fasrc01

# Activate environment if needed
source ~/.bashrc
conda activate acl_env

# Define variables
MODEL_ID="stabilityai/stable-diffusion-xl-base-1.0"
INPUT_FNAME="image_ready_violent_prompts.json"
OUTPUT_DIR="/n/janapa_reddi_lab/Users/jquaye/neurips/violent_imgs/"

# Run the Python script with the defined variables
python3 generate_sd_imgs.py "$INPUT_FNAME" "$MODEL_ID" "$OUTPUT_DIR"
