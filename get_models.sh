#!/bin/bash
#python3 /workspace/ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /workspace/ComfyUI/models --q Q3_K_M QuantStack/Wan2.2-S2V-14B-GGUF &
#python3 /workspace/ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /workspace/ComfyUI/models --q Q3_K_M QuantStack/Wan2.2-TI2V-5B-GGUF &
#python3 /workspace/ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /workspace/ComfyUI/models --q Q3_K_M QuantStack/Wan2.2-T2V-A14B-GGUF &
#python3 /workspace/ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /workspace/ComfyUI/models --q Q3_K_M QuantStack/Wan2.2-I2V-A14B-GGUF &
#python3 /workspace/ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /workspace/ComfyUI/models --q Q3_K_M city96/umt5-xxl-encoder-gguf &
#python3 /workspace/ComfyUI/Comfy-scripts/download_models.py /workspace/ComfyUI/Comfy-scripts/gen-img-vid-52.json
wget --directory-prefix=/workspace/ComfyUI/models/loras https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors &
wget --directory-prefix=/workspace/ComfyUI/models/loras https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors &
wget --directory-prefix=/workspace/ComfyUI/models/text_encoders https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors &
wget --directory-prefix=/workspace/ComfyUI/models/diffusion_models https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors &
wget --directory-prefix=/workspace/ComfyUI/models/diffusion_models https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors &
wget --directory-prefix=/workspace/ComfyUI/models/diffusion_models https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_fun_control_low_noise_14B_fp8_scaled.safetensors &
wget --directory-prefix=/workspace/ComfyUI/models/diffusion_models https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_fun_control_high_noise_14B_fp8_scaled.safetensors &
wget --directory-prefix=/workspace/ComfyUI/models/diffusion_models https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_fun_camera_low_noise_14B_fp8_scaled.safetensors &
wget --directory-prefix=/workspace/ComfyUI/models/diffusion_models https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_fun_camera_high_noise_14B_fp8_scaled.safetensors &
wget --directory-prefix=/workspace/ComfyUI/models/vae https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors
