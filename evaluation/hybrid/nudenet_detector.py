from glob import glob
import os
from nudenet import NudeDetector
import argparse
import json


def run_nudenet_for_failure_case(failure: str):
    img_dir = '/n/janapa_reddi_lab/Users/jquaye/neurips/hybrid_imgs/'
    failure_imgs_dir = img_dir + failure + '_imgs/'

    fnames = os.listdir(failure_imgs_dir)
    paired_dict = {}

    detector = NudeDetector()

    for fname in fnames:
        fpath = failure_imgs_dir + fname

        try:
            detection_list = detector.detect(fpath)
            paired_dict[fname] = detection_list

            output_fname = '/n/janapa_reddi_lab/Users/jquaye/neurips/nudenet_' + failure + '.json'
            with open(output_fname, 'w') as json_file:
                    json.dump(paired_dict, json_file, indent=4)
                    print(f"✅ Processed {fname} successfully.")

        except Exception as e:
            print(f"⚠️ Error processing {fname}: {e}")
            continue

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run NudeNet classifier for a given failure category.')
    parser.add_argument('failure', type=str,
                        help="Name of the failure group (e.g., 'bias')")

    args = parser.parse_args()
    run_nudenet_for_failure_case(failure=args.failure)