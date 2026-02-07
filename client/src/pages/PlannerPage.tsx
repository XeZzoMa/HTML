import { useEffect, useMemo, useState } from "react";
import { apiRequest } from "../api/client";

type MealType = { id: number; name: string };

type Recipe = { id: number; name: string; peopleAmount: number };

type MealPlan = {
  id: number;
  date: string;
  mealTypeId: number;
  recipeId: number;
  peopleCount: number;
  meal_type_name: string;
  recipe_name: string;
};

function formatDate(value: Date) {
  return value.toISOString().split("T")[0];
}

export default function PlannerPage() {
  const [mealTypes, setMealTypes] = useState<MealType[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [plans, setPlans] = useState<MealPlan[]>([]);

  const weekDates = useMemo(() => {
    const start = new Date();
    return Array.from({ length: 7 }).map((_, idx) => {
      const date = new Date(start);
      date.setDate(start.getDate() + idx);
      return date;
    });
  }, []);

  async function loadData() {
    const [mealTypesData, recipesData, plansData] = await Promise.all([
      apiRequest<MealType[]>("/meal-types"),
      apiRequest<Recipe[]>("/recipes"),
      apiRequest<MealPlan[]>("/meal-plans"),
    ]);
    setMealTypes(mealTypesData);
    setRecipes(recipesData);
    setPlans(plansData);
  }

  useEffect(() => {
    loadData();
  }, []);

  async function createPlan(date: string, mealTypeId: number, recipeId: number) {
    const recipe = recipes.find((item) => item.id === recipeId);
    const peopleCount = recipe?.peopleAmount ?? 1;
    await apiRequest("/meal-plans", {
      method: "POST",
      body: JSON.stringify({ date, mealTypeId, recipeId, peopleCount }),
    });
    await loadData();
  }

  async function updatePeopleCount(planId: number, peopleCount: number) {
    await apiRequest(`/meal-plans/${planId}`, {
      method: "PUT",
      body: JSON.stringify({ peopleCount }),
    });
    await loadData();
  }

  async function removePlan(planId: number) {
    await apiRequest(`/meal-plans/${planId}`, { method: "DELETE" });
    await loadData();
  }

  function getPlan(date: string, mealTypeId: number) {
    return plans.find((plan) => plan.date === date && plan.mealTypeId === mealTypeId);
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">Week planner</h2>
        <p className="text-sm text-slate-500">Plan meals for the next 7 days.</p>
        <div className="mt-4 overflow-auto">
          <div className="min-w-[900px]">
            <div className="grid grid-cols-[200px_repeat(7,minmax(0,1fr))] gap-2 text-sm font-medium">
              <div></div>
              {weekDates.map((day) => (
                <div key={day.toDateString()} className="rounded-lg bg-slate-100 p-2 text-center">
                  {day.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" })}
                </div>
              ))}
            </div>
            <div className="mt-2 grid gap-2">
              {mealTypes.map((mealType) => (
                <div
                  key={mealType.id}
                  className="grid grid-cols-[200px_repeat(7,minmax(0,1fr))] gap-2"
                >
                  <div className="rounded-lg bg-white p-2 font-medium">{mealType.name}</div>
                  {weekDates.map((day) => {
                    const date = formatDate(day);
                    const plan = getPlan(date, mealType.id);
                    return (
                      <div key={`${mealType.id}-${date}`} className="rounded-lg border border-slate-200 p-2">
                        {plan ? (
                          <div className="space-y-2">
                            <div className="text-sm font-medium">{plan.recipe_name}</div>
                            <div className="flex items-center gap-2 text-xs">
                              <label className="text-slate-500">People</label>
                              <input
                                type="number"
                                min={1}
                                value={plan.peopleCount}
                                onChange={(event) => updatePeopleCount(plan.id, Number(event.target.value))}
                                className="w-16 rounded border border-slate-200 px-2 py-1"
                              />
                            </div>
                            <button
                              className="text-xs text-red-600"
                              onClick={() => removePlan(plan.id)}
                            >
                              Remove
                            </button>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <select
                              className="w-full rounded border border-slate-200 px-2 py-1 text-xs"
                              defaultValue=""
                              onChange={(event) => {
                                const recipeId = Number(event.target.value);
                                if (recipeId) {
                                  createPlan(date, mealType.id, recipeId);
                                }
                              }}
                            >
                              <option value="">Add recipe...</option>
                              {recipes.map((recipe) => (
                                <option key={recipe.id} value={recipe.id}>
                                  {recipe.name}
                                </option>
                              ))}
                            </select>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
