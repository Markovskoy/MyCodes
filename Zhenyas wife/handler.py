import json
import random
import asyncio
from pyrogram import Client, filters, enums
from g4f.client import AsyncClient
import os
from collections import deque
import subprocess
import sys


# Установка политики события для Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Замените на свои значения
api_id = "9808094"
api_hash = "59e5cf4eec14f7fbd6a6fd3d80c7657c"

# Инициализация Telegram клиента
app = Client("my_bot", api_id=api_id, api_hash=api_hash)

# Инициализация g4f клиента
g4f_client = AsyncClient()

# Папка для сохранения контекстов
context_dir = "contexts"
os.makedirs(context_dir, exist_ok=True)

# Очередь сообщений
message_queue = deque()

# Имя бота
BOT_NAME = "Алиса"

# Загрузка контекста
def load_context(user_id):
    context_path = os.path.join(context_dir, f"{user_id}.json")
    if os.path.exists(context_path):
        with open(context_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return [
        {"role": "system", "content": f"Ты русскоговорящая 24-летняя девушка по имени {BOT_NAME}, ищущая парня. Отвечай только на русском языке. Ты милая, дружелюбная, немного загадочная, но всегда позитивная."}
    ]

# Сохранение контекста
def save_context(user_id, context):
    context_path = os.path.join(context_dir, f"{user_id}.json")
    with open(context_path, "w", encoding="utf-8") as file:
        json.dump(context, file, ensure_ascii=False, indent=4)

# Генерация ответа
async def generate_response(context):
    max_retries = 5
    fallback_models = ["gpt-4o-mini", "text-ada-001", "gpt-3.5-turbo"]
    for attempt in range(max_retries):
        for model in fallback_models:
            try:
                response = await g4f_client.chat.completions.create(
                    temperature=0.7,
                    model=model,
                    messages=context,
                    max_tokens=50
                )
                if not response or not hasattr(response, "choices") or not response.choices:
                    raise ValueError("Некорректный или пустой ответ от модели.")

                bot_reply = response.choices[0].message.content.strip()

                # Проверяем, содержит ли ответ ошибку
                if "Misuse detected" in bot_reply:
                    print(f"[{model}] Misuse detected. Попытка {attempt + 1}/{max_retries}...")
                    continue  # Пробуем другую модель

                return bot_reply  # Возвращаем нормальный ответ
            except Exception as e:
                print(f"[{model}] Ошибка на попытке {attempt + 1}/{max_retries}: {e}")
                await asyncio.sleep(2)  # Небольшая задержка перед повторной попыткой

    return None  # Если все попытки провалились
user_processing_status = {}

# Обработка входящих сообщений
@app.on_message(filters.text)
async def handle_message(client, message):
    global message_queue
    user_id = message.from_user.id
    print(f"Новое сообщение от {user_id}: {message.text}")

    # Проверяем, обрабатывается ли уже сообщение от этого пользователя
    if user_processing_status.get(user_id, False):
        print(f"Сообщение от {user_id} добавлено в очередь.")
        message_queue.append((user_id, message))
    else:
        # Устанавливаем статус обработки
        user_processing_status[user_id] = True
        message_queue.append((user_id, message))

# Обработка очереди сообщений
async def process_message_queue():
    while True:
        if message_queue:
            user_id, message = message_queue.popleft()
            try:
                context = load_context(user_id)

                # Добавляем сообщение пользователя
                user_message = {"role": "user", "content": message.text}
                context.append(user_message)
                save_context(user_id, context)

                # Читаем сообщение
                await app.read_chat_history(chat_id=message.chat.id)
                await asyncio.sleep(random.randint(3, 6))

                # Генерация ответа
                bot_reply = await generate_response(context)
                if bot_reply:
                    # Устанавливаем статус "печатает"
                    await app.send_chat_action(chat_id=message.chat.id, action=enums.ChatAction.TYPING)
                    await asyncio.sleep(random.randint(3, 5))
                    if random.random() < 0.25:  # 25% шанс на ответ с цитированием
                        await message.reply_text(bot_reply, quote=True)
                    else:
                        await message.reply_text(bot_reply)

                    # Сохраняем ответ бота
                    assistant_message = {"role": "assistant", "content": bot_reply}
                    context.append(assistant_message)
                    save_context(user_id, context)
            finally:
                # Освобождаем пользователя после обработки сообщения
                user_processing_status[user_id] = False
        else:
            await asyncio.sleep(1)

# Основной запуск
if __name__ == "__main__":
    user_ids = [file.split('.')[0] for file in os.listdir(context_dir) if file.endswith('.json')]

    if not user_ids:
        print("Контекстов не найдено. Запускаем send_message...")
        try:
            subprocess.run(["python", "send_message.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка выполнения send_message: {e}")
    else:
        print("Контексты найдены. Ожидаем сообщения...")
    asyncio.ensure_future(process_message_queue())
    app.run()
