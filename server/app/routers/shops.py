from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.errors import bad_request, not_found
from app.models import Shop
from app.schemas import ShopCreate, ShopOut

router = APIRouter()


@router.get("", response_model=list[ShopOut])
async def list_shops(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Shop).order_by(Shop.name))
    return result.scalars().all()


@router.post("", response_model=ShopOut)
async def create_shop(payload: ShopCreate, session: AsyncSession = Depends(get_session)):
    shop = Shop(name=payload.name)
    session.add(shop)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise bad_request("Shop name must be unique")
    await session.refresh(shop)
    return shop


@router.delete("/{shop_id}")
async def delete_shop(shop_id: int, session: AsyncSession = Depends(get_session)):
    shop = await session.get(Shop, shop_id)
    if not shop:
        raise not_found("Shop")
    await session.delete(shop)
    await session.commit()
    return {"status": "deleted"}
