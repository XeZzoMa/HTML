from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    category = Column(String(100), nullable=False)

    recipe_links = relationship("RecipeIngredient", back_populates="ingredient")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    people_amount = Column(Integer, nullable=False)
    steps = Column(JSONB, nullable=False)

    ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeIngredient.sort_order",
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (UniqueConstraint("recipe_id", "ingredient_id", name="uq_recipe_ing"),)

    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True)
    amount = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), nullable=False)
    sort_order = Column(Integer, nullable=False)

    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_links")


class MealType(Base):
    __tablename__ = "meal_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    meal_type_id = Column(Integer, ForeignKey("meal_types.id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    people_count = Column(Integer, nullable=False)

    meal_type = relationship("MealType")
    recipe = relationship("Recipe")


class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)


class CustomShoppingItem(Base):
    __tablename__ = "custom_shopping_items"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=True)
    unit = Column(String(50), nullable=True)
    checked = Column(Boolean, nullable=False, default=False)


class ShoppingItemState(Base):
    __tablename__ = "shopping_item_states"

    id = Column(Integer, primary_key=True)
    item_key = Column(String(200), unique=True, nullable=False)
    checked = Column(Boolean, nullable=False, default=False)


class ShopItemOrder(Base):
    __tablename__ = "shop_item_orders"
    __table_args__ = (UniqueConstraint("shop_id", "item_key", name="uq_shop_item"),)

    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    item_key = Column(String(200), nullable=False)
    sort_order = Column(Integer, nullable=False)

    shop = relationship("Shop")
