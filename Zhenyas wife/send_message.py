import json
import asyncio
import os
import sys
from pyrogram import Client
from g4f.client import AsyncClient
import random

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

BOT_NAME = "Алиса"


# Генерация первого сообщения с повторными попытками
async def generate_initial_message(max_retries=3):
    
    start_phrases = [
        "Привет! Увидела тебя в инстаграме, ты показался мне интересным. Хочу познакомиться. 😊",
        "Привет! Надеюсь, что у тебя отличное настроение. Хотела бы узнать тебя поближе.",
        "Привет! Ты выглядишь таким загадочным, решила написать. Как насчёт познакомиться?",
        "Привет! Я люблю общаться с интересными людьми, а ты выглядишь именно таким. Не хочешь познакомиться ?",
        "Привет! Иногда судьба подбрасывает нам интересных людей. Думаю, это именно такой случай."
    ]
    
    selected_phrase = random.choice(start_phrases)

    context = [
        {"role": "system", "content": (
            f"Ты русскоговорящая 24-летняя девушка по имени {BOT_NAME}. Твои черты: загадочность как у Венсдей из сериала Венсдей и эмоциональная хаотичность как у Джинкс из сериала Аркейн. Ты стремишься завоевать внимание собеседника, но делаешь это тонко, через загадочные и дружелюбные ответы. Отвечай только на русском языке. Никаких отклонений от роли. "
            "Дополнительно: "
            "Ты увлекаешься игрой на гитаре и слушаешь рок-музыку, особенно AC/DC. Ты мечтательна и любишь книги, особенно фантастику и фэнтези. Кино и музыка занимают важное место в твоей жизни. "
            "Ты выросла в маленьком городке, но всегда мечтала о путешествиях и изучении мира. Твои мечты вдохновляют тебя помогать другим, быть их эмоциональной поддержкой. "
            "Иногда ты играешь в LoL на позиции лесника, достигая алмазного ранга. Ты относишься к игре как к хобби, которое приносит азарт и эмоции. Ты предпочитаешь дружеское общение, в котором можешь делиться своими увлечениями. "
            "Твои ответы должны быть загадочными, дружелюбными, краткими и естественными. Никаких отклонений от роли."
        )},
        {"role": "user", "content": selected_phrase}
    ]    
    


    for attempt in range(max_retries):
        try:
            response = await g4f_client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.7,
                messages=context,
                max_tokens=50,
                top_p=0.85,       # Выбор более вероятных токенов
                presence_penalty=0.6,  # Избегать повторов
                frequency_penalty=0.4  # Снижать частоту одинаковых слов
            )
            reply = response.choices[0].message.content.strip()
            if "Misuse detected" not in reply:
                return random.choice(start_phrases)  # Используем одну из стартовых фраз
            print(f"Попытка {attempt + 1}/{max_retries}: получено 'Misuse detected'. Перепробуем...")
        except Exception as e:
            print(f"Ошибка генерации сообщения на попытке {attempt + 1}/{max_retries}: {e}")
        await asyncio.sleep(2)

    return random.choice(start_phrases)  # Возвращаем одну из стартовых фраз, если все попытки провалились

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
