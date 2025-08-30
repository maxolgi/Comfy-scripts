#!/bin/bash
python3 /ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /ComfyUI/models --q Q3_K_M QuantStack/Wan2.2-S2V-14B-GGUF &
python3 /ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /ComfyUI/models --q Q3_K_M QuantStack/Wan2.2-TI2V-5B-GGUF &
python3 /ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /ComfyUI/models --q Q3_K_M QuantStack/Wan2.2-T2V-A14B-GGUF &
python3 /ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /ComfyUI/models --q Q3_K_M QuantStack/Wan2.2-I2V-A14B-GGUF &
python3 /ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /ComfyUI/models --q Q3_K_M city96/umt5-xxl-encoder-gguf &
python3 /ComfyUI/Comfy-scripts/download_models.py --watch --daemon --directory /ComfyUI/user/default/workflows/
