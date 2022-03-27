import logging
from os import getenv

import requests
from aiogram import Bot, Dispatcher, executor, types

from aiogram.utils.exceptions import BotBlocked, MessageIsTooLong

logging.basicConfig(level=logging.DEBUG)

TOKEN = getenv("BOT_TOKEN")
if not TOKEN:
    exit("Error: no token provided")

bot = Bot(token=f"{TOKEN}")
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await message.answer(
        "Привет, <i>" + message.chat.first_name +
        "</i>!🙃 Я могу ответить на любой вопрос про Кыргызстан", parse_mode='html')


@dp.message_handler()
async def get_answer(message: types.Message):
    question = message.text
    response = requests.get(f"http://127.0.0.1:8000/api/v1/answers/?cosine={question}")
    data = response.json()
    answers = split_answer(data['results'][0]['text'])
    for answer in answers:
        await message.answer(answer)


@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")

    return True


@dp.errors_handler(exception=MessageIsTooLong)
async def error_bot_blocked(exception: MessageIsTooLong):
    print(f"Ошибка: {exception}\nСообщение слишком длинное!")

    return True


def split_answer(answer):
    length_of_answer = 4096
    answers = []
    current_start_index = 0

    if len(answer) <= length_of_answer:
        return [answer]

    try:
        for part in range(1, len(answer) // 4096 + 1):
            for current_end_index in range(length_of_answer + current_start_index, current_start_index, -1):
                if answer[current_end_index] == '.':
                    answers.append(answer[current_start_index:current_end_index + 1])
                    current_start_index = current_end_index + 2
                    break

        if len(answer) - current_start_index > 4096:
            answers.append(split_answer(answer[current_start_index:len(answer)]))
        else:
            answers.append(answer[current_start_index:len(answer)])

    except Exception as ex:
        print(ex)
        answers = []
        for idx in range(0, len(answer), 4096):
            answers.append(answer[idx:idx+4096])

    return answers


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
