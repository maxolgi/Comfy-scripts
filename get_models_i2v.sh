#!/bin/bash
python3 /workspace/ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /workspace/ComfyUI/models --q Q3_K_M QuantStack/Wan2.2-I2V-A14B-GGUF &
python3 /workspace/ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /workspace/ComfyUI/models --q Q3_K_M city96/umt5-xxl-encoder-gguf &
wget --directory-prefix=/workspace/ComfyUI/models/loras https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors &
wget --directory-prefix=/workspace/ComfyUI/models/loras https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors &
