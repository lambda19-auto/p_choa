'''
avatar for class Analyze
'''
import os
import httpx
import asyncio
from io import BytesIO
from dotenv import load_dotenv


class Avatar:

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('HEYGEN_API_KEY')
        self.url_generate = 'https://api.heygen.com/v2/video/generate'
        self.url_status = 'https://api.heygen.com/v2/video_status'
        self.headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }

    async def create_video(self, text: str) -> BytesIO:
        """
        Генерируем видео по тексту и возвращаем BytesIO для Telegram
        """
        timeout = httpx.Timeout(
            connect=10.0,
            read=60.0,
            write=10.0,
            pool=60.0
        )

        # Шаг 1: generate
        async with httpx.AsyncClient(timeout=timeout) as client:
            payload = {
                'video_inputs': [
                    {
                        'character': {
                            'type': 'talking_photo',
                            'talking_photo_id': 'f24fe80a36704e91a33dbdf9ac4b8c29',
                            'scale': 1.0,
                            'talking_style': 'expressive',
                            'expression': 'happy',
                            'super_resolution': True,
                            "matting": False
                        },
                        'voice': {
                            'type': 'text',
                            'input_text': text,
                            'voice_id': '2b0124724e144eedba61ecb590d6c266'
                        }
                    }
                ],
                'dimension': {
                    'width': 720,
                    'height': 1280
                }
            }

            resp = await client.post(self.url_generate, headers=self.headers, json=payload)
            if resp.status_code != 200:
                raise Exception(f"HeyGen API error {resp.status_code}: {resp.text}")

            data = resp.json()
            video_id = data.get('data', {}).get('video_id')
            print("Полученный video_id:", video_id)
            if not video_id:
                raise Exception(f"Video ID not found in response: {data}")

        # Шаг 2: опрашиваем статус
        max_attempts = 60
        sleep_seconds = 60  # немного меньше, чтобы быстрее реагировать

        video_url = None
        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(max_attempts):
                status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
                r = await client.get(status_url, headers=self.headers)

                if r.status_code != 200:
                    print(f"[{attempt+1}] Ошибка API: {r.status_code}, {r.text}")
                else:
                    d = r.json()
                    status = d.get('data', {}).get('status')
                    print(f"[{attempt+1}] Статус видео: {status}")

                    if status == 'completed':
                        video_url = d['data']['video_url']
                        print(f"Видео готово! URL: {video_url}")
                        break
                    elif status == 'failed':
                        raise Exception('Video generation failed')

                await asyncio.sleep(sleep_seconds)
            else:
                raise Exception("Video was not generated in time")

        # Шаг 3: скачиваем видео в BytesIO
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            r = await client.get(video_url)
            if r.status_code != 200:
                raise Exception(f"Ошибка скачивания видео: {r.status_code} {r.text}")
            video_file = BytesIO(r.content)
            video_file.name = f'video_{video_id}.mp4'

        return video_file


