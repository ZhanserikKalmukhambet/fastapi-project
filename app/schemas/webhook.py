from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime


class WebhookRequest(BaseModel):
    message: str = Field(..., description="Text message to be processed by LLM")
    callback_url: HttpUrl = Field(..., description="URL to send the processed response to")


class WebhookResponse(BaseModel):
    request_id: str = Field(..., description="Unique identifier for the webhook request")
    status: str = Field(..., description="Status of the webhook processing")
    message: Optional[str] = Field(None, description="Response message from LLM")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WebhookCallback(BaseModel):
    request_id: str
    message: str
    status: str = "completed"
    processed_at: datetime = Field(default_factory=datetime.utcnow) 