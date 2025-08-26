import json
import aiohttp
import websockets
import asyncio
import uuid
from nicegui import ui, app
from datetime import datetime
import os
from starlette.middleware.sessions import SessionMiddleware

# API format workflow (converted from provided graph JSON)
workflow_api = {
    "40": {
        "inputs": {"ckpt_name": "ace_step_v1_3.5b.safetensors"},
        "class_type": "CheckpointLoaderSimple"
    },
    "17": {
        "inputs": {"seconds": 120, "batch_size": 1},
        "class_type": "EmptyAceStepLatentAudio"
    },
    "14": {
        "inputs": {
            "tags": "hip hop, soft female vocals, piano, guitar, synthesizer, fast, happy, cheerful, lighthearted\t\n",
            "lyrics": "[Verse 1] Fluffy little ears They sway in the blowing breeze Sparkling, bright blue eyes Gazing at the world they see\n\n[Verse 2] A fluffy, swaying tail Moves wide with every beat Golden strands of hair Flowing in the wind so sweet\n\n[Verse 3] Guardian of Comfy You-I Wrapped in a pink sweater’s cheer With a smile you always bring Keeping everyone near\n\nBlue skirt, black coat traced in gold Soft light wraps around your world In its glow you shine so warm Our gentle Fennec Girl\n\n[Verse 4] With those fluffy ears You can hear the heart’s true sound Dearest Fennec Girl You’re always close, always around",
            "lyrics_strength": 0.9900000000000002,
            "clip": ["40", 1]
        },
        "class_type": "TextEncodeAceStepAudio"
    },
    "44": {
        "inputs": {"conditioning": ["14", 0]},
        "class_type": "ConditioningZeroOut"
    },
    "51": {
        "inputs": {"model": ["40", 0], "shift": 5.000000000000001},
        "class_type": "ModelSamplingSD3"
    },
    "50": {
        "inputs": {"multiplier": 1.0000000000000002},
        "class_type": "LatentOperationTonemapReinhard"
    },
    "49": {
        "inputs": {"model": ["51", 0], "operation": ["50", 0]},
        "class_type": "LatentApplyOperationCFG"
    },
    "52": {
        "inputs": {
            "model": ["49", 0],
            "positive": ["14", 0],
            "negative": ["44", 0],
            "latent_image": ["17", 0],
            "seed": 810270844734026,
            "steps": 50,
            "cfg": 5,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 1
        },
        "class_type": "KSampler"
    },
    "18": {
        "inputs": {"samples": ["52", 0], "vae": ["40", 2]},
        "class_type": "VAEDecodeAudio"
    },
    "59": {
        "inputs": {"audio": ["18", 0], "filename_prefix": "audio/ComfyUI", "quality": "320k"},
        "class_type": "SaveAudioMP3"
    }
    # Note: Other nodes like 60,61 bypassed; 64,68 for repainting (disabled); 48,73 notes
}

server_address = '127.0.0.1:8188'

async def generate_audio(params):
    client_id = str(uuid.uuid4())
    prompt = workflow_api.copy()
    
    # Update params
    prompt["17"]["inputs"]["seconds"] = params["seconds"]
    prompt["17"]["inputs"]["batch_size"] = params["batch_size"]
    prompt["14"]["inputs"]["tags"] = params["tags"]
    prompt["14"]["inputs"]["lyrics"] = params["lyrics"]
    prompt["14"]["inputs"]["lyrics_strength"] = params["lyrics_strength"]
    prompt["51"]["inputs"]["shift"] = params["shift"]
    prompt["50"]["inputs"]["multiplier"] = params["multiplier"]
    prompt["52"]["inputs"]["seed"] = params["seed"]
    prompt["52"]["inputs"]["steps"] = params["steps"]
    prompt["52"]["inputs"]["cfg"] = params["cfg"]
    prompt["52"]["inputs"]["sampler_name"] = params["sampler_name"]
    prompt["52"]["inputs"]["scheduler"] = params["scheduler"]
    prompt["52"]["inputs"]["denoise"] = params["denoise"]
    prompt["59"]["inputs"]["filename_prefix"] = params["filename_prefix"]
    prompt["59"]["inputs"]["quality"] = params["quality"]
    
    # Queue prompt
    async with aiohttp.ClientSession() as session:
        async with session.post(f"http://{server_address}/prompt", json={"prompt": prompt, "client_id": client_id}) as response:
            if response.status != 200:
                text = await response.text()
                print(text)
                raise ValueError(f"Error queuing prompt: {text}")
            data = await response.json()
            if "prompt_id" not in data:
                print(data)
                raise KeyError("'prompt_id' not in response")
            prompt_id = data["prompt_id"]
    
    # WS monitor
    async with websockets.connect(f"ws://{server_address}/ws?clientId={client_id}") as ws:
        while True:
            msg = json.loads(await ws.recv())
            if msg['type'] == 'executed' and msg['data']['prompt_id'] == prompt_id:
                break
    
    # Get history, extract filename
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{server_address}/history/{prompt_id}") as response:
            history = (await response.json())[prompt_id]
    output_audio = history["outputs"]["59"]["audio"][0]
    filename = output_audio["filename"]
    subfolder = output_audio.get("subfolder", "")
    type_ = output_audio.get("type", "output")
    audio_url = f"http://{server_address}/view?filename={filename}&type={type_}&subfolder={subfolder}"
    async with aiohttp.ClientSession() as session:
        async with session.get(audio_url) as resp:
            audio_content = await resp.read()
    return audio_content, filename

