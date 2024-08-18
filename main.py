import asyncio
import logging
import sys
import os
from os import getenv

import cv2
import numpy as np

import aioschedule
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
ID = getenv("CHAT_ID")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')
ext = ['.jpg', '.jpeg']


async def photo():
    for root, dirs, files in os.walk(media_dir):
        for file in files:
            if file.lower().endswith(tuple(ext)) and '~$' not in file:
                photo_file = os.path.join(media_dir, file)
                image_original = cv2.imread(photo_file)

                contrast = 1.1
                brightness = -20
                image = cv2.convertScaleAbs(image_original, alpha=contrast, beta=brightness)
                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                image = cv2.filter2D(image, -1, kernel)
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                h, s, v = cv2.split(hsv)
                h += 1
                s += 10
                v += 0
                final_hsv = cv2.merge((h, s, v))
                image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

                face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)

                image_final = cv2.vconcat([image_original, image])
                cv2.imwrite(photo_file, image_final)

                await bot.send_photo(chat_id=ID, photo=types.FSInputFile(photo_file))
                os.remove(os.path.join(media_dir, file))


async def scheduler():
    aioschedule.every(1).to(3).seconds.do(photo)
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
