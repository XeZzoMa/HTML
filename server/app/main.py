from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import HTTPException

from app.config import settings
from app.routers import (
    ingredients,
    recipes,
    meal_types,
    meal_plans,
    shopping_list,
    shops,
)

app = FastAPI(title="Meal Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content=detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error", "details": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "details": str(exc)},
    )


app.include_router(ingredients.router, prefix="/ingredients", tags=["ingredients"])
app.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
app.include_router(meal_types.router, prefix="/meal-types", tags=["meal-types"])
app.include_router(meal_plans.router, prefix="/meal-plans", tags=["meal-plans"])
app.include_router(shops.router, prefix="/shops", tags=["shops"])
app.include_router(shopping_list.router, prefix="/shopping-list", tags=["shopping-list"])
