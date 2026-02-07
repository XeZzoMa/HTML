from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.errors import bad_request, not_found
from app.models import MealType
from app.schemas import MealTypeCreate, MealTypeOut, MealTypeUpdate

router = APIRouter()


@router.get("", response_model=list[MealTypeOut])
async def list_meal_types(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(MealType).order_by(MealType.name))
    return result.scalars().all()


@router.post("", response_model=MealTypeOut)
async def create_meal_type(payload: MealTypeCreate, session: AsyncSession = Depends(get_session)):
    meal_type = MealType(name=payload.name)
    session.add(meal_type)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise bad_request("Meal type name must be unique")
    await session.refresh(meal_type)
    return meal_type


@router.put("/{meal_type_id}", response_model=MealTypeOut)
async def update_meal_type(
    meal_type_id: int, payload: MealTypeUpdate, session: AsyncSession = Depends(get_session)
):
    meal_type = await session.get(MealType, meal_type_id)
    if not meal_type:
        raise not_found("Meal type")
    meal_type.name = payload.name
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise bad_request("Meal type name must be unique")
    await session.refresh(meal_type)
    return meal_type


@router.delete("/{meal_type_id}")
async def delete_meal_type(meal_type_id: int, session: AsyncSession = Depends(get_session)):
    meal_type = await session.get(MealType, meal_type_id)
    if not meal_type:
        raise not_found("Meal type")
    await session.delete(meal_type)
    await session.commit()
    return {"status": "deleted"}
