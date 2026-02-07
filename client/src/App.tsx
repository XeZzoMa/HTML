import { useState } from "react";
import IngredientsPage from "./pages/IngredientsPage";
import RecipesPage from "./pages/RecipesPage";
import PlannerPage from "./pages/PlannerPage";
import ShoppingListPage from "./pages/ShoppingListPage";
import MealTypesPage from "./pages/MealTypesPage";

const tabs = [
  { id: "ingredients", label: "Ingredients" },
  { id: "recipes", label: "Recipes" },
  { id: "meal-types", label: "Meal Types" },
  { id: "planner", label: "Planner" },
  { id: "shopping", label: "Shopping List" },
];

export default function App() {
  const [active, setActive] = useState("ingredients");

  return (
    <div className="min-h-screen">
      <header className="bg-white shadow-sm">
        <div className="mx-auto max-w-6xl px-4 py-6">
          <h1 className="text-2xl font-semibold">Meal Planner + Shopping List</h1>
          <p className="text-slate-500">Plan meals, scale recipes, and build smarter shopping lists.</p>
        </div>
      </header>
      <nav className="border-b bg-white">
        <div className="mx-auto flex max-w-6xl gap-2 px-4 py-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActive(tab.id)}
              className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                active === tab.id
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>
      <main className="mx-auto max-w-6xl px-4 py-8">
        {active === "ingredients" && <IngredientsPage />}
        {active === "recipes" && <RecipesPage />}
        {active === "meal-types" && <MealTypesPage />}
        {active === "planner" && <PlannerPage />}
        {active === "shopping" && <ShoppingListPage />}
      </main>
    </div>
  );
}
