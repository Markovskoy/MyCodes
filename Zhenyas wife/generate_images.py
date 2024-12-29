import random
from g4f.client import Client

client = Client()

# Полное описание девушки
description = (
    "A highly realistic portrait or full-body image of a young 24-year-old Russian-speaking woman with an oval face and perfectly smooth, radiant skin without a single blemish. "
    "Her skin tone is light with a soft golden hue, enhancing her natural beauty. "
    "She has long, straight, thick hair of deep chocolate brown color, shining under the light and elegantly cascading over her shoulders. "
    "Her eyes are large, almond-shaped, with a rich hazel-green color and a slight golden shimmer, emphasized by long, thick, dark eyelashes. "
    "Her eyebrows are naturally thick, neatly shaped, and dark brown, softly arching to frame her expressive eyes. "
    "Her nose is small, neat, and slightly upturned at the tip, adding charm to her features. "
    "Her chin is well-defined, slightly rounded, giving her face a refined, harmonious, and balanced appearance. "
    "Her lips are full, naturally pink, with a soft and natural contour that complements her youthful look. "
    "Her cheekbones are softly defined, highlighting her femininity and refinement. "
    "Her overall proportions are slender, with a toned figure and an elegant appearance, consistent across all scenes. "
    "Her appearance must always match perfectly with these descriptions, ensuring consistent and identical features across all generated images. "
    "She has a warm, approachable demeanor, reflecting her 24 years of youth and vibrancy, as well as her Russian-speaking background."
)

# Сцены для выбора
scenes = [
    f"Scene: The woman is relaxing on a sofa, wearing a light blue shirt, sitting in a modern, cozy living room with soft natural light. {description} --ar 3:4",
    f"Scene: The woman is sitting at a desk, working on a laptop, surrounded by books and indoor plants, in a bright, minimalist home office. {description} --ar 3:4",
    f"Scene: The woman is lying on a bed with soft blankets, looking directly at the camera with a calm and confident expression. {description} --ar 3:4",
    f"Scene: The woman is standing in a park, surrounded by blooming flowers and trees, smiling gently under the afternoon sun. {description} --ar 3:4",
    f"Scene: The woman is walking along a modern urban street, wearing casual yet elegant attire, with soft sunlight highlighting her features. {description} --ar 3:4",
]

# Выбор случайной сцены
selected_scene = random.choice(scenes)

# Генерация изображения
try:
    response = client.images.generate(
        model="dall-e-3",  # Используем поддерживаемую модель
        prompt=selected_scene,
        response_format="url",
        temperature =1,
    )
    
    # Получение ссылки на изображение
    image_url = response.data[0].url
    print(f"Generated image URL: {image_url}")
except Exception as e:
    print(f"Error generating image: {e}")
