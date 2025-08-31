#!/bin/bash
python3 /ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /ComfyUI/models --q Q3_K_M QuantStack/Wan2.2-I2V-A14B-GGUF &
python3 /ComfyUI/Comfy-scripts/download_models_gguf.py --local_dir /ComfyUI/models --q Q3_K_M city96/umt5-xxl-encoder-gguf &
python /ComfyUI/Comfy-scripts/download_models.py /ComfyUI/Comfy-scripts/video_wan2_2_14B_i2v-gguf.json &

git clone https://github.com/city96/ComfyUI-GGUF /ComfyUI/custom_nodes/ComfyUI-GGUF
git checkout d247022e3fa66851c5084cc251b076aab816423d
pip install --upgrade gguf

cd /ComfyUI/custom_nodes/ComfyUI-Manager && python cm-cli.py update all
