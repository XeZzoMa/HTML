from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.errors import bad_request, not_found
from app.models import (
    CustomShoppingItem,
    MealPlan,
    Recipe,
    RecipeIngredient,
    ShoppingItemState,
    Shop,
    ShopItemOrder,
)
from app.schemas import (
    CustomItemCreate,
    LearnOrderRequest,
    ShoppingListItem,
    ShoppingListResponse,
    ToggleItemRequest,
)

router = APIRouter()


def _round_amount(value: Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@router.get("", response_model=ShoppingListResponse)
async def get_shopping_list(
    until_date: date | None = Query(default=None, alias="untilDate"),
    shop_id: int | None = Query(default=None, alias="shopId"),
    session: AsyncSession = Depends(get_session),
):
    if shop_id:
        shop = await session.get(Shop, shop_id)
        if not shop:
            raise not_found("Shop")
    last_date_result = await session.execute(select(MealPlan.date).order_by(MealPlan.date.desc()))
    last_date = last_date_result.scalars().first()
    if until_date is None:
        until_date = last_date or date.today()

    plan_result = await session.execute(
        select(MealPlan)
        .where(MealPlan.date <= until_date)
        .options(
            selectinload(MealPlan.recipe)
            .selectinload(Recipe.ingredients)
            .selectinload(RecipeIngredient.ingredient)
        )
    )
    plans = plan_result.scalars().all()

    totals: dict[int, dict] = {}
    for plan in plans:
        recipe = plan.recipe
        if not recipe:
            continue
        scale = Decimal(plan.people_count) / Decimal(recipe.people_amount)
        for link in recipe.ingredients:
            entry = totals.setdefault(
                link.ingredient_id,
                {
                    "name": link.ingredient.name,
                    "category": link.ingredient.category,
                    "quantity": Decimal("0"),
                    "unit": link.unit,
                },
            )
            entry["quantity"] += Decimal(link.amount) * scale

    custom_result = await session.execute(select(CustomShoppingItem).order_by(CustomShoppingItem.id))
    custom_items = custom_result.scalars().all()

    state_result = await session.execute(select(ShoppingItemState))
    states = {state.item_key: state.checked for state in state_result.scalars().all()}

    items: list[ShoppingListItem] = []
    for ingredient_id, data in totals.items():
        item_key = f"ingredient:{ingredient_id}"
        items.append(
            ShoppingListItem(
                item_key=item_key,
                name=data["name"],
                category=data["category"],
                quantity=_round_amount(data["quantity"]),
                unit=data["unit"],
                checked=states.get(item_key, False),
                source="ingredient",
            )
        )

    for custom in custom_items:
        item_key = f"custom:{custom.id}"
        items.append(
            ShoppingListItem(
                item_key=item_key,
                name=custom.name,
                category=custom.category,
                quantity=_round_amount(custom.quantity),
                unit=custom.unit,
                checked=custom.checked,
                source="custom",
            )
        )

    if shop_id:
        order_result = await session.execute(
            select(ShopItemOrder).where(ShopItemOrder.shop_id == shop_id)
        )
        order_map = {row.item_key: row.sort_order for row in order_result.scalars().all()}
    else:
        order_map = {}

    def sort_key(item: ShoppingListItem):
        if item.checked:
            return (2, 0, item.category or "", item.name)
        if item.item_key in order_map:
            return (0, order_map[item.item_key], "", "")
        return (1, 0, item.category or "", item.name)

    items.sort(key=sort_key)

    return ShoppingListResponse(untilDate=until_date, items=items)


@router.post("/custom-item", response_model=ShoppingListItem)
async def add_custom_item(
    payload: CustomItemCreate, session: AsyncSession = Depends(get_session)
):
    item = CustomShoppingItem(
        name=payload.name,
        category=payload.category,
        quantity=payload.quantity,
        unit=payload.unit,
        checked=False,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return ShoppingListItem(
        item_key=f"custom:{item.id}",
        name=item.name,
        category=item.category,
        quantity=_round_amount(item.quantity),
        unit=item.unit,
        checked=item.checked,
        source="custom",
    )


@router.post("/toggle")
async def toggle_item(payload: ToggleItemRequest, session: AsyncSession = Depends(get_session)):
    if payload.item_key.startswith("custom:"):
        item_id = int(payload.item_key.split(":")[1])
        item = await session.get(CustomShoppingItem, item_id)
        if not item:
            raise not_found("Custom item")
        item.checked = payload.checked
        await session.commit()
        return {"status": "updated"}
    if not payload.item_key.startswith("ingredient:"):
        raise bad_request("Invalid item_key")
    state = await session.execute(
        select(ShoppingItemState).where(ShoppingItemState.item_key == payload.item_key)
    )
    state_row = state.scalars().first()
    if state_row:
        state_row.checked = payload.checked
    else:
        session.add(ShoppingItemState(item_key=payload.item_key, checked=payload.checked))
    await session.commit()
    return {"status": "updated"}


@router.post("/learn-order")
async def learn_order(payload: LearnOrderRequest, session: AsyncSession = Depends(get_session)):
    shop = await session.get(Shop, payload.shop_id)
    if not shop:
        raise not_found("Shop")
    sequence = payload.item_keys
    if not sequence:
        raise bad_request("itemKeys must not be empty")
    result = await session.execute(
        select(ShopItemOrder).where(ShopItemOrder.shop_id == payload.shop_id)
    )
    existing = result.scalars().all()
    existing_map = {row.item_key: row for row in existing}

    for idx, item_key in enumerate(sequence, start=1):
        if item_key in existing_map:
            existing_map[item_key].sort_order = idx
        else:
            session.add(ShopItemOrder(shop_id=payload.shop_id, item_key=item_key, sort_order=idx))

    remaining = [row for row in existing if row.item_key not in sequence]
    if remaining:
        max_order = len(sequence)
        remaining_sorted = sorted(remaining, key=lambda row: row.sort_order)
        for offset, row in enumerate(remaining_sorted, start=1):
            row.sort_order = max_order + offset

    await session.commit()
    return {"status": "learned"}
