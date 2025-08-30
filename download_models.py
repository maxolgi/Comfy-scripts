import json
from huggingface_hub import hf_hub_download
from multiprocessing import Pool
import argparse
import os
import shutil
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Note: For --watch option, install watchdog via pip install watchdog

# Define all paths at the top
WORKSPACE_DIR = '/'
HF_HOME_DIR = os.path.join(WORKSPACE_DIR, 'hf_home')
HF_HUB_CACHE_DIR = os.path.join(HF_HOME_DIR, 'hub')
MODELS_TEMP_DIR = os.path.join(WORKSPACE_DIR, 'models_temp')
COMFYUI_MODELS_DIR = os.path.join(WORKSPACE_DIR, 'ComfyUI', 'models')

# Set environment variables
os.environ['HF_HOME'] = HF_HOME_DIR
os.environ['HF_HUB_CACHE'] = HF_HUB_CACHE_DIR

MODEL_MAPPING = {
    'qwen-image-q8_0.gguf': ('city96/Qwen-Image-gguf', '', 'unet_gguf'),
    'umt5_xxl_fp8_e4m3fn_scaled.safetensors': ('Comfy-Org/Wan_2.1_ComfyUI_repackaged', 'split_files/text_encoders', 'clip'),
    'wan_2.1_vae.safetensors': ('Comfy-Org/Wan_2.1_ComfyUI_repackaged', 'split_files/vae', 'vae'),
    'wav2vec2_large_english_fp16.safetensors': ('Comfy-Org/Wan_2.2_Comfy_Repackaged', 'split_files/audio_encoders', 'audio_encoders'),
    'qwen-image-lightning-8steps-v1.1-bf16.safetensors': ('lightx2v/Qwen-Image-Lightning', '', 'loras'),
    'wan2.2-s2v-14b-q8_0.gguf': ('QuantStack/Wan2.2-S2V-14B-GGUF', '', 'unet_gguf'),
    'lightx2v_i2v_14b_480p_cfg_step_distill_rank64_bf16.safetensors': ('Kijai/WanVideo_comfy', 'Lightx2v', 'loras')
}

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

        # Auto-parse from specific node types
        node_type = node.get('type')
        if node_type in ['UnetLoaderGGUFDisTorchMultiGPU', 'CLIPLoader', 'VAELoader', 'AudioEncoderLoader', 'LoraLoaderModelOnly']:
            filename_path = node.get('widgets_values', [None])[0]
            if filename_path:
                # Handle paths with \ or /
                split_path = filename_path.replace('\\', '/').split('/')
                filename = split_path[-1]
                path_prefix = '/'.join(split_path[:-1]) + '/' if len(split_path) > 1 else ''
                key = filename.lower()
                if key in MODEL_MAPPING:
                    repo_id, subfolder, base_subdir = MODEL_MAPPING[key]
                    local_subdir = base_subdir + '/' + path_prefix.rstrip('/') if path_prefix else base_subdir
                    url = f"https://huggingface.co/{repo_id}/resolve/main/{subfolder}/{filename}" if subfolder else f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
                    model_tuple = (repo_id, filename, subfolder, local_subdir, url)
                    models_set.add(model_tuple)
                    urls_list.append(url)
                else:
                    warnings.append(f"Unmapped filename {filename} in node {node.get('id')} type {node_type}")

def process_directory(directory, parallel, keep_temp, overwrite):
    models_set = set()
    urls_list = []
    warnings = []
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    for json_file in json_files:
        path = os.path.join(directory, json_file)
        with open(path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
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
    # Check skipped models
    skipped = []
    for repo_id, filename, subfolder, local_subdir, url in models:
        local_dir = os.path.join(COMFYUI_MODELS_DIR, local_subdir)
        final_path = os.path.join(local_dir, filename)
        if os.path.exists(final_path) and not overwrite:
            skipped.append((repo_id, filename, subfolder, local_subdir, url))
    if skipped:
        print("\nModels that will not be downloaded (exist):")
        for model in skipped:
            print(f"- Filename: {model[1]}, Repo: {model[0]}, Subfolder: {model[2]}, Directory: {model[3]}, URL: {model[4]}")
    # Filter models to download
    to_download = [model for model in models if model not in skipped]
    # Prepare models with overwrite
    models_with_overwrite = [(repo_id, filename, subfolder, local_subdir, url, overwrite) for repo_id, filename, subfolder, local_subdir, url in to_download]
    # Parallel download
    pool = Pool(processes=parallel)
    temp_paths = []
    try:
        temp_paths = pool.map(download_model, models_with_overwrite)
    except KeyboardInterrupt:
        print("Interrupted by user.")
        pool.terminate()
        if not keep_temp and os.path.exists(MODELS_TEMP_DIR):
            shutil.rmtree(MODELS_TEMP_DIR, ignore_errors=True)
            print(f"Removed temporary directory: {MODELS_TEMP_DIR}")
        sys.exit(1)
    else:
        pool.close()
    finally:
        pool.join()
    # Handle keep_temp
    if not keep_temp:
        for temp_path in temp_paths:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"Deleted temp file: {temp_path}")
        if os.path.exists(MODELS_TEMP_DIR) and not os.listdir(MODELS_TEMP_DIR):
            os.rmdir(MODELS_TEMP_DIR)
            print(f"Removed empty {MODELS_TEMP_DIR} directory")

