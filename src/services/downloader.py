import os, yt_dlp, asyncio, aiohttp
from config import TEMP_DIR


async def check_tiktok_video(url):
    opts = {
        'quiet': True, 'no_warnings': True,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'ignore_no_formats': True
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=False)
            return bool(info and (info.get('ext') or info.get('formats')))
    except Exception:
        return False


async def check_tiktok_photos(url):
    api_url = f"https://www.tikwm.com/api/?url={url}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    return False
                data = await resp.json()

        if data.get('code') != 0 or not data.get('data'):
            return False

        images = data['data'].get('images', [])
        return bool(images)
    except Exception:
        return False


async def download_tiktok_video(url):
    opts = {
        'outtmpl': f'{TEMP_DIR}/%(id)s.%(ext)s',
        'quiet': True, 'no_warnings': True,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}]
    }

    files = []
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=False)
            if not info: return []

            await asyncio.to_thread(ydl.download, [url])

            target_id = info.get('id', '')
            for fname in os.listdir(TEMP_DIR):
                if target_id and target_id in fname and fname.endswith(('.mp4', '.webm')):
                    files.append(os.path.join(TEMP_DIR, fname))
            return files
    except Exception:
        return []


async def download_tiktok_photos(url):
    api_url = f"https://www.tikwm.com/api/?url={url}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()

        if data.get('code') != 0 or not data.get('data'):
            return []

        images = data['data'].get('images', [])
        if not images:
            return []

        post_id = data['data'].get('id', 'unknown')
        downloaded_files = []

        for idx, img_url in enumerate(images, 1):
            filename = f"photo-{post_id}-{idx}.jpg"
            filepath = os.path.join(TEMP_DIR, filename)

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(img_url) as img_resp:
                        if img_resp.status == 200:
                            with open(filepath, 'wb') as f:
                                f.write(await img_resp.read())
                            downloaded_files.append(filepath)
            except Exception:
                continue

        return downloaded_files

    except Exception:
        return []