"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
Down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("people_amount", sa.Integer(), nullable=False),
        sa.Column("steps", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    )
    op.create_table(
        "meal_types",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "shops",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "custom_shopping_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("checked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_table(
        "shopping_item_states",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("item_key", sa.String(length=200), nullable=False),
        sa.Column("checked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.UniqueConstraint("item_key"),
    )
    op.create_table(
        "recipe_ingredients",
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["ingredient_id"], ["ingredients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("recipe_id", "ingredient_id"),
        sa.UniqueConstraint("recipe_id", "ingredient_id", name="uq_recipe_ing"),
    )
    op.create_table(
        "meal_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("meal_type_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("people_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["meal_type_id"], ["meal_types.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "shop_item_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("shop_id", sa.Integer(), nullable=False),
        sa.Column("item_key", sa.String(length=200), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("shop_id", "item_key", name="uq_shop_item"),
    )


def downgrade() -> None:
    op.drop_table("shop_item_orders")
    op.drop_table("meal_plans")
    op.drop_table("recipe_ingredients")
    op.drop_table("shopping_item_states")
    op.drop_table("custom_shopping_items")
    op.drop_table("shops")
    op.drop_table("meal_types")
    op.drop_table("recipes")
    op.drop_table("ingredients")
