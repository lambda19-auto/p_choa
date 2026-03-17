"""
avatar for class Analyze (stable HeyGen integration)
"""
import os
import httpx
import asyncio
from io import BytesIO
from dotenv import load_dotenv


class Avatar:

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('HEYGEN_API_KEY')

        if not self.api_key:
            raise ValueError("HEYGEN_API_KEY not found in .env")

        self.base_url = 'https://api.heygen.com/v2'

        self.headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }

    async def create_video(self, text: str) -> BytesIO:
        """
        Generate video via HeyGen and return BytesIO
        """

        # --- safety: check text is not empty---
        if not text:
            raise ValueError("Text is empty")

        timeout = httpx.Timeout(60.0)

        # -----------------------
        # STEP 1: CREATE VIDEO (v2)
        # -----------------------
        async with httpx.AsyncClient(timeout=timeout) as client:
            payload = {
                "video_inputs": [
                    {
                        "character": {
                            "type": "talking_photo",
                            "talking_photo_id": "f24fe80a36704e91a33dbdf9ac4b8c29",
                            "scale": 1.0,
                            "talking_style": "expressive"
                        },
                        "voice": {
                            "type": "text",
                            "input_text": text,
                            "voice_id": "2b0124724e144eedba61ecb590d6c266"
                        }
                    }
                ],
                "dimension": {
                    "width": 720,
                    "height": 1280
                }
            }

            resp = await client.post(
                f"{self.base_url}/video/generate",
                headers=self.headers,
                json=payload
            )

            if resp.status_code != 200:
                raise Exception(f"HeyGen API error {resp.status_code}: {resp.text}")

            data = resp.json()
            print("CREATE RESPONSE:", data)

            video_id = data.get('data', {}).get('video_id')
            if not video_id:
                raise Exception(f"Video ID not found: {data}")

        # -----------------------
        # STEP 2: CHECK STATUS (v1 !!!)
        # -----------------------
        video_url = None
        max_attempts = 30
        sleep_seconds = 10

        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(max_attempts):

                status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"

                r = await client.get(status_url, headers=self.headers)

                if r.status_code != 200:
                    print(f"[{attempt+1}] API error: {r.status_code} {r.text}")
                    await asyncio.sleep(sleep_seconds)
                    continue

                d = r.json()
                print(f"[{attempt+1}] STATUS RESPONSE:", d)

                status = d.get('data', {}).get('status')

                if status == 'completed':
                    video_url = d['data']['video_url']
                    print("✅ Видео готово:", video_url)
                    break

                elif status == 'failed':
                    error = d.get('data', {}).get('error')
                    raise Exception(f"❌ Video generation failed: {error}")

                await asyncio.sleep(sleep_seconds)

            else:
                raise Exception("⏱ Video generation timeout")

        # -----------------------
        # STEP 3: DOWNLOAD VIDEO
        # -----------------------
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            r = await client.get(video_url)

            if r.status_code != 200:
                raise Exception(f"Download error: {r.status_code} {r.text}")

            video_file = BytesIO(r.content)
            video_file.name = f'video_{video_id}.mp4'

        return video_file