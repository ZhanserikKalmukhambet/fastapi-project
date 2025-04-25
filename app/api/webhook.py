import uuid
import asyncio
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.webhook import WebhookRequest, WebhookResponse, WebhookCallback
from app.core.database import get_session
from app.models.webhook import WebhookRequest as WebhookRequestModel
from sqlalchemy import select
from app.tasks.webhook_tasks import process_webhook
from celery.result import AsyncResult


router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/webhook", response_model=WebhookResponse)
async def create_webhook(
    webhook: WebhookRequest,
    db_session: AsyncSession = Depends(get_session)
):
    extra = {}

    try:
        request_id = str(uuid.uuid4())
        
        db_webhook = WebhookRequestModel(
            id=request_id,  
            status="pending",
            message=webhook.message,
            callback_url=str(webhook.callback_url)
        )
        db_session.add(db_webhook)

        extra["webhook_id"] = db_webhook.id
        extra["callback_url"] = db_webhook.callback_url

        logger.info(f"webhook.create_webhook: Webhook request created. extra={extra}")
                    
        await db_session.commit()
        await db_session.refresh(db_webhook)
        
        task = process_webhook.delay(
            request_id=request_id,
            message=webhook.message,
            callback_url=str(webhook.callback_url)
        )   
        logger.info(f"webhook.create_webhook: Webhook request processed as a background task. extra={extra}")
        
        return WebhookResponse(
            request_id=db_webhook.id,
            status=db_webhook.status,
            message=db_webhook.message,
            response=db_webhook.response,
            created_at=db_webhook.created_at
        )
        
    except Exception as e:
        await db_session.rollback()

        logger.error(f"webhook.create_webhook: Failed to process webhook", extra={"error": str(e)})

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process webhook: {str(e)}"
        )


@router.get("/webhook/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(webhook_id: str, db_session: AsyncSession = Depends(get_session)) -> WebhookResponse:

    result = await db_session.execute(
        select(WebhookRequestModel).where(WebhookRequestModel.id == webhook_id)
    )
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook request not found")
    
    return WebhookResponse(
        request_id=webhook.id,
        status=webhook.status,
        message=webhook.message,
        response=webhook.response,
        callback_url=webhook.callback_url,
        created_at=webhook.created_at
    )


@router.get("/webhooks", response_model=List[WebhookResponse])
async def list_webhooks(skip: int = Query(0, ge=0), 
                        limit: int = Query(10, ge=1, le=100),
                        callback_url: str = Query(None),
                        db_session: AsyncSession = Depends(get_session)) -> List[WebhookResponse]:
    
    query = select(WebhookRequestModel)
    
    if callback_url:
        query = query.where(WebhookRequestModel.callback_url == callback_url)
    
    result = await db_session.execute(
        query
        .offset(skip)
        .limit(limit)
        .order_by(WebhookRequestModel.created_at.desc())
    )
    webhooks = result.scalars().all()
    
    return [
        WebhookResponse(
            request_id=webhook.id,
            status=webhook.status,
            message=webhook.message,
            response=webhook.response,
            callback_url=webhook.callback_url,
            created_at=webhook.created_at
        )
        for webhook in webhooks
    ]


@router.delete("/webhook/{webhook_id}", status_code=204)
async def delete_webhook(webhook_id: str, db_session: AsyncSession = Depends(get_session)) -> None:
    result = await db_session.execute(
        select(WebhookRequestModel).where(WebhookRequestModel.id == webhook_id)
    )
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook request not found")
    
    if webhook.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending webhook requests can be deleted"
        )
    
    await db_session.delete(webhook)
    await db_session.commit()


@router.get("/webhook/{task_id}/status")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    } 