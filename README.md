# Adversarial Nibbler Prompt-to-Image Pipeline

This repository provides the full pipeline for processing, generating, and evaluating adversarial prompts and their corresponding images based on the Adversarial Nibbler Dataset. The pipeline consists of four stages: **Pre-Processing**, **Prompt Generation**, **Image Generation**, and **Evaluation**.

---

## 🗃️ Pre-Processing

1. **Dataset Preparation**

   * The master dataset is compiled from all rounds of the Adversarial Nibbler Dataset.
   * Deduplication is performed using `dedup-comprehensive.py` to remove redundant entries.

2. **Failure Mode Splitting**

   * Prompt indices are categorized based on participant-provided failure mode annotations using `split_indices_into_failure_modes.py`.

3. **Subsampling for Experimental Balance**

   * Starting with the smallest category (`hate`), we select 250 unique prompts using `select_pids_unique_users.py`.
   * We then sample 250 prompts each for the other categories (`bias`, `sexual`, `violent`) using `after_hate_select_others.py`.
   * This process generates the following index files for downstream experiments:

     * `hate_selected_pids.json`
     * `bias_selected_pids.json`
     * `sexual_selected_pids.json`
     * `violent_selected_pids.json`

---

## ✏️ Prompt Generation

We implement and evaluate three prompting strategies:

1. **Hybrid Strategy**
   *Seed prompt + attack strategy guidance*
2. **Attack-Only Strategy**
   *Attack strategy guidance only*
3. **Seed-Only Strategy**
   *Seed prompt only, no attack guidance*

### Directory Structure

Each strategy has a dedicated folder:

* `hybrid/`
* `AO/` (Attack-Only)
* `SO/` (Seed-Only)

Each folder contains scripts to query the following LLMs:

* Claude
* GPT-4
* Gemini
* LLaMA

Example script names:

* `generate_prompts_using_claude.py`
* `generate_prompts_using_gpt4.py`
* `generate_prompts_using_gemini.py`
* `generate_prompts_using_llama.py`

### Post-Processing

1. Extract prompt text from model responses using:

   * `[neurips] extract_single_prompts_from_model_responses.ipynb`
2. Combine and select the top-4 most diverse prompts per original input using:

   * `[neurips] combine_and_select_top_4_responses.ipynb`

---

## 🖼️ Image Generation

Using the finalized prompts, images are generated with the following Text-to-Image (T2I) models:

* **DALL·E 2** (executed remotely on cluster)
* **Stable Diffusion Variants:**

  * SD VAE
  * SD 1.5
  * SD XL
  * SD XL Turbo

Stable Diffusion models are run using a unified Python script and supporting shell scripts:

* `[script location here]`

---

## ✅ Evaluation

### 1. **Image Safety Classification**

Generated images are evaluated with multiple safety classifiers:

* **NudeNet Classifier** (`nudenet_detector.py`)
* **Stable Diffusion NSFW Classifier** (`sd_nsfw.py`)
* **Q16 Classifier** (`q16.py`)

Results are tallied to compute the **Average Attack Success Rate** using:

* `[neurips] tally_classifier_output.ipynb`

### 2. **Prompt Diversity Calculation**

Diversity is measured by computing **Shannon Entropy** based on:

* **Geographic and Demographic Entities** extracted using spaCy (`GPE` and `NORP` entity types).

Evaluation script:

* `[neurips] calculate_shannon_entropy.ipynb`

---

## 📄 Citation & Acknowledgments

If you use this pipeline or dataset in your research, please cite the original Adversarial Nibbler Dataset publication.
