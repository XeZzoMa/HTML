import { useEffect, useMemo, useState } from "react";
import { apiRequest } from "../api/client";

type Ingredient = {
  id: number;
  name: string;
  category: string;
};

type RecipeIngredient = {
  ingredient_id: number;
  amount: string;
  unit: string;
  sort_order: number;
  ingredient_name?: string;
  ingredient_category?: string;
};

type Recipe = {
  id: number;
  name: string;
  description: string;
  peopleAmount: number;
  steps: string[];
  ingredients: RecipeIngredient[];
};

export default function RecipesPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [editing, setEditing] = useState<Recipe | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [peopleAmount, setPeopleAmount] = useState(2);
  const [steps, setSteps] = useState<string[]>([""]);
  const [recipeIngredients, setRecipeIngredients] = useState<RecipeIngredient[]>([]);
  const [error, setError] = useState<string | null>(null);

  const ingredientOptions = useMemo(
    () => ingredients.map((item) => ({ value: item.id, label: `${item.name} (${item.category})` })),
    [ingredients]
  );

  async function loadData() {
    const [recipesData, ingredientsData] = await Promise.all([
      apiRequest<Recipe[]>("/recipes"),
      apiRequest<Ingredient[]>("/ingredients"),
    ]);
    setRecipes(recipesData);
    setIngredients(ingredientsData);
  }

  useEffect(() => {
    loadData().catch((err) => setError(err.message || "Failed to load"));
  }, []);

  function resetForm() {
    setEditing(null);
    setName("");
    setDescription("");
    setPeopleAmount(2);
    setSteps([""]);
    setRecipeIngredients([]);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (recipeIngredients.length > 10) {
      setError("Recipes can have at most 10 ingredients.");
      return;
    }
    const payload = {
      name,
      description,
      peopleAmount,
      steps: steps.filter((step) => step.trim().length > 0),
      ingredients: recipeIngredients.map((item, index) => ({
        ingredient_id: item.ingredient_id,
        amount: parseFloat(item.amount),
        unit: item.unit,
        sort_order: index + 1,
      })),
    };
    try {
      if (editing) {
        await apiRequest(`/recipes/${editing.id}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });
      } else {
        await apiRequest("/recipes", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      resetForm();
      await loadData();
    } catch (err: any) {
      setError(err.message || "Failed to save recipe");
    }
  }

  function startEdit(recipe: Recipe) {
    setEditing(recipe);
    setName(recipe.name);
    setDescription(recipe.description);
    setPeopleAmount(recipe.peopleAmount);
    setSteps(recipe.steps.length ? recipe.steps : [""]);
    setRecipeIngredients(
      recipe.ingredients.map((item) => ({
        ingredient_id: item.ingredient_id,
        amount: String(item.amount),
        unit: item.unit,
        sort_order: item.sort_order,
      }))
    );
  }

  async function deleteRecipe(id: number) {
    await apiRequest(`/recipes/${id}`, { method: "DELETE" });
    await loadData();
  }

  function updateIngredient(index: number, field: keyof RecipeIngredient, value: string | number) {
    setRecipeIngredients((prev) =>
      prev.map((item, idx) => (idx === index ? { ...item, [field]: value } : item))
    );
  }

  function addIngredientRow() {
    if (recipeIngredients.length >= 10) {
      setError("Ingredient limit reached (10)." );
      return;
    }
    setRecipeIngredients((prev) => [
      ...prev,
      { ingredient_id: ingredients[0]?.id || 0, amount: "", unit: "", sort_order: prev.length + 1 },
    ]);
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">Create or edit recipe</h2>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div className="grid gap-3 md:grid-cols-2">
            <input
              className="rounded-lg border border-slate-200 px-3 py-2"
              placeholder="Recipe name"
              value={name}
              onChange={(event) => setName(event.target.value)}
            />
            <input
              className="rounded-lg border border-slate-200 px-3 py-2"
              placeholder="Base servings"
              type="number"
              min={1}
              value={peopleAmount}
              onChange={(event) => setPeopleAmount(Number(event.target.value))}
            />
          </div>
          <textarea
            className="min-h-[80px] rounded-lg border border-slate-200 px-3 py-2"
            placeholder="Description"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
          />

          <div>
            <h3 className="font-medium">Steps</h3>
            <div className="mt-2 space-y-2">
              {steps.map((step, idx) => (
                <div key={idx} className="flex gap-2">
                  <input
                    className="flex-1 rounded-lg border border-slate-200 px-3 py-2"
                    placeholder={`Step ${idx + 1}`}
                    value={step}
                    onChange={(event) => {
                      const value = event.target.value;
                      setSteps((prev) => prev.map((s, i) => (i === idx ? value : s)));
                    }}
                  />
                  <button
                    type="button"
                    className="rounded-lg border border-slate-200 px-3"
                    onClick={() => setSteps((prev) => prev.filter((_, i) => i !== idx))}
                  >
                    Remove
                  </button>
                </div>
              ))}
              <button
                type="button"
                className="rounded-lg border border-slate-200 px-3 py-1 text-sm"
                onClick={() => setSteps((prev) => [...prev, ""])}
              >
                Add step
              </button>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between">
              <h3 className="font-medium">Ingredients (max 10)</h3>
              <button
                type="button"
                className="rounded-lg border border-slate-200 px-3 py-1 text-sm"
                onClick={addIngredientRow}
              >
                Add ingredient
              </button>
            </div>
            <div className="mt-2 space-y-2">
              {recipeIngredients.map((item, index) => (
                <div key={index} className="grid gap-2 md:grid-cols-4">
                  <select
                    className="rounded-lg border border-slate-200 px-3 py-2"
                    value={item.ingredient_id}
                    onChange={(event) => updateIngredient(index, "ingredient_id", Number(event.target.value))}
                  >
                    {ingredientOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  <input
                    className="rounded-lg border border-slate-200 px-3 py-2"
                    placeholder="Amount"
                    value={item.amount}
                    onChange={(event) => updateIngredient(index, "amount", event.target.value)}
                  />
                  <input
                    className="rounded-lg border border-slate-200 px-3 py-2"
                    placeholder="Unit"
                    value={item.unit}
                    onChange={(event) => updateIngredient(index, "unit", event.target.value)}
                  />
                  <button
                    type="button"
                    className="rounded-lg border border-slate-200 px-3 py-2"
                    onClick={() => setRecipeIngredients((prev) => prev.filter((_, i) => i !== index))}
                  >
                    Remove
                  </button>
                </div>
              ))}
              {recipeIngredients.length === 0 && (
                <p className="text-sm text-slate-500">No ingredients yet.</p>
              )}
            </div>
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <div className="flex gap-2">
            <button className="rounded-lg bg-slate-900 px-4 py-2 text-white" type="submit">
              {editing ? "Update recipe" : "Create recipe"}
            </button>
            <button
              type="button"
              className="rounded-lg border border-slate-200 px-4 py-2"
              onClick={resetForm}
            >
              Clear
            </button>
          </div>
        </form>
      </div>

      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">Recipes</h2>
        <div className="mt-4 space-y-4">
          {recipes.map((recipe) => (
            <div key={recipe.id} className="rounded-xl border border-slate-100 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="text-lg font-semibold">{recipe.name}</h3>
                  <p className="text-sm text-slate-500">Base servings: {recipe.peopleAmount}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    className="rounded-lg border border-slate-200 px-3 py-1 text-sm"
                    onClick={() => startEdit(recipe)}
                  >
                    Edit
                  </button>
                  <button
                    className="rounded-lg border border-red-200 px-3 py-1 text-sm text-red-600"
                    onClick={() => deleteRecipe(recipe.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
              <p className="mt-2 text-sm text-slate-600">{recipe.description}</p>
              <div className="mt-3 text-sm">
                <p className="font-medium">Steps</p>
                <ol className="list-decimal pl-6 text-slate-600">
                  {recipe.steps.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
              <div className="mt-3 text-sm">
                <p className="font-medium">Ingredients</p>
                <ul className="list-disc pl-6 text-slate-600">
                  {recipe.ingredients.map((ing) => (
                    <li key={`${recipe.id}-${ing.ingredient_id}`}>
                      {ing.amount} {ing.unit} {ing.ingredient_name}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
          {recipes.length === 0 && <p className="text-sm text-slate-500">No recipes yet.</p>}
        </div>
      </div>
    </div>
  );
}
