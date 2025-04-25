import httpx
import asyncio
from celery import shared_task
from app.core.celery_app import app
from app.utils.helpers import update_webhook_status


@app.task(bind=True, max_retries=3, retry_backoff=True)
def process_webhook(self, request_id: str, message: str, callback_url: str):
    try:
        llm_response = "LLM_RESPONSE" + " for " + message
        
        with httpx.Client() as client:
            response = client.post(
                callback_url,
                json={
                    "request_id": request_id,
                    "status": "completed",
                    "response": llm_response
                }
            )

            if response.status_code != 200:
                raise Exception(f"Failed to process webhook: {response.status_code}")
        
        asyncio.run(update_webhook_status(request_id, "completed", llm_response))
    except Exception as exc:
        asyncio.run(update_webhook_status(request_id, "failed", str(exc)))

        raise self.retry(exc=exc)
        