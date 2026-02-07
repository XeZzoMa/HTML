from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.errors import bad_request, not_found
from app.models import Ingredient
from app.schemas import IngredientCreate, IngredientOut, IngredientUpdate

router = APIRouter()


@router.get("", response_model=list[IngredientOut])
async def list_ingredients(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Ingredient).order_by(Ingredient.name))
    return result.scalars().all()


@router.post("", response_model=IngredientOut)
async def create_ingredient(payload: IngredientCreate, session: AsyncSession = Depends(get_session)):
    ingredient = Ingredient(name=payload.name, category=payload.category)
    session.add(ingredient)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise bad_request("Ingredient name must be unique")
    await session.refresh(ingredient)
    return ingredient


@router.put("/{ingredient_id}", response_model=IngredientOut)
async def update_ingredient(
    ingredient_id: int, payload: IngredientUpdate, session: AsyncSession = Depends(get_session)
):
    ingredient = await session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise not_found("Ingredient")
    ingredient.name = payload.name
    ingredient.category = payload.category
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise bad_request("Ingredient name must be unique")
    await session.refresh(ingredient)
    return ingredient


@router.delete("/{ingredient_id}")
async def delete_ingredient(ingredient_id: int, session: AsyncSession = Depends(get_session)):
    ingredient = await session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise not_found("Ingredient")
    await session.delete(ingredient)
    await session.commit()
    return {"status": "deleted"}
