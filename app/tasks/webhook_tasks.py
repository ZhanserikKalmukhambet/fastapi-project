import httpx
from celery import states
from app.core.celery_app import celery_app
from app.core.config import get_settings

settings = get_settings()

@celery_app.task(
    bind=True,
    name="tasks.process_webhook",
    max_retries=3,
    retry_backoff=True
)
def process_webhook(self, request_id: str, message: str, callback_url: str):
    """
    Process webhook request with mock LLM response
    """
    try:
        # 1. Mock LLM processing
        llm_response = "LLM_RESPONSE"
        
        # 2. Send to callback URL
        with httpx.Client() as client:
            response = client.post(
                callback_url,
                json={
                    "request_id": request_id,
                    "status": "completed",
                    "response": llm_response
                }
            )
            response.raise_for_status()
        
        # 3. Return success result
        return {
            "status": "completed",
            "request_id": request_id,
            "response": llm_response
        }
        
    except httpx.HTTPError as exc:
        # Handle callback URL errors
        self.update_state(
            state=states.FAILURE,
            meta={
                "request_id": request_id,
                "error": f"Callback URL error: {str(exc)}"
            }
        )
        raise self.retry(exc=exc)
        
    except Exception as exc:
        # Handle any other errors
        self.update_state(
            state=states.FAILURE,
            meta={
                "request_id": request_id,
                "error": f"Task processing error: {str(exc)}"
            }
        )
        raise exc 