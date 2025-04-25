from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session, AsyncSessionFactory
from app.models.webhook import WebhookRequest
from sqlalchemy import select
from datetime import datetime


async def update_webhook_status(request_id: str, status: str, response: str) -> bool:
    print("Updating webhook status")

    try:
        async with AsyncSessionFactory() as session:
            result = await session.execute(select(WebhookRequest).where(WebhookRequest.id == request_id))
            
            webhook = result.scalar_one_or_none()
            if webhook is None:
                print(f"Webhook with ID {request_id} not found")
                return False

            webhook.status = status
            webhook.response = response
            webhook.processed_at = datetime.utcnow()

            await session.commit()
            await session.refresh(webhook)

            print("Webhook status updated")
            return True
    except Exception as e:
        print(f"Error updating webhook status: {e}")
        
        await session.rollback()

        print("Webhook status update failed")
        return False

    
