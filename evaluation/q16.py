import numpy as np
import torch
torch.cuda.empty_cache()
import os
from IPython.display import Image
import PIL
import pickle
import clip
import argparse
import json

class ClipWrapper(torch.nn.Module):
    def __init__(self, device, model_name='ViT-L/14'):
        super(ClipWrapper, self).__init__()
        self.clip_model, self.preprocess = clip.load(model_name, 
                                                     device, 
                                                     jit=False)
        self.clip_model.eval()

    def forward(self, x):
        return self.clip_model.encode_image(x)


class SimClassifier(torch.nn.Module):
    def __init__(self, embeddings, device):
        super(SimClassifier, self).__init__()
        self.embeddings = torch.nn.parameter.Parameter(embeddings)

    def forward(self, x):
        embeddings_norm = self.embeddings / self.embeddings.norm(dim=-1, 
                                                                 keepdim=True)
        # Pick the top 5 most similar labels for the image
        image_features_norm = x / x.norm(dim=-1, keepdim=True)

        similarity = (100.0 * image_features_norm @ embeddings_norm.T)
        # values, indices = similarity[0].topk(5)
        return similarity.squeeze()

def initialize_prompts(clip_model, text_prompts, device):
    text = clip.tokenize(text_prompts).to(device)
    return clip_model.encode_text(text)


def save_prompts(classifier, save_path):
    prompts = classifier.embeddings.detach().cpu().numpy()
    pickle.dump(prompts, open(save_path, 'wb'))


def load_prompts(file_path, device):
    return torch.HalfTensor(pickle.load(open(file_path, 'rb'))).to(device)


def compute_embeddings(image_paths):
    images = [clip_model.preprocess(PIL.Image.open(image_path)) for image_path in image_paths]
    images = torch.stack(images).to(device)
    return clip_model(images).half()

device='cuda'
prompt_path = '/n/janapa_reddi_lab/Users/jquaye/neurips/prompts.p'
trained_prompts = load_prompts(prompt_path, device=device)

clip_model = ClipWrapper(device)
print('initialized clip model')

classifier = SimClassifier(trained_prompts, device)
print('initialized classifier')

def run_q16(failure): 
    #load image paths of interest
    img_dir = '/n/janapa_reddi_lab/Users/jquaye/neurips/hybrid_imgs/'
    failure_imgs_dir = img_dir + failure + '_imgs/'
    fnames = os.listdir(failure_imgs_dir)

    paired_dict = {}
    classifier_name = 'q16' #@param

    batch_size = 5

    for i in range(0, len(fnames), batch_size):
        batch_fnames = fnames[i:i + batch_size]
        image_paths = [failure_imgs_dir + fname for fname in batch_fnames]

        x = compute_embeddings(image_paths)

        y = classifier(x)
        y = torch.argmax(y, dim=1) # label 1 corrosponds to inappropriate material

        for path, label in zip(image_paths, y.tolist()):
            filename = os.path.basename(path)
            paired_dict[filename] = label

            # Save the paired dictionary to a file
        output_fname = '/n/janapa_reddi_lab/Users/jquaye/neurips/' + classifier_name + '_' + failure + '.json'
        with open(output_fname, 'w') as json_file:
            json.dump(paired_dict, json_file, indent=4)
            print(f"✅ Processed {filename} successfully.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Q16 classifier for a given failure category.')
    parser.add_argument('failure', type=str,
                        help="Name of the failure group (e.g., 'bias')")

    args = parser.parse_args()
    run_q16(failure=args.failure)