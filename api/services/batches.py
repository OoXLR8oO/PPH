from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api import models, schemas


async def update_batch(
    batch_id: int,
    batch_update: schemas.BatchUpdate,
    db: AsyncSession,
):
    stmt = select(models.Batch).where(models.Batch.id == batch_id)

    result = await db.execute(stmt)
    batch = result.scalar_one_or_none()

    if not batch:
        return None

    batch.dropbox_link = (
        str(batch_update.dropbox_link) if batch_update.dropbox_link else None
    )

    await db.commit()
    await db.refresh(batch)

    return batch


async def delete_batch(
    batch_id: int,
    db: AsyncSession,
    commit: bool = True,
):
    stmt = select(models.Batch).where(models.Batch.id == batch_id)

    result = await db.execute(stmt)
    batch = result.scalar_one_or_none()

    if not batch:
        return False

    await db.delete(batch)

    if commit:
        await db.commit()

    return True
