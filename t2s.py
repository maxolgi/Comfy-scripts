import json
import aiohttp
import websockets
import asyncio
import uuid
from nicegui import ui, app
from datetime import datetime
import os
from starlette.middleware.sessions import SessionMiddleware
import os
import sys
import random

DEBUG = True

def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1)
    os.chdir("/")
    os.setsid()
    os.umask(0)
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1)
    sys.stdout.flush()
    sys.stderr.flush()
    si = open(os.devnull, 'r')
    so = open(os.devnull, 'a+')
    se = open(os.devnull, 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

# Full workflow API from t2s_api.json with additions
workflow_api = {
  "14": {
    "inputs": {
      "tags": "anime, cute female vocals, kawaii pop, j-pop, childish, piano, guitar, synthesizer, fast, happy, cheerful, lighthearted",
      "lyrics": "[verse]\nフワフワ　オミミガ\nユレルヨ　カゼノナカ\nキラキラ　アオイメ\nミツメル　セカイヲ\n\n[verse]\nフワフワ　シッポハ\nオオキク　ユレルヨ\nキンイロ　カミノケ\nナビクヨ　カゼノナカ\n\n[verse]\nコンフィーユーアイノ\nマモリビト\nピンクノ　セーターデ\nエガオヲ　クレルヨ\n\nアオイロ　スカートト\nクロイコート　キンノモヨウ\nヤサシイ　ヒカリガ\nツツムヨ　フェネックガール\n\n[verse]\nフワフワ　オミミデ\nキコエル　ココロノ　コエ\nダイスキ　フェネックガール\nイツデモ　ソバニイルヨ",
      "lyrics_strength": 0.9900000000000002,
      "clip": [
        "40",
        1
      ]
    },
    "class_type": "TextEncodeAceStepAudio"
  },
  "17": {
    "inputs": {
      "seconds": 120,
      "batch_size": 1
    },
    "class_type": "EmptyAceStepLatentAudio"
  },
  "18": {
    "inputs": {
      "samples": [
        "52",
        0
      ],
      "vae": [
        "40",
        2
      ]
    },
    "class_type": "VAEDecodeAudio"
  },
  "40": {
    "inputs": {
      "ckpt_name": "ace_step_v1_3.5b.safetensors"
    },
    "class_type": "CheckpointLoaderSimple"
  },
  "44": {
    "inputs": {
      "conditioning": [
        "14",
        0
      ]
    },
    "class_type": "ConditioningZeroOut"
  },
  "49": {
    "inputs": {
      "model": [
        "51",
        0
      ],
      "operation": [
        "50",
        0
      ]
    },
    "class_type": "LatentApplyOperationCFG"
  },
  "50": {
    "inputs": {
      "multiplier": 1.0000000000000002
    },
    "class_type": "LatentOperationTonemapReinhard"
  },
  "51": {
    "inputs": {
      "shift": 5.000000000000001,
      "model": [
        "40",
        0
      ]
    },
    "class_type": "ModelSamplingSD3"
  },
  "52": {
    "inputs": {
      "seed": 247844496912620,
      "steps": 50,
      "cfg": 5,
      "sampler_name": "euler",
      "scheduler": "simple",
      "denoise": 0.30000000000000004,
      "model": [
        "49",
        0
      ],
      "positive": [
        "14",
        0
      ],
      "negative": [
        "44",
        0
      ],
      "latent_image": [
        "17",
        0
      ]
    },
    "class_type": "KSampler"
  },
  "59": {
    "inputs": {
      "filename_prefix": "audio/ComfyUI",
      "quality": "V0",
      "audioUI": "",
      "audio": [
        "18",
        0
      ]
    },
    "class_type": "SaveAudioMP3"
  },
  "60": {
    "inputs": {
      "filename_prefix": "audio/ComfyUI",
      "audioUI": "",
      "audio": [
        "18",
        0
      ]
    },
    "class_type": "SaveAudio"
  },
  "61": {
    "inputs": {
      "filename_prefix": "audio/ComfyUI",
      "quality": "128k",
      "audioUI": "",
      "audio": [
        "18",
        0
      ]
    },
    "class_type": "SaveAudioOpus"
  },
  "64": {
    "inputs": {
      "audio": "Honey.wav",
      "audioUI": ""
    },
    "class_type": "LoadAudio"
  },
  "68": {
    "inputs": {
      "audio": [
        "64",
        0
      ],
      "vae": [
        "40",
        2
      ]
    },
    "class_type": "VAEEncodeAudio"
  },
  "76": {
    "inputs": {
      "seed": 840755638734093,
      "steps": 50,
      "cfg": 4.98,
      "sampler_name": "dpmpp_3m_sde_gpu",
      "scheduler": "exponential",
      "denoise": 1,
      "model": [
        "77",
        0
      ],
      "positive": [
        "78",
        0
      ],
      "negative": [
        "79",
        0
      ],
      "latent_image": [
        "81",
        0
      ]
    },
    "class_type": "KSampler"
  },
  "77": {
    "inputs": {
      "ckpt_name": "stable-audio-open-1.0.safetensors"
    },
    "class_type": "CheckpointLoaderSimple"
  },
  "78": {
    "inputs": {
      "text": "heaven church electronic dance music",
      "clip": [
        "80",
        0
      ]
    },
    "class_type": "CLIPTextEncode"
  },
  "79": {
    "inputs": {
      "text": "",
      "clip": [
        "80",
        0
      ]
    },
    "class_type": "CLIPTextEncode"
  },
  "80": {
    "inputs": {
      "clip_name": "t5-base.safetensors",
      "type": "stable_audio",
      "device": "default"
    },
    "class_type": "CLIPLoader"
  },
  "81": {
    "inputs": {
      "seconds": 47.6,
      "batch_size": 1
    },
    "class_type": "EmptyLatentAudio"
  },
  "82": {
    "inputs": {
      "samples": [
        "76",
        0
      ],
      "vae": [
        "77",
        2
      ]
    },
    "class_type": "VAEDecodeAudio"
  },
  "83": {
    "inputs": {
      "filename_prefix": "audio/ComfyUI",
      "audioUI": "",
      "audio": [
        "82",
        0
      ]
    },
    "class_type": "SaveAudio"
  },
  "84": {  # New negative conditioning for exclude
    "inputs": {
      "conditioning": ["78", 0]  # Link to positive for base, but override with negative tags
    },
    "class_type": "ConditioningZeroOut"
  },
  "85": {
    "inputs": {
      "filename_prefix": "audio/ComfyUI",
      "quality": "V0",
      "audioUI": "",
      "audio": [
        "82",
        0
      ]
    },
    "class_type": "SaveAudioMP3"
  },
  "86": {
    "inputs": {
      "filename_prefix": "audio/ComfyUI",
      "quality": "128k",
      "audioUI": "",
      "audio": [
        "82",
        0
      ]
    },
    "class_type": "SaveAudioOpus"
  }
}

server_address = '127.0.0.1:8188'

async def generate_audio(params, uploaded_audio=None, is_simple=False):
    client_id = str(uuid.uuid4())
    prompt = workflow_api.copy()
    
    # Conditional branches
    if is_simple:
        # Stable Audio branch for Simple mode
        prompt["78"]["inputs"]["text"] = params["prompt"]
        # Remove ACE-specific nodes
        del prompt["14"], prompt["44"], prompt["17"], prompt["51"], prompt["50"], prompt["49"], prompt["18"], prompt["59"], prompt["60"], prompt["61"], prompt["64"], prompt["68"]
        prompt["76"]["inputs"]["positive"] = ["78", 0]
        prompt["76"]["inputs"]["negative"] = ["79", 0]
        prompt["76"]["inputs"]["latent_image"] = ["81", 0]
        prompt["82"]["inputs"]["samples"] = ["76", 0]
        if params["format"] == "mp3":
            del prompt["83"], prompt["86"]
            prompt["85"]["inputs"]["filename_prefix"] = params["filename_prefix"]
            prompt["85"]["inputs"]["quality"] = params["quality"]
        elif params["format"] == "flac":
            del prompt["85"], prompt["86"]
            prompt["83"]["inputs"]["filename_prefix"] = params["filename_prefix"]
        elif params["format"] == "opus":
            del prompt["83"], prompt["85"]
            prompt["86"]["inputs"]["filename_prefix"] = params["filename_prefix"]
            prompt["86"]["inputs"]["quality"] = params["quality"]
    else:
        # ACE-Step base
        prompt["14"]["inputs"]["tags"] = params["tags"]
        prompt["14"]["inputs"]["lyrics"] = params["lyrics"]
        prompt["14"]["inputs"]["lyrics_strength"] = params["lyrics_strength"]
        prompt["17"]["inputs"]["seconds"] = params["seconds"]
        prompt["17"]["inputs"]["batch_size"] = params["batch_size"]
        prompt["51"]["inputs"]["shift"] = params["shift"]
        prompt["50"]["inputs"]["multiplier"] = params["vocal_volume"]  # Vocal volume
        prompt["52"]["inputs"]["seed"] = random.randint(0, 2**64 - 1) if params["denoise"] == 1 else params["seed"]
        prompt["52"]["inputs"]["steps"] = params["steps"]
        prompt["52"]["inputs"]["cfg"] = params["cfg"]
        prompt["52"]["inputs"]["sampler_name"] = params["sampler_name"]
        prompt["52"]["inputs"]["scheduler"] = params["scheduler"]
        prompt["52"]["inputs"]["denoise"] = params["denoise"]
        
        # Repaint if audio uploaded
        if uploaded_audio:
            prompt["64"]["inputs"]["audio"] = uploaded_audio
            prompt["52"]["inputs"]["latent_image"] = ["68", 0]
            prompt["52"]["inputs"]["denoise"] = 0.3  # Default for repaint
        
        # Negative for exclude
        if params["exclude_styles"]:
            prompt["79"]["inputs"]["text"] = params["exclude_styles"]
            prompt["52"]["inputs"]["negative"] = ["84", 0]  # Use new negative

        # Delete unused save nodes
        if params["format"] == "mp3":
            del prompt["60"], prompt["61"]
            prompt["59"]["inputs"]["filename_prefix"] = params["filename_prefix"]
            prompt["59"]["inputs"]["quality"] = params["quality"]
        elif params["format"] == "flac":
            del prompt["59"], prompt["61"]
            prompt["60"]["inputs"]["filename_prefix"] = params["filename_prefix"]
        elif params["format"] == "opus":
            del prompt["59"], prompt["60"]
            prompt["61"]["inputs"]["filename_prefix"] = params["filename_prefix"]
            prompt["61"]["inputs"]["quality"] = params["quality"]

    # Queue and fetch as before
    async with aiohttp.ClientSession() as session:
        if DEBUG:
            print("POST /prompt:", json.dumps({"prompt": prompt, "client_id": client_id}))
        async with session.post(f"http://{server_address}/prompt", json={"prompt": prompt, "client_id": client_id}) as response:
            if DEBUG:
                print("POST /prompt response status:", response.status)
            if response.status != 200:
                text = await response.text()
                if DEBUG:
                    print("POST /prompt error text:", text)
                raise ValueError(f"Error queuing prompt: {text}")
            data = await response.json()
            if DEBUG:
                print("POST /prompt response data:", data)
            prompt_id = data.get("prompt_id")
            if prompt_id is None:
                raise KeyError("'prompt_id' not in response")
    
    async with websockets.connect(f"ws://{server_address}/ws?clientId={client_id}") as ws:
        while True:
            msg = json.loads(await ws.recv())
            if DEBUG:
                print("WS recv:", msg)
            if msg['type'] == 'progress' and msg['data']['prompt_id'] == prompt_id:
                percent = int(100 * msg['data']['value'] / msg['data']['max'])
                params['progress'].text = f'Generating... {percent}%'
            if msg['type'] == 'executed' and msg['data']['prompt_id'] == prompt_id:
                break
    
    async with aiohttp.ClientSession() as session:
        history = None
        for attempt in range(30):
            if DEBUG:
                print("GET /history/", prompt_id, f"attempt {attempt+1}")
            async with session.get(f"http://{server_address}/history/{prompt_id}") as response:
                if DEBUG:
                    print("GET /history response status:", response.status)
                try:
                    full_history = await response.json()
                    if DEBUG:
                        print("GET /history full json:", full_history)
                    if prompt_id in full_history:
                        history = full_history[prompt_id]
                        break
                except Exception as e:
                    if DEBUG:
                        print("History fetch error:", str(e))
            await asyncio.sleep(1)
        if history is None:
            raise ValueError(f"History for prompt_id {prompt_id} not found after 30 attempts")

    node_id = {
        'mp3': '59' if not is_simple else '85',
        'flac': '60' if not is_simple else '83',
        'opus': '61' if not is_simple else '86'
    }[params["format"]]
    output_audio = history["outputs"][node_id]["audio"][0]
    filename = output_audio["filename"]
    subfolder = output_audio.get("subfolder", "")
    type_ = output_audio.get("type", "output")
    audio_url = f"http://{server_address}/view?filename={filename}&type={type_}&subfolder={subfolder}"
    async with aiohttp.ClientSession() as session:
        if DEBUG:
            print("GET /view:", audio_url)
        async with session.get(audio_url) as resp:
            if DEBUG:
                print("GET /view response status:", resp.status)
            audio_content = await resp.read()
    os.makedirs('media', exist_ok=True)
    path = os.path.join('media', filename)
    with open(path, 'wb') as f:
        f.write(audio_content)
    return filename

app.add_static_files('/media', 'media')

@ui.page('/')
async def main():
    with ui.row().classes('w-full h-screen'):
        # Main content
        with ui.column().classes('w-full bg-gray-900 p-4'):
            tabs = ui.tabs().classes('w-full')
            with tabs:
                ui.tab('Simple')
                ui.tab('Custom')
            panels = ui.tab_panels(tabs, value='Custom').classes('w-full')  # Default to Custom
            with panels:
                with ui.tab_panel('Simple'):
                    simple_prompt = ui.textarea(placeholder='Describe your song').classes('w-full bg-gray-800 text-white')
                    async def simple_submit():
                        simple_progress.text = 'Generating... 0%'
                        simple_download_button.style('visibility: hidden')
                        try:
                            params = {
                                "prompt": simple_prompt.value,
                                "format": simple_format_select.value,
                                "filename_prefix": "audio/ComfyUI",
                                "quality": "320k"
                            }
                            params['progress'] = simple_progress
                            filename = await generate_audio(params, is_simple=True)
                            app.storage.user['filename'] = filename
                            simple_progress.text = 'Done - Ready to download'
                            simple_download_button.style('visibility: visible')
                        except Exception as e:
                            simple_progress.text = f'Error: {str(e)}'
                    async def simple_download():
                        filename = app.storage.user.get('filename')
                        if filename:
                            download_url = f'/media/{filename}'
                            await ui.run_javascript(f'''
                                fetch('{download_url}')
                                  .then(response => response.blob())
                                  .then(blob => {{
                                    const url = window.URL.createObjectURL(blob);
                                    const link = document.createElement('a');
                                    link.href = url;
                                    link.download = '{filename}';
                                    document.body.appendChild(link);
                                    link.click();
                                    document.body.removeChild(link);
                                    window.URL.revokeObjectURL(url);
                                  }});
                            ''')
                    async def simple_cancel():
                        simple_progress.text = 'Cancelling...'
                        async with aiohttp.ClientSession() as session:
                            await session.post(f"http://{server_address}/interrupt")
                        simple_progress.text = 'Cancelled'
                    with ui.row():
                        simple_download_button = ui.button('Download').classes('bg-orange-500 text-white').style('visibility: hidden')
                        simple_download_button.on_click(simple_download)
                        simple_format_select = ui.select(['mp3', 'flac', 'opus'], value='flac', label='Format')
                        simple_button = ui.button('Create').classes('bg-orange-500 text-white')
                        simple_button.on_click(simple_submit)
                    simple_progress = ui.label('Ready').classes('text-white')
                with ui.tab_panel('Custom'):
                    async def submit():
                        progress.text = 'Generating... 0%'
                        download_button.style('visibility: hidden')
                        custom_button.props('text=Cancel')
                        custom_button.on_click(cancel)
                        try:
                            uploaded_path = uploaded_path if 'uploaded_path' in globals() else None
                            tags_val = tags.value
                            if vocal_gender.value:
                                tags_val += f", {vocal_gender.value.lower()} vocals"
                            params = {
                                "seconds": seconds.value,
                                "batch_size": int(batch_size.value),
                                "tags": tags_val,
                                "lyrics": lyrics.value,
                                "lyrics_strength": 0 if instrumental.value else lyrics_strength.value,
                                "shift": shift.value,
                                "vocal_volume": vocal_volume.value / 50.0,  # Remap 0-100 to 0-2
                                "multiplier": multiplier.value,
                                "seed": int(seed.value),
                                "steps": int(steps.value),
                                "cfg": weirdness.value / 5.0,
                                "sampler_name": sampler_name.value,
                                "scheduler": scheduler.value,
                                "denoise": 1 if song_mode.value == 'Full Song' else 0.3,
                                "filename_prefix": filename_prefix.value,
                                "quality": quality.value,
                                "exclude_styles": exclude_styles.value,
                                "format": format_select.value
                            }
                            params['progress'] = progress
                            filename = await generate_audio(params, uploaded_path)
                            app.storage.user['filename'] = filename
                            progress.text = 'Done - Ready to download'
                            download_button.style('visibility: visible')
                        except Exception as e:
                            progress.text = f'Error: {str(e)}'
                        finally:
                            custom_button.props('text=Create')
                            custom_button.on_click(submit)
                    async def download():
                        filename = app.storage.user.get('filename')
                        if filename:
                            download_url = f'/media/{filename}'
                            await ui.run_javascript(f'''
                                fetch('{download_url}')
                                  .then(response => response.blob())
                                  .then(blob => {{
                                    const url = window.URL.createObjectURL(blob);
                                    const link = document.createElement('a');
                                    link.href = url;
                                    link.download = '{filename}';
                                    document.body.appendChild(link);
                                    link.click();
                                    document.body.removeChild(link);
                                    window.URL.revokeObjectURL(url);
                                  }});
                            ''')
                    async def cancel():
                        progress.text = 'Cancelling...'
                        async with aiohttp.ClientSession() as session:
                            await session.post(f"http://{server_address}/interrupt")
                        progress.text = 'Cancelled'
                        custom_button.props('text=Create')
                        custom_button.on_click(submit)
                    with ui.row().classes('w-full justify-between'):
                        with ui.row():
                            async def handle_upload(e: ui.upload.on_upload):
                                global uploaded_path
                                os.makedirs('uploads', exist_ok=True)
                                filename = e.name
                                with open(f'uploads/{filename}', 'wb') as f:
                                    f.write(e.content.read())
                                uploaded_path = f'uploads/{filename}'
                                ui.notify('Audio uploaded')
                            audio_upload = ui.upload(on_upload=handle_upload).classes('bg-gray-800 text-white')
                            ui.button('+ Persona').classes('bg-gray-800 text-white')
                            ui.button('+ Inspo').classes('bg-gray-800 text-white')
                        with ui.column().classes('items-end'):
                            with ui.row().classes('justify-end'):
                                progress = ui.label('Ready').classes('text-white text-right')
                            with ui.row():
                                download_button = ui.button('Download').classes('bg-orange-500 text-white').style('visibility: hidden')
                                download_button.on_click(download)
                                custom_button = ui.button('Create').classes('bg-orange-500 text-white')
                                custom_button.on_click(submit)
                            with ui.row().classes('justify-end'):
                                filename_prefix = ui.input(label='Filename Prefix', value="audio/ComfyUI")
                                format_select = ui.select(['mp3', 'flac', 'opus'], value='mp3', label='Format')
                                quality = ui.select(['128k', '192k', '256k', '320k', 'V0'], value='320k', label='Quality')
                    ui.label('♪ Lyrics').classes('text-white')
                    lyrics = ui.textarea(placeholder='Add your own lyrics here', value=workflow_api["14"]["inputs"]["lyrics"]).classes('w-full bg-gray-800 text-white')
                    with ui.row():
                        ui.button('Auto').classes('bg-gray-800 text-white')  # Non-functional
                        ui.button('Write Lyrics').classes('bg-gray-800 text-white')  # Non-functional
                        seconds = ui.number(label='Seconds', value=60)
                        lyrics_strength = ui.number(label='Lyrics Strength', value=0.99, format='%.2f')
                        instrumental = ui.switch('Instrumental').classes('text-white')
                        song_mode = ui.radio(['By Line', 'Full Song'], value='Full Song').classes('text-white')
                    ui.label('♪ Styles').classes('text-white')
                    tags = ui.textarea(placeholder='Enter style tags', value=workflow_api["14"]["inputs"]["tags"]).classes('w-full bg-gray-800 text-white')
                    with ui.row().classes('flex-wrap'):
                        ui.button('break up', on_click=lambda: tags.set_value(tags.value + ' break up')).classes('bg-gray-700 text-white rounded-full m-1')
                        ui.button('country', on_click=lambda: tags.set_value(tags.value + ' country')).classes('bg-gray-700 text-white rounded-full m-1')
                        ui.button('jazz', on_click=lambda: tags.set_value(tags.value + ' jazz')).classes('bg-gray-700 text-white rounded-full m-1')
                        ui.button('dramatic layered soundscape', on_click=lambda: tags.set_value(tags.value + ' dramatic layered soundscape')).classes('bg-gray-700 text-white rounded-full m-1')
                        ui.button('orchestra strings', on_click=lambda: tags.set_value(tags.value + ' orchestra strings')).classes('bg-gray-700 text-white rounded-full m-1')
                        ui.button('exp', on_click=lambda: tags.set_value(tags.value + ' exp')).classes('bg-gray-700 text-white rounded-full m-1')
                    # Advanced Options
                    advanced_expansion = ui.expansion('Advanced Options').classes('w-full bg-gray-800 text-white')
                    with advanced_expansion:
                        exclude_styles = ui.input(label='Exclude styles', placeholder='Enter styles to exclude').classes('w-full')
                        vocal_gender = ui.select(['Male', 'Female'], value='Female', label='Vocal Gender').classes('w-full')
                        ui.label('Weirdness').classes('text-white')
                        weirdness = ui.slider(min=0, max=100, value=50).classes('w-full')
                        ui.label('Style Influence').classes('text-white')
                        style_influence = ui.slider(min=0, max=100, value=50).classes('w-full')
                        ui.label('Vocal Volume').classes('text-white')
                        vocal_volume = ui.slider(min=0, max=100, value=50).classes('w-full')
                        with ui.row():
                            batch_size = ui.number(label='Batch Size', value=1)
                            shift = ui.number(label='Shift', value=5.0, format='%.1f')
                        with ui.row():
                            multiplier = ui.number(label='Multiplier', value=1.0, format='%.1f')
                            seed = ui.number(label='Seed', value=810270844734026)
                            steps = ui.number(label='Steps', value=50)
                            cfg = ui.number(label='CFG', value=5)
                        with ui.row():
                            sampler_name = ui.select(['euler', 'euler_ancestral', 'heun', 'heunpp2', 'dpm_2', 'dpm_2_ancestral', 'lms', 'dpm_fast', 'dpm_adaptive', 'dpmpp_2s_ancestral', 'dpmpp_sde', 'dpmpp_sde_gpu', 'dpmpp_2m', 'dpmpp_2m_sde', 'dpmpp_2m_sde_gpu', 'dpmpp_3m_sde', 'dpmpp_3m_sde_gpu', 'ddpm', 'lcm', 'ipndm', 'ipndm_v', 'deis', 'ddim', 'uni_pc', 'uni_pc_bh2'], value='euler', label='Sampler Name')
                            scheduler = ui.select(['normal', 'karras', 'exponential', 'sgm_uniform', 'simple', 'ddim_uniform'], value='simple', label='Scheduler')
                            denoise = ui.number(label='Denoise', value=1)

app.add_middleware(SessionMiddleware, secret_key='your_secret_key')
if sys.platform != 'win32':
    daemonize()
ui.run(dark=True)
