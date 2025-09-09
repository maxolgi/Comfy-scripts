#!/bin/bash
wget -q --directory-prefix=/ComfyUI/models/checkpoints https://huggingface.co/Comfy-Org/stable-audio-open-1.0_repackaged/resolve/main/stable-audio-open-1.0.safetensors &
wget -q --directory-prefix=/ComfyUI/models/text_encoders https://huggingface.co/ComfyUI-Wiki/t5-base/resolve/main/t5-base.safetensors &
wget -q --directory-prefix=/ComfyUI/models/checkpoints https://huggingface.co/Comfy-Org/ACE-Step_ComfyUI_repackaged/resolve/main/all_in_one/ace_step_v1_3.5b.safetensors &
