import asyncio
import httpx
from datetime import datetime, timedelta
from collections import deque

retry_queue = deque()
MAX_RETRIES = 5
DELAYS = [60, 300, 900, 3600, 7200]  # 1min, 5min, 15min, 1hr, 2hr

class WebhookRetry:
    def __init__(self, url: str, payload: dict):
        self.url = url
        self.payload = payload
        self.attempts = 0
        self.created_at = datetime.now()
        self.next_retry = self.created_at
    
    def should_retry(self):
        return datetime.now() >= self.next_retry and self.attempts < MAX_RETRIES
    
    def retry(self):
        self.attempts += 1
        if self.attempts < MAX_RETRIES:
            self.next_retry = datetime.now() + timedelta(seconds=DELAYS[self.attempts])

async def process_retry_queue():
    while True:
        if retry_queue:
            retry = retry_queue[0]
            if retry.should_retry():
                retry_queue.popleft()
                try:
                    async with httpx.AsyncClient() as client:
                        r = await client.post(retry.url, json=retry.payload, timeout=30)
                        if r.status_code != 200:
                            retry.retry()
                            if retry.attempts < MAX_RETRIES:
                                retry_queue.append(retry)
                except:
                    retry.retry()
                    if retry.attempts < MAX_RETRIES:
                        retry_queue.append(retry)
        await asyncio.sleep(30)

def add_to_retry_queue(url: str, payload: dict):
    retry = WebhookRetry(url, payload)
    retry_queue.append(retry)
    print(f"Added to retry queue: {url}")
