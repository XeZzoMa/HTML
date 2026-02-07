from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db import get_session
from app.errors import bad_request, not_found
from app.models import MealPlan, MealType, Recipe
from app.schemas import MealPlanCreate, MealPlanOut, MealPlanUpdate

router = APIRouter()


@router.get("", response_model=list[MealPlanOut])
async def list_meal_plans(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(MealPlan).options(joinedload(MealPlan.meal_type), joinedload(MealPlan.recipe))
    )
    plans = result.scalars().all()
    return [
        MealPlanOut(
            id=plan.id,
            date=plan.date,
            mealTypeId=plan.meal_type_id,
            recipeId=plan.recipe_id,
            peopleCount=plan.people_count,
            meal_type_name=plan.meal_type.name,
            recipe_name=plan.recipe.name,
        )
        for plan in plans
    ]


@router.post("", response_model=MealPlanOut)
async def create_meal_plan(payload: MealPlanCreate, session: AsyncSession = Depends(get_session)):
    meal_type = await session.get(MealType, payload.meal_type_id)
    recipe = await session.get(Recipe, payload.recipe_id)
    if not meal_type:
        raise not_found("Meal type")
    if not recipe:
        raise not_found("Recipe")
    if payload.people_count <= 0:
        raise bad_request("peopleCount must be positive")
    plan = MealPlan(
        date=payload.date,
        meal_type_id=payload.meal_type_id,
        recipe_id=payload.recipe_id,
        people_count=payload.people_count,
    )
    session.add(plan)
    await session.commit()
    await session.refresh(plan)
    return MealPlanOut(
        id=plan.id,
        date=plan.date,
        mealTypeId=plan.meal_type_id,
        recipeId=plan.recipe_id,
        peopleCount=plan.people_count,
        meal_type_name=meal_type.name,
        recipe_name=recipe.name,
    )


@router.put("/{plan_id}", response_model=MealPlanOut)
async def update_meal_plan(
    plan_id: int, payload: MealPlanUpdate, session: AsyncSession = Depends(get_session)
):
    plan = await session.get(MealPlan, plan_id)
    if not plan:
        raise not_found("Meal plan")
    if payload.people_count <= 0:
        raise bad_request("peopleCount must be positive")
    plan.people_count = payload.people_count
    await session.commit()
    meal_type = await session.get(MealType, plan.meal_type_id)
    recipe = await session.get(Recipe, plan.recipe_id)
    return MealPlanOut(
        id=plan.id,
        date=plan.date,
        mealTypeId=plan.meal_type_id,
        recipeId=plan.recipe_id,
        peopleCount=plan.people_count,
        meal_type_name=meal_type.name if meal_type else "",
        recipe_name=recipe.name if recipe else "",
    )


@router.delete("/{plan_id}")
async def delete_meal_plan(plan_id: int, session: AsyncSession = Depends(get_session)):
    plan = await session.get(MealPlan, plan_id)
    if not plan:
        raise not_found("Meal plan")
    await session.delete(plan)
    await session.commit()
    return {"status": "deleted"}
