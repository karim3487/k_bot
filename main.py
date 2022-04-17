# import logging
from os import getenv

import requests
from aiogram import Bot, Dispatcher, executor, types

from aiogram.utils.exceptions import BotBlocked, MessageIsTooLong

# logging.basicConfig(level=logging.DEBUG)

TOKEN = getenv("BOT_TOKEN")
if not TOKEN:
    exit("Error: no token provided")

bot = Bot(token=f"{TOKEN}")
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await message.answer(
        "Привет, <i>" + message.chat.first_name +
        "</i>!🙃 Я могу ответить на любой вопрос", parse_mode='html')


@dp.message_handler()
async def get_answer(message: types.Message):
    question = message.text
    response = requests.get(f"http://127.0.0.1:8000/api/v1/answers/?cosine={question}")
    data = response.json()

    answers = data['results'][:3]
    for answer in answers:
        article = answer['article']
        if article is not None:
            await message.answer(
                build_message(
                    answer['text'],
                    article['header'],
                    article['lid'],
                    article['url']
                ),
                parse_mode='html'
            )
        else:
            if answer['url'] != '':
                await message.answer(f"{answer['text']}\n\nСсылка {answer['url']}")
            else:
                await message.answer(answer['text'])


@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    print(f"I was blocked by a user!\nMessage: {update}\nError: {exception}")

    return True


@dp.errors_handler(exception=MessageIsTooLong)
async def error_bot_blocked(update: types.Update, exception: MessageIsTooLong):
    print(f"Message is too long\nMessage: {update}\nError: {exception}")

    return True


def build_message(text, header, lid, url):
    return f"{text}\n\n\n<b>{header}</b>\n\n{lid}\n\n<i>Ссылка на статью:{url}</i>"


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
