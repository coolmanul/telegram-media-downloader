import re, asyncio
from aiogram import Router, F
from aiogram.types import (
    InlineQuery, InlineQueryResultArticle, InlineQueryResultPhoto,
    InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, FSInputFile, InputMediaVideo, InputMediaPhoto,
)
from services.downloader import (
    check_tiktok_video, check_tiktok_photos,
    download_tiktok_video, download_tiktok_photos,
    get_tiktok_thumbnail,
)
from services.cleaner import cleanup

router = Router()


@router.inline_query(F.query.regexp(r'https?://\S*tiktok\.com\S*'))
async def inline_tiktok(query: InlineQuery):
    match = re.search(r'https?://\S*tiktok\.com\S*', query.query)
    if not match:
        return
    url = match.group(0).strip()

    thumb = await get_tiktok_thumbnail(url)
    if not thumb:
        thumb = "https://placehold.co/400x500/1a1a2e/ffffff?text=TikTok"

    results = [
        InlineQueryResultPhoto(
            id="1",
            photo_url=thumb,
            thumbnail_url=thumb,
            caption=f"📥 TikTok\n{url}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⏳ Download", callback_data="dl_tiktok")]
                ]
            ),
        )
    ]
    await query.answer(results, cache_time=0, is_personal=True)


@router.callback_query(F.data == "dl_tiktok")
async def callback_download(callback: CallbackQuery):
    text = callback.message.caption or callback.message.text or ""
    match = re.search(r'https?://\S*tiktok\.com\S*', text)
    if not match:
        await callback.answer("No link found", show_alert=True)
        return
    url = match.group(0).strip()

    await callback.answer()
    await callback.message.edit_caption(
        caption="⏳ Downloading...",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[]),
    )

    if await check_tiktok_video(url):
        files = await download_tiktok_video(url)
        if files:
            try:
                await callback.message.edit_media(
                    media=InputMediaVideo(
                        media=FSInputFile(files[0]),
                        caption="✅ Downloaded",
                    ),
                )
                asyncio.create_task(cleanup(files))
            except Exception:
                await callback.message.answer_video(
                    video=FSInputFile(files[0]),
                    caption="✅ Downloaded",
                )
                asyncio.create_task(cleanup(files))
        else:
            await callback.message.edit_caption("❌ Download failed")
        return

    if await check_tiktok_photos(url):
        files = await download_tiktok_photos(url)
        if files:
            try:
                await callback.message.delete()
                media_batches = []
                for i in range(0, len(files), 10):
                    batch = files[i:i+10]
                    media_group = [InputMediaPhoto(media=FSInputFile(f)) for f in batch]
                    media_batches.append(media_group)
                for batch in media_batches:
                    await callback.message.answer_media_group(media=batch)
                    await asyncio.sleep(1)
                asyncio.create_task(cleanup(files))
            except Exception:
                pass
        else:
            await callback.message.edit_caption("❌ Download failed")
        return

    await callback.message.edit_caption("❌ Unsupported content")


@router.inline_query()
async def inline_default(query: InlineQuery):
    if not query.query.strip():
        return
    results = [
        InlineQueryResultArticle(
            id="1",
            title="📥 Download from TikTok",
            description="Send a TikTok link via inline",
            input_message_content=InputTextMessageContent(
                message_text="Send a TikTok link like @bot https://vm.tiktok.com/XXX"
            ),
        )
    ]
    await query.answer(results, cache_time=1, is_personal=True)
