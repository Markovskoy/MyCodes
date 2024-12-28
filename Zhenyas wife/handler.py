import json
import random
import asyncio
from pyrogram import Client, filters, enums
from g4f.client import Client as G4FClient
import subprocess
import sys
from collections import deque

# Установка политики события для Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Замените на свои значения
api_id = "9808094"
api_hash = "59e5cf4eec14f7fbd6a6fd3d80c7657c"

# Инициализация Telegram клиента
app = Client("my_bot", api_id=api_id, api_hash=api_hash)

# Инициализация g4f клиента
g4f_client = G4FClient()

# Путь для сохранения контекста
context_file = "context.json"

# Очередь сообщений
message_queue = deque()

# Имя бота
BOT_NAME = "Алиса"

# Загрузка истории диалога
def load_context():
    try:
        with open(context_file, "r", encoding="utf-8") as file:
            content = file.read().strip()
            return json.loads(content) if content else [
                {"role": "system", "content": f"Ты русскоговорящая 24-летняя девушка по имени {BOT_NAME}, ищущая парня. Отвечай только на русском языке. Ты милая, дружелюбная, немного загадочная, но всегда позитивная."}
            ]
    except FileNotFoundError:
        return [{"role": "system", "content": f"Ты русскоговорящая 24-летняя девушка по имени {BOT_NAME}, ищущая парня. Отвечай только на русском языке. Ты милая, дружелюбная, немного загадочная, но всегда позитивная."}]

# Сохранение истории диалога
def save_context(context):
    with open(context_file, "w", encoding="utf-8") as file:
        json.dump(context, file, ensure_ascii=False, indent=4)

# Проверка языка на основе наличия кириллицы
def is_russian(text):
    return any("а" <= char <= "я" or "А" <= char <= "Я" for char in text)

# Проверка, отправлено ли первое сообщение
def is_first_message_sent():
    context = load_context()
    for msg in context:
        if msg["role"] == "assistant" and "Привет, увидела тебя в инсте" in msg["content"]:
            return True
    return False

# Генерация ответа с повторными попытками
async def generate_response(context):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = g4f_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=context,
                max_tokens=50
            )

            if not response or not hasattr(response, "choices") or not response.choices:
                raise ValueError("Некорректный или пустой ответ от модели.")

            bot_reply = response.choices[0].message.content.strip()

            # Проверяем язык ответа
            if not is_russian(bot_reply):
                print(f"Ответ на неверном языке: {bot_reply}. Попытка {attempt + 1}/{max_retries}")
                continue  # Перегенерация ответа

            # Обрезаем слишком длинные ответы
            bot_reply = ". ".join(bot_reply.split(".")[:2]).strip()
            if not bot_reply.endswith((".", "!", "?")):
                bot_reply += "."

            # Гарантируем, что бот называет себя Алиса
            bot_reply = bot_reply.replace("Меня зовут Аня", f"Меня зовут {BOT_NAME}")

            return bot_reply
        except Exception as e:
            print(f"Ошибка генерации ответа на попытке {attempt + 1}/{max_retries}: {e}")
            await asyncio.sleep(2)  # Небольшая задержка перед повторной попыткой
    return None  # Если все попытки провалились

# Обработка входящих сообщений
@app.on_message(filters.text)
async def handle_message(client, message):
    global message_queue
    print(f"Новое сообщение от {message.from_user.username or message.from_user.id}: {message.text}")

    # Добавляем сообщение в очередь
    message_queue.append(message)

# Обработка очереди сообщений
async def process_message_queue():
    context = load_context()
    introduced = False  # Флаг, представился ли бот
    while True:
        if message_queue:
            message = message_queue.popleft()
            text = message.text

            # Сохраняем сообщение пользователя в контекст
            context.append({"role": "user", "content": text})
            save_context(context)

            # Задержка перед статусом "печатает"
            delay_before_typing = random.randint(3, 6)
            print(f"Задержка перед статусом 'печатает': {delay_before_typing} секунд")
            await asyncio.sleep(delay_before_typing)

            # Устанавливаем статус "печатает"
            await app.send_chat_action(chat_id=message.chat.id, action=enums.ChatAction.TYPING)
            await asyncio.sleep(random.randint(3, 6))

            # Генерация ответа
            bot_reply = await generate_response(context)

            if bot_reply:
                # Логика, чтобы бот не повторялся в ответах
                if "Меня зовут" in bot_reply and introduced:
                    # Если бот уже представился, удаляем из ответа упоминание о представлении
                    bot_reply = bot_reply.replace(f"Меня зовут {BOT_NAME}! ", "")

                if not introduced and "Меня зовут" in bot_reply:
                    introduced = True  # Устанавливаем флаг, что бот представился

                # Случайный выбор: цитировать или просто отвечать
                if random.random() < 0.5:  # 50% шанс на цитирование
                    await message.reply_text(bot_reply, quote=True)
                else:
                    await message.reply_text(bot_reply)

                # Сохраняем ответ в контекст
                context.append({"role": "assistant", "content": bot_reply})
                save_context(context)
        else:
            await asyncio.sleep(1)

# Основной запуск
# Основной запуск handler
if __name__ == "__main__":
    if not is_first_message_sent():
        print("Запускаем скрипт отправки первого сообщения...")
        try:
            subprocess.run(["python", "send_message.py"], check=True)
            print("Скрипт отправки первого сообщения выполнен успешно.")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка выполнения скрипта отправки сообщения: {e}")
    else:
        print("Первое сообщение уже отправлено. Пропускаем отправку.")

    print("Бот запущен. Ожидаем сообщения...")
    asyncio.ensure_future(process_message_queue())
    app.run()
