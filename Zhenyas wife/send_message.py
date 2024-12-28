import json
import asyncio
import os
from pyrogram import Client
from g4f.client import AsyncClient

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

# Генерация первого сообщения
async def generate_initial_message():
    try:
        context = [
            {"role": "system", "content": "Ты русскоговорящая 24-летняя девушка, ищущая парня. Отвечай дружелюбно, коротко, и только на русском языке."},
            {"role": "user", "content": "Придумай первое сообщение, чтобы познакомиться с новым человеком."}
        ]

        response = await g4f_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=context,
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Ошибка генерации первого сообщения: {e}")
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
async def send_message(user_id, chat_id):
    try:
        await app.start()

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
    finally:
        # Завершаем работу клиента
        try:
            await app.stop()
            await asyncio.sleep(1)  # Даём время на завершение фоновых задач
        except Exception as e:
            print(f"Ошибка завершения клиента: {e}")

# Упрощённая обработка событийного цикла
def run_async_task(task):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(task)
    finally:
        # Завершаем оставшиеся задачи
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

# Основной запуск
if __name__ == "__main__":
    user = asyncio.run(app.get_users(recipient_identifier))
    run_async_task(send_message(user.id, user.id))
