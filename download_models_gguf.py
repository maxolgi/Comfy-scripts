from huggingface_hub import hf_hub_download, HfApi
import os
import argparse
import shutil

parser = argparse.ArgumentParser(description="Download GGUF and safetensors files from Hugging Face repo.")
parser.add_argument("repo_id", type=str, help="Full Hugging Face repo ID, e.g., YarvixPA/Wan2.2-S2V-14B-GGUF")
parser.add_argument("--local_dir", type=str, default="./models", help="Local destination directory")
parser.add_argument("--q", type=str, default=None, help="Quantization level to filter GGUF files, e.g., Q3 or Q3_K_M")
args = parser.parse_args()

api = HfApi()
files = api.list_repo_files(args.repo_id)

safetensors_files = [f for f in files if f.endswith('.safetensors')]
gguf_files = [f for f in files if f.endswith('.gguf')]

if args.q:
    if '_' in args.q:
        gguf_files = [f for f in gguf_files if f'-{args.q}.gguf' in f]
    else:
        gguf_files = [f for f in gguf_files if f'-{args.q}_' in f]

gguf_dir = os.path.join(args.local_dir, "unet")
vae_dir = os.path.join(args.local_dir, "vae")
text_encoder_dir = os.path.join(args.local_dir, "text_encoder")

to_download = []
for f in safetensors_files:
    if "encoder" in f.lower():
        dir_path = text_encoder_dir
    else:
        dir_path = vae_dir
    to_download.append((f, dir_path))

for f in gguf_files:
    if "encoder" in f.lower():
        dir_path = text_encoder_dir
    else:
        dir_path = gguf_dir
    to_download.append((f, dir_path))

for f, dir_path in to_download:
    base_name = os.path.basename(f)
    local_path = os.path.join(dir_path, base_name)
    if not os.path.exists(local_path):
        temp_path = hf_hub_download(repo_id=args.repo_id, filename=f)
        shutil.copy(temp_path, local_path)
    else:
        print(f"Skipping {base_name}, already exists.")
