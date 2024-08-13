import asyncio
import logging
import sys
import os
from os import getenv

import aioschedule
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')
ext = ['.jpg', '.jpeg']


async def photo():
    for root, dirs, files in os.walk(media_dir):
        print(f'root: {root},\n dirs: {dirs},\n files: {files}')
        for file in files:
            if file.lower().endswith(tuple(ext)) and '~$' not in file:
                photo_file = os.path.join(media_dir, file)
                await bot.send_photo(chat_id=-1002205937294, photo=types.FSInputFile(photo_file))
                os.remove(os.path.join(media_dir, file))


async def scheduler():
    aioschedule.every(10).seconds.do(photo)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(0.1)


async def on_startup():
    asyncio.create_task(scheduler())
    await asyncio.sleep(0.1)


async def main() -> None:
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
