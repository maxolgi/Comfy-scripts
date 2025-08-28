import json
from huggingface_hub import hf_hub_download
from multiprocessing import Pool
import os
import shutil
import sys
import requests
from nicegui import ui

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
    repo_id, filename, subfolder, local_subdir, url, overwrite = model_info
    os.makedirs(MODELS_TEMP_DIR, exist_ok=True)
    local_dir = os.path.join(COMFYUI_MODELS_DIR, local_subdir)
    os.makedirs(local_dir, exist_ok=True)
    final_path = os.path.join(local_dir, filename)
    if os.path.exists(final_path) and not overwrite:
        print(f"Skipping existing {filename} in {local_dir}")
        return None
    # Download to temp
    temp_path = hf_hub_download(repo_id=repo_id, filename=filename, subfolder=subfolder, local_dir=MODELS_TEMP_DIR)
    print(f"Downloaded {filename} from {repo_id} (subfolder: {subfolder}) to {temp_path}")
    # Move to final
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
                clean_repo_path = repo_path.split('?')[0]
                filename = clean_repo_path.split('/')[-1]
                subfolder = '/'.join(clean_repo_path.split('/')[:-1])
                local_subdir = m.get('directory', '')
                if not local_subdir:
                    warnings.append(f"Model {filename} missing directory")
                model_tuple = (repo_base, filename, subfolder, local_subdir, url)
                models_set.add(model_tuple)
                urls_list.append(url)

async def download_for_template(template_name):
    workflow_url = f"https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/{template_name}.json"
    response = requests.get(workflow_url)
    if response.status_code != 200:
        ui.notify(f"Failed to fetch {template_name}")
        return
    workflow = response.json()
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
    # Defaults: parallel=1, keep_temp=False, overwrite=False
    skipped = []
    for repo_id, filename, subfolder, local_subdir, url in models:
        local_dir = os.path.join(COMFYUI_MODELS_DIR, local_subdir)
        final_path = os.path.join(local_dir, filename)
        if os.path.exists(final_path):
            skipped.append((repo_id, filename, subfolder, local_subdir, url))
    to_download = [model for model in models if model not in skipped]
    models_with_overwrite = [(repo_id, filename, subfolder, local_subdir, url, False) for repo_id, filename, subfolder, local_subdir, url in to_download]
    pool = Pool(processes=1)
    temp_paths = []
    try:
        temp_paths = pool.map(download_model, models_with_overwrite)
    except KeyboardInterrupt:
        print("Interrupted by user.")
        pool.terminate()
        if os.path.exists(MODELS_TEMP_DIR):
            shutil.rmtree(MODELS_TEMP_DIR, ignore_errors=True)
            print(f"Removed temporary directory: {MODELS_TEMP_DIR}")
        sys.exit(1)
    else:
        pool.close()
    finally:
        pool.join()
    # Handle keep_temp=False
    for temp_path in temp_paths:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Deleted temp file: {temp_path}")
    if os.path.exists(MODELS_TEMP_DIR) and not os.listdir(MODELS_TEMP_DIR):
        os.rmdir(MODELS_TEMP_DIR)
        print(f"Removed empty {MODELS_TEMP_DIR} directory")
    ui.notify(f"Downloaded models for {template_name}")

def build_ui():
    comfyui_url = "http://localhost:8888"
    response = requests.get(f"{comfyui_url}/api/workflow_templates")
    categories = response.json()
    with ui.tabs().classes('w-full') as tabs:
        for cat in categories:
            with ui.tab(cat['moduleName']):
                for templ in cat['templates']:
                    with ui.row():
                        ui.label(templ['name'])
                        ui.button('Download Models', on_click=lambda t=templ['name']: download_for_template(t))

build_ui()
ui.run()
