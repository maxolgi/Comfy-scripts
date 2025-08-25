import json
from huggingface_hub import hf_hub_download
from multiprocessing import Pool
import argparse
import os
import shutil

# Define all paths at the top
WORKSPACE_DIR = '/'
HF_HOME_DIR = os.path.join(WORKSPACE_DIR, 'hf_home')
HF_HUB_CACHE_DIR = os.path.join(HF_HOME_DIR, 'hub')
MODELS_TEMP_DIR = os.path.join(WORKSPACE_DIR, 'models_temp')
COMFYUI_MODELS_DIR = os.path.join(WORKSPACE_DIR, 'ComfyUI', 'models')

# Set environment variables
os.environ['HF_HOME'] = HF_HOME_DIR
os.environ['HF_HUB_CACHE'] = HF_HUB_CACHE_DIR

def download_model(model_info):
    repo_id, filename, subfolder, local_subdir, url = model_info
    os.makedirs(MODELS_TEMP_DIR, exist_ok=True)
    local_dir = os.path.join(COMFYUI_MODELS_DIR, local_subdir)
    os.makedirs(local_dir, exist_ok=True)
    # Download to temp
    temp_path = hf_hub_download(repo_id=repo_id, filename=filename, subfolder=subfolder, local_dir=MODELS_TEMP_DIR)
    print(f"Downloaded {filename} from {repo_id} (subfolder: {subfolder}) to {temp_path}")
    # Move to final
    final_path = os.path.join(local_dir, filename)
    shutil.move(temp_path, final_path)
    print(f"Moved {filename} to {final_path}")
    return temp_path  # Return temp_path for potential keeping

def extract_models_from_nodes(nodes, models_set, urls_list, warnings):
    for node in nodes:
        properties = node.get('properties', {})
        if 'models' in properties:
            for m in properties['models']:
                url = m.get('url')
                if not url:
                    warnings.append(f"Model in node {node.get('id')} missing URL")
                    continue
                parts = url.split('/resolve/main/')
                if len(parts) != 2:
                    warnings.append(f"Invalid URL format in node {node.get('id')}: {url}")
                    continue
                repo_base = parts[0].split('https://huggingface.co/')[1]
                repo_path = parts[1]
                filename = repo_path.split('/')[-1]
                subfolder = '/'.join(repo_path.split('/')[:-1])
                local_subdir = m.get('directory', '')
                if not local_subdir:
                    warnings.append(f"Model {filename} missing directory")
                model_tuple = (repo_base, filename, subfolder, local_subdir, url)
                models_set.add(model_tuple)
                urls_list.append(url)

def main(workflow_path, parallel, keep_temp):
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    models_set = set()
    urls_list = []
    warnings = []
    # Extract from main nodes
    extract_models_from_nodes(workflow.get('nodes', []), models_set, urls_list, warnings)
    # Extract from subgraphs
    definitions = workflow.get('definitions', {})
    subgraphs = definitions.get('subgraphs', [])
    for sg in subgraphs:
        extract_models_from_nodes(sg.get('nodes', []), models_set, urls_list, warnings)
    models = list(models_set)
    # Print all models found
    print("All models found:")
    for model in models:
        print(f"- Filename: {model[1]}, Repo: {model[0]}, Subfolder: {model[2]}, Directory: {model[3]}, URL: {model[4]}")
    # Print list of all URLs
    print("\nAll URLs:")
    for url in urls_list:
        print(f"- {url}")
    # Print warnings
    if warnings:
        print("\nWarnings:")
        for warn in warnings:
            print(f"- {warn}")
    # Parallel download
    with Pool(processes=parallel) as pool:
        temp_paths = pool.map(download_model, models)
    # Handle keep_temp
    if not keep_temp:
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"Deleted temp file: {temp_path}")
        if os.path.exists(MODELS_TEMP_DIR) and not os.listdir(MODELS_TEMP_DIR):
            os.rmdir(MODELS_TEMP_DIR)
            print(f"Removed empty {MODELS_TEMP_DIR} directory")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download models from ComfyUI workflow JSON")
    parser.add_argument('workflow_path', type=str, help="Path to the workflow JSON file")
    parser.add_argument('--parallel', type=int, default=10, help="Number of parallel downloads (default: 10)")
    parser.add_argument('--keep_temp', action='store_true', help="Keep the /models_temp directory and files (default: False)")
    args = parser.parse_args()
    main(args.workflow_path, args.parallel, args.keep_temp)
