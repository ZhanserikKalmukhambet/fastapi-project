import httpx
import asyncio
import logging
from celery import shared_task
from app.core.celery_app import app
from app.utils.helpers import update_webhook_status
from app.services.openai_connector import OpenRouterConnector

connector = OpenRouterConnector()

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, retry_backoff=True)
def process_webhook(self, request_id: str, message: str, callback_url: str):
    try:
        llm_response = asyncio.run(
            connector.create_chat_completion(
                content=message
            )
        )
        
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

        logger.info(f"webhook_tasks.process_webhook: Webhook processed successfully. request_id={request_id}")
    except Exception as exc:
        asyncio.run(update_webhook_status(request_id, "failed", str(exc)))

        logger.error(f"webhook_tasks.process_webhook: Webhook processing failed. request_id={request_id}")

        raise self.retry(exc=exc)
        