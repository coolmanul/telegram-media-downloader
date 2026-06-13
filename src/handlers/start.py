from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ChatType

router = Router()

@router.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def cmd_start(message: Message):
    await message.answer(
        "я умею скачивать видео и фото из TikTok\nпросто отправь ссылку или добавь в группу"
    )