app.add_static_files('/media', 'media')

@ui.page('/')
async def main():
    tabs = ui.tabs().classes('w-full')
    with tabs:
        ui.tab('Tab 1')
        ui.tab('Tab 2')
        ui.tab('Tab 3')
        ui.tab('Tab 4')
        ui.tab('Tab 5')
        ui.tab('Tab 6')
    panels = ui.tab_panels(tabs, value='Tab 1').classes('w-full')
    with panels:
        with ui.tab_panel('Tab 1'):
            
            
            async def submit():
                progress.text = 'Generating...'
                try:
                    params = {
                        "seconds": seconds.value,
                        "batch_size": int(batch_size.value),
                        "tags": tags.value,
                        "lyrics": lyrics.value,
                        "lyrics_strength": lyrics_strength.value,
                        "shift": shift.value,
                        "multiplier": multiplier.value,
                        "seed": int(seed.value),
                        "steps": int(steps.value),
                        "cfg": cfg.value,
                        "sampler_name": sampler_name.value,
                        "scheduler": scheduler.value,
                        "denoise": denoise.value,
                        "filename_prefix": filename_prefix.value,
                        "quality": quality.value
                    }
                    audio_content, filename = await generate_audio(params)
                    os.makedirs('media', exist_ok=True)
                    path = os.path.join('media', filename)
                    with open(path, 'wb') as f:
                        f.write(audio_content)
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
                    progress.text = 'Done'
                except Exception as e:
                    progress.text = f'Error: {str(e)}'
            
            with ui.row().classes('h-[600px] w-full'):
                with ui.column().classes('w-1/4 h-full'):
                    lyrics = ui.textarea(label='Lyrics', value="[Verse 1] Fluffy little ears They sway in the blowing breeze Sparkling, bright blue eyes Gazing at the world they see\n\n[Verse 2] A fluffy, swaying tail Moves wide with every beat Golden strands of hair Flowing in the wind so sweet\n\n[Verse 3] Guardian of Comfy You-I Wrapped in a pink sweater’s cheer With a smile you always bring Keeping everyone near\n\nBlue skirt, black coat traced in gold Soft light wraps around your world In its glow you shine so warm Our gentle Fennec Girl\n\n[Verse 4] With those fluffy ears You can hear the heart’s true sound Dearest Fennec Girl You’re always close, always around").classes('w-full h-full')
                with ui.column().classes('w-1/2 h-full'):
                    tags = ui.textarea(label='Tags', value="hip hop, soft female vocals, piano, guitar, synthesizer, fast, happy, cheerful, lighthearted\t\n").classes('w-full h-[25vh]')
                    with ui.row():
                        ui.button('Generate', on_click=submit)
                        progress = ui.label('Ready')
                    with ui.row():
                        seconds = ui.number(label='Seconds', value=120)
                        filename_prefix = ui.input(label='Filename Prefix', value="audio/ComfyUI")
                        quality = ui.select(['320k', 'other_qualities...'], value='320k', label='Quality')
                        lyrics_strength = ui.number(label='Lyrics Strength', value=0.99, format='%.2f')
                    with ui.row():
                        batch_size = ui.number(label='Batch Size', value=1)
                        shift = ui.number(label='Shift', value=5.0, format='%.1f')
                        multiplier = ui.number(label='Multiplier', value=1.0, format='%.1f')
                        seed = ui.number(label='Seed', value=810270844734026)
                        steps = ui.number(label='Steps', value=50)
                        cfg = ui.number(label='CFG', value=5)
                        sampler_name = ui.select(['euler', 'other_samplers...'], value='euler', label='Sampler Name')  # Add options as needed
                        scheduler = ui.select(['simple', 'other_schedulers...'], value='simple', label='Scheduler')
                        denoise = ui.number(label='Denoise', value=1)
        with ui.tab_panel('Tab 2'):
            ui.label('Content for Tab 2')
        with ui.tab_panel('Tab 3'):
            ui.label('Content for Tab 3')
        with ui.tab_panel('Tab 4'):
            ui.label('Coming soon')
        with ui.tab_panel('Tab 5'):
            ui.label('Coming soon')
        with ui.tab_panel('Tab 6'):
            ui.label('Coming soon')

app.add_middleware(SessionMiddleware, secret_key='your_secret_key')
ui.run(dark=True)
