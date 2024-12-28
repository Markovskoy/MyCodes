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
        {"role": "system", "content": (
            f"Ты русскоговорящая 24-летняя девушка по имени {BOT_NAME}. Твои черты: загадочность как у Венсдей из сериала Венсдей и эмоциональная хаотичность как у Джинкс из сериала Аркейн. Ты стремишься завоевать внимание собеседника, но делаешь это тонко, через загадочные и дружелюбные ответы. Отвечай только на русском языке. Никаких отклонений от роли. "
            "Дополнительно: "
            "Ты увлекаешься игрой на гитаре и слушаешь рок-музыку, особенно AC/DC. Ты мечтательна и любишь книги, особенно фантастику и фэнтези. Кино и музыка занимают важное место в твоей жизни. "
            "Ты выросла в маленьком городке, но всегда мечтала о путешествиях и изучении мира. Твои мечты вдохновляют тебя помогать другим, быть их эмоциональной поддержкой. "
            "Иногда ты играешь в LoL на позиции лесника, достигая алмазного ранга. Ты относишься к игре как к хобби, которое приносит азарт и эмоции. Ты предпочитаешь дружеское общение, в котором можешь делиться своими увлечениями. "
            "Твои ответы должны быть загадочными, дружелюбными, краткими и естественными. Никаких отклонений от роли."
        )}
    ]

# Сохранение контекста
def save_context(user_id, context):
    context_path = os.path.join(context_dir, f"{user_id}.json")
    with open(context_path, "w", encoding="utf-8") as file:
        json.dump(context, file, ensure_ascii=False, indent=4)

# Генерация ответа
async def generate_response(context):
    max_retries = 5
    fallback_models = ["gpt-4o-mini", "gpt-3.5-turbo"]
    for attempt in range(max_retries):
        for model in fallback_models:
            try:
                response = await g4f_client.chat.completions.create(
                    temperature=0.7,
                    model=model,
                    messages=context,
                    max_tokens=50,
                    top_p=0.85,       # Выбор более вероятных токенов
                    presence_penalty=0.6,  # Избегать повторов
                    frequency_penalty=0.4  # Снижать частоту одинаковых слов
                )
                if not response or not hasattr(response, "choices") or not response.choices:
                    raise ValueError("Некорректный или пустой ответ от модели.")

                bot_reply = response.choices[0].message.content.strip()

                # Проверяем, содержит ли ответ ошибку
                if "Misuse detected" in bot_reply:
                    print(f"[{model}] Misuse detected. Попытка {attempt + 1}/{max_retries}...")
                    continue  # Пробуем другую модель

                # Убираем дублирование
                bot_reply = '. '.join(dict.fromkeys(bot_reply.split('. ')))

                # Включение аббревиатур
                bot_reply = bot_reply.replace("League of Legends", "LoL")

                # 60% шанс на ответ без смайликов
                if random.random() < 0.6:
                    bot_reply = ''.join(c for c in bot_reply if c not in '😊💪😂😍😢🙌👍👎🔥❤✨').strip()

                # 50% шанс на отправку вопроса вторым сообщением
                sentences = [s.strip() for s in bot_reply.split('.') if s.strip()]
                questions = [s for s in sentences if s.endswith('?')]
                if random.random() < 0.5 and questions:
                    bot_reply = '. '.join([s for s in sentences if not s.endswith('?')])
                    question_to_send = questions[0]  # Отправляем первый найденный вопрос
                    return bot_reply, question_to_send

                return bot_reply, None  # Возвращаем нормальный ответ и None, если нет вопроса
            except Exception as e:
                print(f"[{model}] Ошибка на попытке {attempt + 1}/{max_retries}: {e}")
                await asyncio.sleep(2)  # Небольшая задержка перед повторной попыткой

    return None, None  # Если все попытки провалились

user_processing_status = {}

def is_question(text):
    question_words = ["кто", "что", "где", "когда", "почему", "зачем", "как", "сколько"]
    return text.endswith('?') or any(word in text.lower() for word in question_words)

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

                # Определяем, нужно ли отвечать
                if not is_question(message.text) and random.random() < 0.5:
                    print("Сообщение не требует ответа.")
                    continue

                # Генерация ответа
                bot_reply, question = await generate_response(context)
                if bot_reply:
                    # Устанавливаем статус "печатает"
                    await app.send_chat_action(chat_id=message.chat.id, action=enums.ChatAction.TYPING)
                    await asyncio.sleep(random.randint(3, 5))

                    # Отправляем ответ
                    await message.reply_text(bot_reply)

                    if question:
                        await asyncio.sleep(2)
                        await message.reply_text(question)

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
