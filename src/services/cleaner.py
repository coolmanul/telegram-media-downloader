import os, asyncio

async def cleanup(files):
    for f in files:
        if os.path.exists(f):
            await asyncio.sleep(2)
            try: os.remove(f)
            except: pass