import asyncio
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import delete

from app.db import AsyncSessionLocal
from app.models import (
    CustomShoppingItem,
    Ingredient,
    MealPlan,
    MealType,
    Recipe,
    RecipeIngredient,
    Shop,
)


async def seed():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(MealPlan))
        await session.execute(delete(RecipeIngredient))
        await session.execute(delete(Recipe))
        await session.execute(delete(Ingredient))
        await session.execute(delete(MealType))
        await session.execute(delete(CustomShoppingItem))
        await session.execute(delete(Shop))
        await session.commit()

        ingredients = [
            Ingredient(name="Chicken Breast", category="Meat"),
            Ingredient(name="Olive Oil", category="Pantry"),
            Ingredient(name="Garlic", category="Produce"),
            Ingredient(name="Tomato", category="Produce"),
            Ingredient(name="Pasta", category="Pantry"),
            Ingredient(name="Spinach", category="Produce"),
            Ingredient(name="Eggs", category="Dairy"),
            Ingredient(name="Milk", category="Dairy"),
            Ingredient(name="Oats", category="Pantry"),
            Ingredient(name="Banana", category="Produce"),
        ]
        session.add_all(ingredients)

        meal_types = [
            MealType(name="Breakfast"),
            MealType(name="Morning snack"),
            MealType(name="Lunch"),
            MealType(name="Afternoon snack"),
            MealType(name="Dinner"),
            MealType(name="Evening snack"),
        ]
        session.add_all(meal_types)

        recipe1 = Recipe(
            name="Garlic Chicken Pasta",
            description="Quick skillet chicken pasta with garlic and tomatoes.",
            people_amount=2,
            steps=[
                "Season chicken and sear in olive oil.",
                "Add garlic and tomatoes, cook until soft.",
                "Toss with cooked pasta and spinach.",
            ],
        )
        recipe1.ingredients = [
            RecipeIngredient(ingredient=ingredients[0], amount=Decimal("300"), unit="g", sort_order=1),
            RecipeIngredient(ingredient=ingredients[1], amount=Decimal("2"), unit="tbsp", sort_order=2),
            RecipeIngredient(ingredient=ingredients[2], amount=Decimal("3"), unit="cloves", sort_order=3),
            RecipeIngredient(ingredient=ingredients[3], amount=Decimal("2"), unit="pcs", sort_order=4),
            RecipeIngredient(ingredient=ingredients[4], amount=Decimal("200"), unit="g", sort_order=5),
            RecipeIngredient(ingredient=ingredients[5], amount=Decimal("2"), unit="cups", sort_order=6),
        ]

        recipe2 = Recipe(
            name="Banana Oatmeal",
            description="Creamy oats with banana and milk.",
            people_amount=1,
            steps=[
                "Combine oats and milk in a saucepan.",
                "Cook until thick, then top with banana slices.",
            ],
        )
        recipe2.ingredients = [
            RecipeIngredient(ingredient=ingredients[8], amount=Decimal("0.5"), unit="cup", sort_order=1),
            RecipeIngredient(ingredient=ingredients[7], amount=Decimal("1"), unit="cup", sort_order=2),
            RecipeIngredient(ingredient=ingredients[9], amount=Decimal("1"), unit="pc", sort_order=3),
        ]

        recipe3 = Recipe(
            name="Spinach Omelet",
            description="Fluffy eggs with spinach.",
            people_amount=1,
            steps=["Whisk eggs.", "Cook in skillet with spinach."],
        )
        recipe3.ingredients = [
            RecipeIngredient(ingredient=ingredients[6], amount=Decimal("2"), unit="pcs", sort_order=1),
            RecipeIngredient(ingredient=ingredients[5], amount=Decimal("1"), unit="cup", sort_order=2),
        ]

        session.add_all([recipe1, recipe2, recipe3])

        shops = [Shop(name="Fresh Mart"), Shop(name="Neighborhood Market")]
        session.add_all(shops)

        await session.commit()

        today = date.today()
        meal_type_map = {mt.name: mt for mt in meal_types}
        plans = [
            MealPlan(
                date=today,
                meal_type_id=meal_type_map["Dinner"].id,
                recipe_id=recipe1.id,
                people_count=2,
            ),
            MealPlan(
                date=today,
                meal_type_id=meal_type_map["Breakfast"].id,
                recipe_id=recipe2.id,
                people_count=1,
            ),
            MealPlan(
                date=today + timedelta(days=1),
                meal_type_id=meal_type_map["Lunch"].id,
                recipe_id=recipe3.id,
                people_count=1,
            ),
        ]
        session.add_all(plans)

        custom_items = [
            CustomShoppingItem(
                name="Coffee", category="Pantry", quantity=Decimal("1"), unit="bag", checked=False
            ),
            CustomShoppingItem(name="Paper Towels", category="Household", checked=False),
        ]
        session.add_all(custom_items)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
