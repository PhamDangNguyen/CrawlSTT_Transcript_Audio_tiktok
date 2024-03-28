from utils import download_audio
from concurrent.futures import ThreadPoolExecutor


output_path='audio_mien_trung'
with open('tiktok_urls.txt', 'r') as f:
    video_urls = [url.replace('\n', '').strip() for url in f if url.replace('\n', '').strip()]

# print(video_urls[0])

with ThreadPoolExecutor(max_workers=2) as executor:
    executor.map(download_audio, [(url, output_path) for url in video_urls])