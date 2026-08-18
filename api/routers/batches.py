from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from api import schemas
from api.database import get_db
from api.limiter import limiter
from api.services import batches

router = APIRouter(
    prefix="/batches",
    tags=["Batches"],
)


@router.patch("/{batch_id}")
@limiter.limit("60/minute")
async def update_batch(
    request: Request,
    batch_id: int,
    batch_update: schemas.BatchUpdate,
    db: AsyncSession = Depends(get_db),
):
    batch = await batches.update_batch(
        batch_id,
        batch_update,
        db,
    )

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )

    return batch


@router.delete("/{batch_id}")
@limiter.limit("60/minute")
async def delete_batch(
    request: Request,
    batch_id: int,
    db: AsyncSession = Depends(get_db),
):
    deleted = await batches.delete_batch(
        batch_id,
        db,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )

    return {"message": "Batch deleted successfully"}
