from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    message: str
    details: Optional[dict] = None


class IngredientBase(BaseModel):
    name: str
    category: str


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(IngredientBase):
    pass


class IngredientOut(IngredientBase):
    id: int

    class Config:
        from_attributes = True


class RecipeIngredientIn(BaseModel):
    ingredient_id: int
    amount: Decimal
    unit: str
    sort_order: int


class RecipeIngredientOut(BaseModel):
    ingredient_id: int
    amount: Decimal
    unit: str
    sort_order: int
    ingredient_name: str
    ingredient_category: str


class RecipeBase(BaseModel):
    name: str
    description: str
    people_amount: int = Field(alias="peopleAmount")
    steps: List[str]


class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredientIn]


class RecipeUpdate(RecipeBase):
    ingredients: List[RecipeIngredientIn]


class RecipeOut(RecipeBase):
    id: int
    ingredients: List[RecipeIngredientOut]

    class Config:
        from_attributes = True
        populate_by_name = True


class MealTypeBase(BaseModel):
    name: str


class MealTypeCreate(MealTypeBase):
    pass


class MealTypeUpdate(MealTypeBase):
    pass


class MealTypeOut(MealTypeBase):
    id: int

    class Config:
        from_attributes = True


class MealPlanBase(BaseModel):
    date: date
    meal_type_id: int = Field(alias="mealTypeId")
    recipe_id: int = Field(alias="recipeId")
    people_count: int = Field(alias="peopleCount")


class MealPlanCreate(MealPlanBase):
    pass


class MealPlanUpdate(BaseModel):
    people_count: int = Field(alias="peopleCount")


class MealPlanOut(MealPlanBase):
    id: int
    meal_type_name: str
    recipe_name: str

    class Config:
        from_attributes = True
        populate_by_name = True


class ShopBase(BaseModel):
    name: str


class ShopCreate(ShopBase):
    pass


class ShopOut(ShopBase):
    id: int

    class Config:
        from_attributes = True


class CustomItemCreate(BaseModel):
    name: str
    category: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None


class ShoppingListItem(BaseModel):
    item_key: str
    name: str
    category: Optional[str]
    quantity: Optional[Decimal]
    unit: Optional[str]
    checked: bool
    source: str


class ShoppingListResponse(BaseModel):
    until_date: date = Field(alias="untilDate")
    items: List[ShoppingListItem]


class ToggleItemRequest(BaseModel):
    item_key: str
    checked: bool


class LearnOrderRequest(BaseModel):
    shop_id: int = Field(alias="shopId")
    item_keys: List[str] = Field(alias="itemKeys")


class ShoppingListQuery(BaseModel):
    until_date: Optional[date] = Field(default=None, alias="untilDate")
    shop_id: Optional[int] = Field(default=None, alias="shopId")
