import gradio as gr
import requests
import json
import time
import base64
from io import BytesIO
from PIL import Image
import os
import random
import sys
import argparse
import re

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

parser = argparse.ArgumentParser(description="Gradio app for video generation")
parser.add_argument("listen_ip_port", type=str, help="IP:port for Gradio to listen on, e.g., 0.0.0.0:7860")
parser.add_argument("comfyui_ip_port", type=str, help="IP:port for ComfyUI API, e.g., 192.168.1.3:8888")
parser.add_argument("--comfyui_public_url", type=str, default=None, help="Public URL for ComfyUI (e.g., for proxies)")
parser.add_argument("--debug", action="store_true", help="Enable debug printing for API calls")
parser.add_argument("--max_history_videos", type=int, default=1, help="Maximum number of history videos to display")
args = parser.parse_args()

listen_ip_port = args.listen_ip_port
server_name, server_port_str = listen_ip_port.split(':')
server_port = int(server_port_str)

COMFYUI_URL = f"http://{args.comfyui_ip_port}"
comfyui_public_url = args.comfyui_public_url if args.comfyui_public_url else COMFYUI_URL
debug = args.debug
max_history_videos = args.max_history_videos

# Hardcoded API workflow from api.json
workflow = {
  "8": {
    "inputs": {
      "clip_name": "umt5-xxl-encoder-Q3_K_M.gguf",
      "type": "wan"
    },
    "class_type": "CLIPLoaderGGUF",
    "_meta": {
      "title": "CLIPLoader (GGUF)"
    }
  },
  "9": {
    "inputs": {
      "text": "",
      "clip": [
        "8",
        0
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Negative Prompt)"
    }
  },
  "15": {
    "inputs": {
      "filename_prefix": "video/CameraImage",
      "format": "auto",
      "codec": "auto",
      "video_preview": "",
      "video": [
        "14:1366",
        0
      ]
    },
    "class_type": "SaveVideo",
    "_meta": {
      "title": "Save Video"
    }
  },
  "20": {
    "inputs": {
      "text": "Beautiful young European woman with honey blonde hair gracefully turning her head back over shoulder, gentle smile, bright eyes looking at camera. Hair flowing in slow motion as she turns. Soft natural lighting, clean background, cinematic slow-motion portrait.",
      "clip": [
        "8",
        0
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Positive Prompt)"
    }
  },
  "22": {
    "inputs": {
      "image": "Capture.JPG"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "14:1365": {
    "inputs": {
      "samples": [
        "14:1376",
        0
      ],
      "vae": [
        "14:1377",
        0
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "14:1368": {
    "inputs": {
      "shift": 5.000000000000001,
      "model": [
        "14:1372",
        0
      ]
    },
    "class_type": "ModelSamplingSD3",
    "_meta": {
      "title": "ModelSamplingSD3"
    }
  },
  "14:1370": {
    "inputs": {
      "shift": 5.000000000000001,
      "model": [
        "14:1375",
        0
      ]
    },
    "class_type": "ModelSamplingSD3",
    "_meta": {
      "title": "ModelSamplingSD3"
    }
  },
  "14:1372": {
    "inputs": {
      "lora_name": "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",
      "strength_model": 1.0000000000000002,
      "model": [
        "14:1371",
        0
      ]
    },
    "class_type": "LoraLoaderModelOnly",
    "_meta": {
      "title": "LoraLoaderModelOnly"
    }
  },
  "14:1375": {
    "inputs": {
      "lora_name": "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors",
      "strength_model": 1.0000000000000002,
      "model": [
        "14:1374",
        0
      ]
    },
    "class_type": "LoraLoaderModelOnly",
    "_meta": {
      "title": "LoraLoaderModelOnly"
    }
  },
  "14:1377": {
    "inputs": {
      "vae_name": "Wan2.1_VAE.safetensors"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "14:1366": {
    "inputs": {
      "fps": 16,
      "images": [
        "14:1365",
        0
      ]
    },
    "class_type": "CreateVideo",
    "_meta": {
      "title": "Create Video"
    }
  },
  "14:1369": {
    "inputs": {
      "add_noise": "enable",
      "noise_seed": 1093964355475357,
      "steps": 2,
      "cfg": 1,
      "sampler_name": "euler",
      "scheduler": "simple",
      "start_at_step": 0,
      "end_at_step": 1,
      "return_with_leftover_noise": "enable",
      "model": [
        "14:1370",
        0
      ],
      "positive": [
        "14:1373",
        0
      ],
      "negative": [
        "14:1373",
        1
      ],
      "latent_image": [
        "14:1373",
        2
      ]
    },
    "class_type": "KSamplerAdvanced",
    "_meta": {
      "title": "KSampler (Advanced)"
    }
  },
  "14:1376": {
    "inputs": {
      "add_noise": "disable",
      "noise_seed": 0,
      "steps": 2,
      "cfg": 1,
      "sampler_name": "euler",
      "scheduler": "simple",
      "start_at_step": 1,
      "end_at_step": 2,
      "return_with_leftover_noise": "disable",
      "model": [
        "14:1368",
        0
      ],
      "positive": [
        "14:1373",
        0
      ],
      "negative": [
        "14:1373",
        1
      ],
      "latent_image": [
        "14:1369",
        0
      ]
    },
    "class_type": "KSamplerAdvanced",
    "_meta": {
      "title": "KSampler (Advanced)"
    }
  },
  "14:1373": {
    "inputs": {
      "width": 464,
      "height": 688,
      "length": 101,
      "batch_size": 1,
      "positive": [
        "20",
        0
      ],
      "negative": [
        "9",
        0
      ],
      "vae": [
        "14:1377",
        0
      ],
      "start_image": [
        "22",
        0
      ]
    },
    "class_type": "WanImageToVideo",
    "_meta": {
      "title": "WanImageToVideo"
    }
  },
  "14:1374": {
    "inputs": {
      "unet_name": "Wan2.2-I2V-A14B-HighNoise-Q3_K_M.gguf"
    },
    "class_type": "UnetLoaderGGUF",
    "_meta": {
      "title": "Unet Loader (GGUF)"
    }
  },
  "14:1371": {
    "inputs": {
      "unet_name": "Wan2.2-I2V-A14B-LowNoise-Q3_K_M.gguf"
    },
    "class_type": "UnetLoaderGGUF",
    "_meta": {
      "title": "Unet Loader (GGUF)"
    }
  }
}

def get_all_videos(num_videos):
    url = f"{COMFYUI_URL}/history"
    if debug:
        print(f"Debug: Sending GET to {url}")
    history_response = requests.get(url)
    if debug:
        print(f"Debug: Response status: {history_response.status_code}, content: {history_response.json() if history_response.content else history_response.text}")
    all_history = history_response.json()
    videos = []
    for prompt_id, entry in all_history.items():
        if "outputs" in entry and "15" in entry["outputs"]:
            node_output = entry["outputs"]["15"]
            if "images" in node_output and node_output["images"]:
                video_info = node_output["images"][0]
                filename = video_info["filename"]
                if filename.startswith("Gradio_"):
                    match = re.search(r"Gradio_(\d+)", filename)
                    if match:
                        ts = int(match.group(1))
                        subfolder = video_info.get("subfolder", "")
                        type_ = video_info.get("type", "output")
                        video_url = f"{comfyui_public_url}/view?filename={filename}&subfolder={subfolder}&type={type_}"
                        videos.append((ts, video_url))
    videos.sort(key=lambda x: x[0], reverse=True)
    videos = videos[:num_videos]
    return [v[1] for v in videos]

def render_video_list(video_urls):
    html = '<div style="display: flex; flex-direction: column;">'
    for i, url in enumerate(video_urls):
        video_id = f"video_{i}"
        html += f'''
        <div style="position: relative; margin-bottom: 10px;">
            <video id="{video_id}" controls autoplay="false" src="{url}" style="max-width: 100%;"></video>
            <div id="context-menu-{video_id}" style="display: none; position: absolute; background: #333; color: white; border: 1px solid #555; border-radius: 4px; z-index: 1000;">
                <div style="padding: 8px; cursor: pointer;" onclick="window.location.href='{url}&download=true'">Download to Camera Roll</div>
            </div>
        </div>
        '''
    html += '''
    <script>
        document.querySelectorAll('video').forEach(video => {
            const contextMenu = document.getElementById(`context-menu-${video.id}`);
            video.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                contextMenu.style.display = 'block';
                contextMenu.style.left = `${e.pageX}px`;
                contextMenu.style.top = `${e.pageY}px`;
            });
            document.addEventListener('click', () => {
                contextMenu.style.display = 'none';
            });
        });
    </script>
    </div>
    '''
    return html

def update_history():
    video_urls = get_all_videos(max_history_videos)
    return render_video_list(video_urls)

def generate_video(prompt, image, debug=False):
    if image is None:
        return "", None
    
    try:
        # Upload image
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
        files = {'image': ('upload.jpg', img_bytes, 'image/jpeg')}
        url = f"{COMFYUI_URL}/upload/image"
        if debug:
            print(f"Debug: Sending POST to {url} with files={files}")
        upload_response = requests.post(url, files=files)
        if debug:
            print(f"Debug: Response status: {upload_response.status_code}, content: {upload_response.json() if upload_response.content else upload_response.text}")
        uploaded_filename = upload_response.json()["name"]
        
        # Update workflow
        workflow["22"]["inputs"]["image"] = uploaded_filename
        workflow["20"]["inputs"]["text"] = prompt if prompt else ""
        prefix = f"video/Gradio_{int(time.time())}"
        workflow["15"]["inputs"]["filename_prefix"] = prefix
        workflow["14:1369"]["inputs"]["noise_seed"] = random.randint(0, 2**64 - 1)
        
        # Queue prompt
        prompt_data = {"prompt": workflow}
        url = f"{COMFYUI_URL}/prompt"
        if debug:
            print(f"Debug: Sending POST to {url} with json={prompt_data}")
        queue_response = requests.post(url, json=prompt_data)
        if debug:
            print(f"Debug: Response status: {queue_response.status_code}, content: {queue_response.json() if queue_response.content else queue_response.text}")
        prompt_id = queue_response.json()["prompt_id"]
        
        # Poll history with progress
        start_time = time.time()
        timeout = 300
        while time.time() - start_time < timeout:
            url = f"{COMFYUI_URL}/history/{prompt_id}"
            if debug:
                print(f"Debug: Sending GET to {url}")
            history_response = requests.get(url)
            if debug:
                print(f"Debug: Response status: {history_response.status_code}, content: {history_response.json() if history_response.content else history_response.text}")
            history = history_response.json()
            if prompt_id in history:
                break
            time.sleep(2)
        
        if prompt_id not in history:
            return "", None
        
        # Parse exact video info
        node_output = history[prompt_id]["outputs"]["15"]
        video_info = node_output["images"][0]
        filename = video_info["filename"]
        subfolder = video_info.get("subfolder", "")
        type_ = video_info.get("type", "output")
        video_url = f"{comfyui_public_url}/view?filename={filename}&subfolder={subfolder}&type={type_}"
        new_video_html = f'<video controls autoplay="false" src="{video_url}" style="max-width: 100%;"></video>'
        
        video_urls = get_all_videos(max_history_videos)
        history_html = render_video_list(video_urls)
        
        return new_video_html, history_html
    except Exception as e:
        if debug:
            import traceback
            print(f"Debug: Exception details: {traceback.format_exc()}")
        return "", None

with gr.Blocks(css="footer {display: none !important;}", js="""() => { const params = new URLSearchParams(window.location.search); if (!params.has('__theme')) { params.set('__theme', 'dark'); window.location.search = params.toString(); } const observer = new MutationObserver(() => { const modals = document.querySelectorAll('.gr-modal'); modals.forEach(modal => { if (modal.textContent.includes('connection might break')) { modal.style.display = 'none'; } }); }); observer.observe(document.body, { childList: true, subtree: true }); }""") as demo:
    image_state = gr.State(None)
    debug_state = gr.State(debug)
    with gr.Row():
        image_input = gr.Image(sources=["upload"], type="pil", interactive=True, show_label=False, container=False)
    prompt = gr.Textbox(placeholder="Optional text prompt", label="", container=False)
    gen_btn = gr.Button("Vidioze")
    gr.Markdown("")
    history_html = gr.HTML()
    output = gr.HTML(label="")
    
    gen_btn.click(generate_video, inputs=[prompt, image_state, debug_state], outputs=[output, history_html])
    image_input.change(fn=lambda img: img, inputs=image_input, outputs=image_state)
    demo.load(update_history, outputs=history_html)

demo.queue()
demo.launch(server_name=server_name, server_port=server_port)