def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        print(f"Fork #1 failed: {e}")
        sys.exit(1)

    os.chdir('/')
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        print(f"Fork #2 failed: {e}")
        sys.exit(1)

    sys.stdout.flush()
    sys.stderr.flush()
    with open(os.devnull, 'r') as si, open(os.devnull, 'a+') as so, open(os.devnull, 'a+') as se:
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

def main(workflow_path, directory, parallel, keep_temp, overwrite, watch, daemon):
    if not workflow_path and not directory:
        parser.print_help()
        sys.exit(0)
    if watch and not directory:
        print("Error: --watch requires --directory")
        sys.exit(1)
    if daemon and not (watch and directory):
        print("Error: --daemon requires --watch and --directory")
        sys.exit(1)
    
    if daemon:
        daemonize()
    
    models_set = set()
    urls_list = []
    warnings = []
    
    if directory:
        if watch and not os.path.exists(directory):
            print("Directory does not exist yet. Waiting for it to be created...")
            try:
                while not os.path.exists(directory):
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Waiting interrupted.")
                sys.exit(0)
            print("Directory created. Starting initial processing and watching.")
        process_directory(directory, parallel, keep_temp, overwrite)
    
    if workflow_path:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
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
        # Check skipped models
        skipped = []
        for repo_id, filename, subfolder, local_subdir, url in models:
            local_dir = os.path.join(COMFYUI_MODELS_DIR, local_subdir)
            final_path = os.path.join(local_dir, filename)
            if os.path.exists(final_path) and not overwrite:
                skipped.append((repo_id, filename, subfolder, local_subdir, url))
        if skipped:
            print("\nModels that will not be downloaded (exist):")
            for model in skipped:
                print(f"- Filename: {model[1]}, Repo: {model[0]}, Subfolder: {model[2]}, Directory: {model[3]}, URL: {model[4]}")
        # Filter models to download
        to_download = [model for model in models if model not in skipped]
        # Prepare models with overwrite
        models_with_overwrite = [(repo_id, filename, subfolder, local_subdir, url, overwrite) for repo_id, filename, subfolder, local_subdir, url in to_download]
        # Parallel download
        pool = Pool(processes=parallel)
        temp_paths = []
        try:
            temp_paths = pool.map(download_model, models_with_overwrite)
        except KeyboardInterrupt:
            print("Interrupted by user.")
            pool.terminate()
            if not keep_temp and os.path.exists(MODELS_TEMP_DIR):
                shutil.rmtree(MODELS_TEMP_DIR, ignore_errors=True)
                print(f"Removed temporary directory: {MODELS_TEMP_DIR}")
            sys.exit(1)
        else:
            pool.close()
        finally:
            pool.join()
        # Handle keep_temp
        if not keep_temp:
            for temp_path in temp_paths:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                    print(f"Deleted temp file: {temp_path}")
            if os.path.exists(MODELS_TEMP_DIR) and not os.listdir(MODELS_TEMP_DIR):
                os.rmdir(MODELS_TEMP_DIR)
                print(f"Removed empty {MODELS_TEMP_DIR} directory")
    
    if watch:
        class WorkflowHandler(FileSystemEventHandler):
            def __init__(self, directory, parallel, keep_temp, overwrite):
                self.directory = directory
                self.parallel = parallel
                self.keep_temp = keep_temp
                self.overwrite = overwrite

            def on_modified(self, event):
                if event.src_path.endswith('.json'):
                    print(f"Detected change in {event.src_path}, rerunning model download...")
                    process_directory(self.directory, self.parallel, self.keep_temp, self.overwrite)

            def on_created(self, event):
                if event.src_path.endswith('.json'):
                    print(f"Detected new file {event.src_path}, rerunning model download...")
                    process_directory(self.directory, self.parallel, self.keep_temp, self.overwrite)

        event_handler = WorkflowHandler(directory, parallel, keep_temp, overwrite)
        observer = Observer()
        observer.schedule(event_handler, path=directory, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print("Watching stopped.")
            sys.exit(0)
        observer.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download models from ComfyUI workflow JSON")
    parser.add_argument('workflow_path', nargs='?', default=None, help="Path to the workflow JSON file")
    parser.add_argument('--directory', type=str, default=None, help="Directory containing multiple workflow JSON files")
    parser.add_argument('--parallel', type=int, default=1, help="Number of parallel downloads (default: 1)")
    parser.add_argument('--keep_temp', action='store_true', help="Keep the /models_temp directory and files (default: False)")
    parser.add_argument('--overwrite', action='store_true', help="Force overwrite if model exists in target (default: False)")
    parser.add_argument('--watch', action='store_true', help="Watch the directory for changes and rerun on file add/change (requires --directory)")
    parser.add_argument('--daemon', action='store_true', help="Daemonize the process to run in background (requires --watch and --directory)")
    args = parser.parse_args()
    if args.directory:
        args.directory = os.path.abspath(args.directory)
    if args.workflow_path:
        args.workflow_path = os.path.abspath(args.workflow_path)
    main(args.workflow_path, args.directory, args.parallel, args.keep_temp, args.overwrite, args.watch, args.daemon)
