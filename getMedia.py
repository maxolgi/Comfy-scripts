import requests
import os
import time
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

server_url = sys.argv[1]
download_dir = "downloaded_renders"
poll_interval = 1  # seconds

os.makedirs(download_dir, exist_ok=True)
downloaded = set()  # Track (filename, subfolder, typ) tuples

# Setup retry session
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

print("Monitoring for new media... Press Ctrl+C to stop.")

while True:
    try:
        # Fetch history
        history_response = session.get(f"{server_url}/history")
        history = history_response.json()

        # Collect current media
        current_media = set()
        for prompt_data in history.values():
            if 'outputs' in prompt_data:
                for node_output in prompt_data['outputs'].values():
                    for key, value in node_output.items():
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict) and 'filename' in item:
                                    fn = item['filename']
                                    sub = item.get('subfolder', '')
                                    typ = item.get('type', 'output')
                                    current_media.add((fn, sub, typ))

        # Download new ones
        new_media = current_media - downloaded
        for filename, subfolder, typ in new_media:
            file_path = os.path.join(download_dir, filename)
            if os.path.exists(file_path):
                print(f"Skipped (already exists): {filename}")
                downloaded.add((filename, subfolder, typ))
                continue
            params = {'filename': filename, 'type': typ, 'subfolder': subfolder}
            response = session.get(f"{server_url}/view", params=params, stream=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Downloaded: {filename}")
                downloaded.add((filename, subfolder, typ))
            else:
                print(f"Failed: {filename} (status: {response.status_code}, reason: {response.reason})")

        time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("Stopped monitoring.")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(poll_interval)
