import os, asyncio, re
from aiogram import Router, F
from aiogram.types import Message, FSInputFile, InputMediaPhoto
from services.downloader import (
    check_tiktok_video, check_tiktok_photos,
    download_tiktok_video, download_tiktok_photos
)
from services.cleaner import cleanup

router = Router()

@router.message(F.text.regexp(r'https?://\S*tiktok\.com\S*'))
async def handle_tiktok_link(message: Message):
    match = re.search(r'https?://\S*tiktok\.com\S*', message.text)
    if not match:
        return

    url = match.group(0).strip()

    if await check_tiktok_video(url):
        status_msg = await message.answer("⏳")
        files = await download_tiktok_video(url)

        if files:
            await message.answer_video(
                video=FSInputFile(files[0]),
                reply_to_message_id=message.message_id
            )
            await status_msg.delete()
            asyncio.create_task(cleanup(files))
        else:
            await status_msg.delete()
        return

    if await check_tiktok_photos(url):
        status_msg = await message.answer("⏳")
        files = await download_tiktok_photos(url)

        if files:
            await send_photos_in_batches(message, files)
            await status_msg.delete()
            asyncio.create_task(cleanup(files))
        else:
            await status_msg.delete()
        return

async def send_photos_in_batches(message: Message, files: list):
    try:
        for i in range(0, len(files), 10):
            batch = files[i:i+10]
            media_group = []

            for photo_path in batch:
                media_group.append(InputMediaPhoto(media=FSInputFile(photo_path)))

            await message.answer_media_group(
                media=media_group,
                reply_to_message_id=message.message_id
            )

            if i + 10 < len(files):
                await asyncio.sleep(1)

    except Exception:
        pass
