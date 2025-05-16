#!/bin/bash
#SBATCH -p shared       
#SBATCH -o dalle_violent_%j.out     # Standard output and error log
#SBATCH -e dalle_violent_%j.err      # Separate error file
#SBATCH -c 4                 # Number of CPU cores
#SBATCH --mem 8G                         # Total memory
#SBATCH -t 20:00:00                   # Time limit hrs:min:sec



# Activate environment if needed
source ~/.bashrc
conda activate acl_env

# Load any required modules (adjust based on your environment)
module load python/3.10.9-fasrc01

# Define variables
MODEL_ID="dall-e-2"  # Model ID for DALL-E 2
INPUT_FNAME="image_ready_violent_prompts.json"
OUTPUT_DIR="/n/janapa_reddi_lab/Users/jquaye/neurips/violent_imgs/"

# Run the Python script with the defined variables
python3 -m pip install --force-reinstall openai
python3 generate_dalle_imgs.py "$INPUT_FNAME" "$MODEL_ID" "$OUTPUT_DIR"