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
parser.add_argument("--max_history_videos", type=int, default=10, help="Maximum number of history videos to display")
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
      "text": "ransform any static input image into a vibrant lively, action-packed scene generate a dynamic video. add objects and props according to the context",
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
      "steps": 4,
      "cfg": 1,
      "sampler_name": "euler",
      "scheduler": "simple",
      "start_at_step": 0,
      "end_at_step": 2,
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
      "steps": 4,
      "cfg": 1,
      "sampler_name": "euler",
      "scheduler": "simple",
      "start_at_step": 2,
      "end_at_step": 4,
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

ORIGINAL_POSITIVE = workflow["20"]["inputs"]["text"]

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
    for url in video_urls:
        html += f'<video controls autoplay="false" preload="none" src="{url}" style="max-width: 100%; margin-bottom: 10px;"></video>'
    html += '</div>'
    return html

def update_history():
    video_urls = get_all_videos(max_history_videos)
    return render_video_list(video_urls)

def generate_video(prompt, image, fire=False, water=False, fun=False, dance=False, debug=False, resolution="320x480", negative_prompt=""):
    if image is None:
        return "", None
    
    try:
        # Determine resolution
        if resolution == "320x480":
            width, height = 320, 480
        elif resolution == "464x688":
            width, height = 464, 688
        elif resolution == "1280x720":
            width, height = 1280, 720
        elif resolution == "1920x1080":
            width, height = 1920, 1080
        else:
            width, height = 320, 480
        
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
        fixed_positive = ORIGINAL_POSITIVE
        FIRE_PROMPT = "From any static input image, generate a dynamic video that adds realistic intense, roaring orange and red flames to all prominent objects. Ignite every visible element—whether structures, vehicles, furniture, or natural features—with vivid, crackling fire that spreads rapidly, producing thick black smoke and swirling embers. Animate the flames to leap and dance across surfaces, with sparks flying and heat distortion warping the air. Use dynamic camera movements: zoom in on burning details, pan across the spreading inferno, and tilt up to show flames against the sky. Emphasize a chaotic, thrilling vibe with sounds of crackling fire, shattering materials, and occasional explosive pops. Ensure every object is engulfed in intense, fiery destruction, creating a wild, universal spectacle of flame and motion."
        WATER_PROMPT = "Make where all prominent objects—whether buildings, trees, vehicles, furniture, or anything else—are dynamically drenched in water in playful, varied ways. Animate torrents of sparkling blue water cascading over objects, leaving them glistening as if caught in a sudden downpour. Make some objects drip with gentle streams, others get splashed with wild, frothy waves, and some shimmer with mist or bubbles clinging to their surfaces. Add dynamic effects like rippling puddles forming at the base of objects, rainbow-reflecting droplets flying through the air, and swirling water trails looping around moving elements. Use lively camera angles: zoom in on water splashing across an object’s surface, pan through a scene of gushing streams, and pull back to reveal a soaked, glistening world. Infuse a whimsical, energetic atmosphere with sounds of rushing water, bubbly gurgles, and cheerful splashes, creating a augh-out-loud spectacle where everything is delightfully drenched in a dazzling dance of water."
        FUN_PROMPT = "bursting with whimsical energy. Animate all prominent objects—whether buildings, trees, cars, furniture, or anything else—to bounce, spin, and twirl with exaggerated, cartoonish glee, glowing with vibrant neon colors like pink, teal, and yellow. Add playful effects like sparkling confetti raining down, glittering starbursts popping around objects, and rainbow trails following their movements. Bring the scene to life with dynamic camera angles: zoom in on a dancing object, swoop through the chaos like a roller coaster, and pull back to reveal a vibrant, dreamlike world pulsing with energy. Infuse a joyful, atmosphere with sounds of cartoonish boings, upbeat bubblegum music, and occasional giggly sound effects. Make every object move with infectious, over-the-top excitement, creating a laugh-out-loud, imaginative spectacle that feels like a whimsical fever dream of pure fun. Use dynamic camera angles: zoom in on a person’s smooth dance moves, pan across objects twirling in unison, and pull back to reveal a joyful, dance-filled world. Infuse a fun, atmosphere, creating a laugh-out-loud, high-energy spectacle"
        DANCE_PROMPT = "they all dance together people and objects burst into dynamic, playful dance movements. Animate  elements to groove with unique, whimsical dance styles, trees sway rhythmically like they’re in a breeze, and objects like cars or furniture bounce and spin with cartoonish energy. Add vibrant effects like glowing neon trails following their movements, sparkling confetti bursting around them, and colorful light pulses syncing to the beat. Use dynamic camera angles: zoom in on a person’s smooth dance moves, pan across objects twirling in unison, and pull back to reveal a joyful, dance-filled world. Infuse a fun, atmosphere, creating a laugh-out-loud, high-energy spectacle where everything dances in a dazzling, rhythmic celebration."
        extras = []
        if fire:
            extras.append(FIRE_PROMPT)
        if water:
            extras.append(WATER_PROMPT)
        if fun:
            extras.append(FUN_PROMPT)
        if dance:
            extras.append(DANCE_PROMPT)
        effective_positive = (prompt + " " if prompt else "") + " ".join(extras) + (" " if extras else "") + fixed_positive
        workflow["20"]["inputs"]["text"] = effective_positive
        fixed_negative = "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走, NSFW, adding people and actors thatwere not requested"
        effective_negative = (negative_prompt + " " if negative_prompt else "") + fixed_negative
        workflow["9"]["inputs"]["text"] = effective_negative
        prefix = f"video/Gradio_{int(time.time())}"
        workflow["15"]["inputs"]["filename_prefix"] = prefix
        workflow["14:1369"]["inputs"]["noise_seed"] = random.randint(0, 2**64 - 1)
        workflow["14:1373"]["inputs"]["width"] = width
        workflow["14:1373"]["inputs"]["height"] = height
        
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
            url =f"{COMFYUI_URL}/history/{prompt_id}"
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
        new_video_html = ""
        
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
    negative_prompt = gr.Textbox(placeholder="Optional negative text prompt", label="", container=False)
    with gr.Row():
        fire_checkbox = gr.Checkbox(label="Fire")
        water_checkbox = gr.Checkbox(label="Water")
        fun_checkbox = gr.Checkbox(label="Fun")
        dance_checkbox = gr.Checkbox(label="Dance")
    with gr.Row():
        resolution = gr.Radio(choices=["320x480", "464x688", "1280x720", "1920x1080"], value="320x480", label="Resolution")
    gen_btn = gr.Button("vyidd")
    gr.Markdown("")
    history_html = gr.HTML()
    output = gr.HTML(label="")
    
    gen_btn.click(generate_video, inputs=[prompt, image_state, fire_checkbox, water_checkbox, fun_checkbox, dance_checkbox, debug_state, resolution, negative_prompt], outputs=[output, history_html])
    image_input.change(fn=lambda img: img, inputs=image_input, outputs=image_state)
    demo.load(update_history, outputs=history_html)

demo.queue()
demo.launch(server_name=server_name, server_port=server_port)
