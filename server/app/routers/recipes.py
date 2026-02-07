from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.errors import bad_request, not_found
from app.models import Ingredient, Recipe, RecipeIngredient
from app.schemas import RecipeCreate, RecipeOut, RecipeUpdate

router = APIRouter()


def _recipe_to_out(recipe: Recipe) -> RecipeOut:
    return RecipeOut(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        peopleAmount=recipe.people_amount,
        steps=recipe.steps,
        ingredients=[
            {
                "ingredient_id": link.ingredient_id,
                "amount": link.amount,
                "unit": link.unit,
                "sort_order": link.sort_order,
                "ingredient_name": link.ingredient.name,
                "ingredient_category": link.ingredient.category,
            }
            for link in recipe.ingredients
        ],
    )


@router.get("", response_model=list[RecipeOut])
async def list_recipes(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Recipe)
        .options(selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient))
        .order_by(Recipe.name)
    )
    recipes = result.scalars().unique().all()
    return [_recipe_to_out(recipe) for recipe in recipes]


@router.post("", response_model=RecipeOut)
async def create_recipe(payload: RecipeCreate, session: AsyncSession = Depends(get_session)):
    if len(payload.ingredients) > 10:
        raise bad_request("Recipes can have at most 10 ingredients")
    ingredient_ids = [item.ingredient_id for item in payload.ingredients]
    result = await session.execute(select(Ingredient).where(Ingredient.id.in_(ingredient_ids)))
    ingredients = {item.id for item in result.scalars().all()}
    if len(ingredients) != len(set(ingredient_ids)):
        raise bad_request("One or more ingredients do not exist")

    recipe = Recipe(
        name=payload.name,
        description=payload.description,
        people_amount=payload.people_amount,
        steps=payload.steps,
    )
    for item in payload.ingredients:
        recipe.ingredients.append(
            RecipeIngredient(
                ingredient_id=item.ingredient_id,
                amount=item.amount,
                unit=item.unit,
                sort_order=item.sort_order,
            )
        )
    session.add(recipe)
    await session.commit()
    await session.refresh(recipe)
    await session.refresh(recipe, attribute_names=["ingredients"])
    return await get_recipe(recipe.id, session)


@router.get("/{recipe_id}", response_model=RecipeOut)
async def get_recipe(recipe_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Recipe)
        .where(Recipe.id == recipe_id)
        .options(selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient))
    )
    recipe = result.scalars().first()
    if not recipe:
        raise not_found("Recipe")
    return _recipe_to_out(recipe)


@router.put("/{recipe_id}", response_model=RecipeOut)
async def update_recipe(
    recipe_id: int, payload: RecipeUpdate, session: AsyncSession = Depends(get_session)
):
    if len(payload.ingredients) > 10:
        raise bad_request("Recipes can have at most 10 ingredients")
    recipe = await session.get(Recipe, recipe_id)
    if not recipe:
        raise not_found("Recipe")
    ingredient_ids = [item.ingredient_id for item in payload.ingredients]
    result = await session.execute(select(Ingredient).where(Ingredient.id.in_(ingredient_ids)))
    ingredients = {item.id for item in result.scalars().all()}
    if len(ingredients) != len(set(ingredient_ids)):
        raise bad_request("One or more ingredients do not exist")

    recipe.name = payload.name
    recipe.description = payload.description
    recipe.people_amount = payload.people_amount
    recipe.steps = payload.steps

    recipe.ingredients = []
    for item in payload.ingredients:
        recipe.ingredients.append(
            RecipeIngredient(
                ingredient_id=item.ingredient_id,
                amount=item.amount,
                unit=item.unit,
                sort_order=item.sort_order,
            )
        )
    await session.commit()
    return await get_recipe(recipe_id, session)


@router.delete("/{recipe_id}")
async def delete_recipe(recipe_id: int, session: AsyncSession = Depends(get_session)):
    recipe = await session.get(Recipe, recipe_id)
    if not recipe:
        raise not_found("Recipe")
    await session.delete(recipe)
    await session.commit()
    return {"status": "deleted"}
