import json
import asyncio
import os
import sys
from pyrogram import Client
from g4f.client import AsyncClient

# Установить политику событий для Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Замените на свои значения
api_id = "9808094"
api_hash = "59e5cf4eec14f7fbd6a6fd3d80c7657c"

# Инициализация Telegram клиента
app = Client("my_bot", api_id=api_id, api_hash=api_hash)
g4f_client = AsyncClient()

# Укажите username (без @) или номер телефона
recipient_identifier = "+79524136263"

# Папка для хранения контекстов
context_dir = "contexts"
os.makedirs(context_dir, exist_ok=True)

# Генерация первого сообщения с повторными попытками
async def generate_initial_message(max_retries=3):
    context = [
        {"role": "system", "content": "Ты русскоговорящая 24-летняя девушка, ищущая парня. Отвечай дружелюбно, коротко, и только на русском языке."},
        {"role": "user", "content": "Придумай первое сообщение, чтобы познакомиться с новым человеком."}
    ]
    for attempt in range(max_retries):
        try:
            response = await g4f_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=context,
                max_tokens=50
            )
            reply = response.choices[0].message.content.strip()
            if "Misuse detected" not in reply:
                return reply
            print(f"Попытка {attempt + 1}/{max_retries}: получено 'Misuse detected'. Перепробуем...")
        except Exception as e:
            print(f"Ошибка генерации сообщения на попытке {attempt + 1}/{max_retries}: {e}")
        await asyncio.sleep(2)
    return "Привет! Хочешь познакомиться? 😊"

# Загрузка контекста
def load_context(user_id):
    context_path = os.path.join(context_dir, f"{user_id}.json")
    if os.path.exists(context_path):
        with open(context_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return [
        {"role": "system", "content": "Ты русскоговорящая 24-летняя девушка, ищущая парня. Отвечай дружелюбно, коротко, и только на русском языке."}
    ]

# Сохранение контекста
def save_context(user_id, context):
    context_path = os.path.join(context_dir, f"{user_id}.json")
    with open(context_path, "w", encoding="utf-8") as file:
        json.dump(context, file, ensure_ascii=False, indent=4)

# Отправка первого сообщения
async def send_message(recipient_identifier):
    try:
        async with app:
            user = await app.get_users(recipient_identifier)
            user_id = user.id
            chat_id = user.id

            # Загрузка контекста
            context = load_context(user_id)

            # Проверка, отправлено ли первое сообщение
            if any(msg.get("role") == "assistant" for msg in context):
                print(f"Сообщение уже отправлено пользователю {user_id}. Пропускаем отправку.")
                return

            # Генерация первого сообщения
            initial_message = await generate_initial_message()

            # Отправляем сообщение
            await app.send_message(chat_id, initial_message)
            print(f"Отправлено первое сообщение пользователю {user_id}: {initial_message}")

            # Сохраняем в контекст
            context.append({"role": "assistant", "content": initial_message})
            save_context(user_id, context)

    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")

# Основной запуск
if __name__ == "__main__":
    asyncio.run(send_message(recipient_identifier))
